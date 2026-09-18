#!/usr/bin/env python3
"""
WhatsApp Integration for Zedchatbot using Twilio.
Bridges the RAG pipeline to the WhatsApp messaging interface.
Logs interactions into the evaluation database.
"""

import asyncio
import re
import time
from fastapi import APIRouter, Form, Response
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from src.core.database import db
from src.core.logger import logger
from src.configs.settings import settings
from src.multilingual.language_detector import detect_language
from src.rag.pipeline import generate_reply

router = APIRouter()

MAX_RESPONSE_LEN = 3500

# Retain strong references to background reply tasks to prevent garbage collection
_background_tasks: set = set()

THINKING_MESSAGES = {
    "en": "Thank you! I'm thinking about your question and will reply shortly...",
    "bem": "Natotela! Ndetontokania pe lipusho lwenu, nalayasuka mukashita kanoono",
    "ny": "Zikomo! Ndikuganiza za funso lanu ndipo ndiyankha posachedwa...",
    "sn": "Ndatenda! Ndiri kufunga nezvemubvunzo wenyu uye ndichapindura munguva pfupi...",
}


def send_whatsapp_reply(to: str, message: str) -> bool:
    if not (
        settings.TWILIO_ACCOUNT_SID
        and settings.TWILIO_AUTH_TOKEN
        and settings.TWILIO_PHONE_NUMBER
    ):
        logger.warning(
            "WhatsApp: Twilio credentials are not configured. Skipping reply."
        )
        return False

    to_number = to if to.startswith("whatsapp:") else f"whatsapp:{to}"

    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=message,
            from_=f"whatsapp:{settings.TWILIO_PHONE_NUMBER}",
            to=to_number,
        )
        logger.info(f"WhatsApp: Sent response to {to_number}")
        return True
    except Exception as e:
        logger.error(f"WhatsApp: Twilio send error for {to_number}: {e}")
        return False


def format_for_whatsapp(text: str) -> str:
    """Formats markdown response into clean, natural WhatsApp mobile format.
    
    - Replaces Markdown bold (**text**) with WhatsApp bold (*text*).
    - Converts markdown headers (### Header) to clean bold titles (*HEADER*).
    - Replaces hyphens (- item) with clean unicode bullet points (• item).
    - Ensures clean line spacing between numbered steps for high mobile readability.
    """
    if not text:
        return ""

    s = text.replace("\r\n", "\n")

    # 1. Convert markdown headers (### Title) to *TITLE*
    s = re.sub(r"^#{1,4}\s*(.*?)$", r"*\1*", s, flags=re.MULTILINE)

    # 2. Convert markdown bold **text** to whatsapp *text*
    s = re.sub(r"\*\*([^*]+)\*\*", r"*\1*", s)

    # 3. Convert markdown links [Label](url) to "Label (url)"
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", s)

    # 4. Convert bullet markers at line starts to clean bullet dots •
    s = re.sub(r"^(\s*)[-*]\s+", r"\1• ", s, flags=re.MULTILINE)

    # 5. Ensure double line breaks before steps (e.g., "*Step 2:...")
    s = re.sub(r"(?<!\n)\n(\*?Step\s+\d+[:\)])", r"\n\n\1", s, flags=re.IGNORECASE)

    # 6. Collapse excessive consecutive blank lines
    s = re.sub(r"\n{3,}", "\n\n", s)

    return s.strip()


async def process_and_reply(from_number: str, body: str, user_lang: str = "en") -> None:
    try:
        t0 = time.perf_counter()

        # Dynamic country detection from phone prefix (+263 -> zw, +260 -> zm) or message tag
        country = _resolve_whatsapp_country(from_number, body)

        answer, sources = await asyncio.to_thread(
            generate_reply,
            message=body,
            country=country,
            language=user_lang,
        )
        elapsed_ms = (time.perf_counter() - t0) * 1000

        # Log WhatsApp interaction to SQLite database
        db.log_interaction(
            channel="whatsapp",
            country=country,
            user_query=body,
            detected_language=user_lang,
            retrieved_sources=sources,
            response=answer,
            response_time_ms=elapsed_ms,
        )

        formatted_answer = format_for_whatsapp(answer)
        if len(formatted_answer) > MAX_RESPONSE_LEN:
            formatted_answer = formatted_answer[:MAX_RESPONSE_LEN] + "\n\n[Message truncated]"
        final_text = f"{formatted_answer}\n\n---\n*ZedChatBot | Community Assistant*"
        send_whatsapp_reply(from_number, final_text)

    except Exception as e:
        logger.error(f"WhatsApp Background Error: {e}")
        send_whatsapp_reply(from_number, "Sorry, I hit an error. Please try again.")


def _resolve_whatsapp_country(from_number: str, message_body: str) -> str:
    """Intelligently detects country from E.164 phone prefix, message tag, or defaults to zm."""
    clean_body = (message_body or "").strip().lower()
    if clean_body.startswith("!zw") or clean_body.startswith("zw:") or "[zw]" in clean_body:
        return "zw"
    if clean_body.startswith("!zm") or clean_body.startswith("zm:") or "[zm]" in clean_body:
        return "zm"

    clean_from = (from_number or "").strip()
    if "+263" in clean_from or clean_from.startswith("263"):
        return "zw"
    if "+260" in clean_from or clean_from.startswith("260"):
        return "zm"

    return getattr(settings, "DEFAULT_COUNTRY", "zm").lower()


@router.post("/whatsapp")
async def whatsapp_webhook(Body: str = Form(...), From: str = Form(...)):
    logger.info(f"WhatsApp: Message received from {From}")
    country = _resolve_whatsapp_country(From, Body)
    logger.info(f"WhatsApp: Routed to country '{country}' for sender {From}")

    clean_body = Body.strip()
    if clean_body.lower().startswith(("!zw", "!zm")):
        clean_body = clean_body[3:].strip()

    user_lang = detect_language(clean_body)
    thinking_msg = THINKING_MESSAGES.get(user_lang, THINKING_MESSAGES["en"])
    logger.info(f"WhatsApp: Detected language {user_lang}, sending ack in {user_lang}")

    # Modern, robust async worker execution tracking task lifecycle
    task = asyncio.create_task(
        process_and_reply(From, clean_body, user_lang)
    )
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)

    twiml_resp = MessagingResponse()
    twiml_resp.message(thinking_msg)
    return Response(
        content=str(twiml_resp),
        media_type="application/xml",
    )


@router.get("/whatsapp-test")
async def whatsapp_test_get():
    logger.info("WhatsApp Test: GET received — webhook is reachable.")
    twiml_resp = MessagingResponse()
    msg = twiml_resp.message()
    msg.body("Test reply from ZedChatBot — webhook is working!")
    return Response(
        content=str(twiml_resp),
        media_type="application/xml",
    )


@router.post("/whatsapp-test")
async def whatsapp_test_post(Body: str = Form(""), From: str = Form("")):
    logger.info(f"WhatsApp Test: POST received from {From}: {Body[:50]}")
    twiml_resp = MessagingResponse()
    msg = twiml_resp.message()
    msg.body("Test reply from ZedChatBot — webhook is working!")
    return Response(
        content=str(twiml_resp),
        media_type="application/xml",
    )
