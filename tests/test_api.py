import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.core.database import db

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "zedchatbot-api"
    assert data["database"] == "connected"
    assert data["vector_store"] == "ready"


def test_root_endpoint() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome to the Zedchatbot API!" in response.json()["message"]


def test_stats_endpoint() -> None:
    response = client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_interactions" in data
    assert "by_country" in data


def test_chat_validation_invalid_country() -> None:
    response = client.post("/chat", json={"message": "Hello", "country": "zz"})
    assert response.status_code == 422


def test_chat_validation_invalid_language() -> None:
    response = client.post("/chat", json={"message": "Hello", "country": "zm", "language": "klingon"})
    assert response.status_code == 422


def test_chat_validation_message_length() -> None:
    # Empty message should fail
    response = client.post("/chat", json={"message": "", "country": "zm"})
    assert response.status_code == 422

    # Message exceeding 2000 characters should fail
    huge_message = "A" * 2001
    response2 = client.post("/chat", json={"message": huge_message, "country": "zm"})
    assert response2.status_code == 422


def test_feedback_endpoint() -> None:
    # First log a dummy interaction
    interaction_id = db.log_interaction(
        channel="web",
        country="zm",
        user_query="Test query",
        detected_language="en",
        retrieved_sources=["test_doc.txt"],
        response="Test answer",
        response_time_ms=150,
    )
    assert interaction_id is not None

    # Test submitting valid feedback
    payload = {
        "interaction_id": interaction_id,
        "rating": 5,
        "comment": "Very accurate answer!",
    }
    response = client.post("/feedback", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    # Test submitting feedback for nonexistent interaction
    bad_payload = {
        "interaction_id": 999999,
        "rating": 3,
        "comment": "Non-existent",
    }
    bad_response = client.post("/feedback", json=bad_payload)
    assert bad_response.status_code == 404


def test_whatsapp_test_endpoints() -> None:
    # GET should succeed without requiring form data
    get_res = client.get("/whatsapp-test")
    assert get_res.status_code == 200
    assert "Test reply from ZedChatBot" in get_res.text

    # POST should also succeed
    post_res = client.post("/whatsapp-test", data={"Body": "Hello", "From": "+260970000000"})
    assert post_res.status_code == 200
    assert "Test reply from ZedChatBot" in post_res.text


def test_send_whatsapp_reply_safe_without_credentials() -> None:
    from src.api.whatsapp_api import send_whatsapp_reply
    # Should safely return and log without crashing when credentials are missing or None
    send_whatsapp_reply("+260970000000", "Safe test message")


def test_language_detector_no_cjk_artifacts() -> None:
    from src.multilingual.language_detector import KNOWN_NYANJA_PHRASES
    for phrase in KNOWN_NYANJA_PHRASES:
        # Check that no CJK Unicode characters exist
        for char in phrase:
            assert not (0x4E00 <= ord(char) <= 0x9FFF), f"Unexpected CJK character found: {char} in {phrase}"


def test_format_for_whatsapp() -> None:
    from src.api.whatsapp_api import format_for_whatsapp
    raw = (
        "### CDF Guide\n"
        "- **Step 1:** Get forms from council.\n"
        "- **Step 2:** Prepare NRC.\n"
        "Check [Official Portal](https://council.gov.zm)."
    )
    formatted = format_for_whatsapp(raw)
    assert "*CDF Guide*" in formatted
    assert "*Step 1:*" in formatted
    assert "• *Step 1:*" in formatted
    assert "• *Step 2:*" in formatted
    assert "**" not in formatted
    assert "Official Portal (https://council.gov.zm)" in formatted


