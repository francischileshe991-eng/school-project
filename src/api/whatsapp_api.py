#!/usr/bin/env python3
"""
WhatsApp Integration for Zedchatbot using Twilio.
Bridges the RAG pipeline to the WhatsApp messaging interface.
Logs interactions into the evaluation database.
"""

import asyncio
import time
from fastapi import APIRouter, Form, Response
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from src.core.database import db
from src.core.logger import logger
from src.configs.settings import settings
from src.multilingual.language_detector import detect_language

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



def process_and_reply(body: str, from_number: str, country: str):
    start_time = time.perf_counter()
    user_lang = detect_language(body)

    try:
        from src.rag.pipeline import generate_reply

        answer, sources = generate_reply(body, country)
        elapsed_ms = int((time.perf_counter() - start_time) * 1000)

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

        if len(answer) > MAX_RESPONSE_LEN:
            answer = answer[:MAX_RESPONSE_LEN] + "\n\n[Message truncated]"
        final_text = f"{answer}\n\n---\nZedChatBot | Community Assistant"
        send_whatsapp_reply(from_number, final_text)

    except Exception as e:
        logger.error(f"WhatsApp Background Error: {e}")
        send_whatsapp_reply(from_number, "Sorry, I hit an error. Please try again.")


@router.post("/whatsapp")
async def whatsapp_webhook(Body: str = Form(...), From: str = Form(...)):
    logger.info(f"WhatsApp: Message received from {From}")
    country = "zm"

    user_lang = detect_language(Body)
    thinking_msg = THINKING_MESSAGES.get(user_lang, THINKING_MESSAGES["en"])
    logger.info(f"WhatsApp: Detected language {user_lang}, sending ack in {user_lang}")

    # Modern, robust async worker execution tracking task lifecycle
    task = asyncio.create_task(
        asyncio.to_thread(process_and_reply, Body, From, country)
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
