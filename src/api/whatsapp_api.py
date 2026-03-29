#!/usr/bin/env python3
"""
WhatsApp Integration for Zedchatbot using Twilio.
Phase 4: Messaging API implementation.
"""

from fastapi import APIRouter, Form, Response
from src.configs.settings import settings
from src.core.logger import logger

router = APIRouter()

@router.post("/whatsapp")
async def whatsapp_webhook(
    Body: str = Form(...), 
    From: str = Form(...)
):
    """
    Webhook for Twilio WhatsApp incoming messages.
    Receives message, processes through RAG, and returns TwiML response.
    """
    logger.info(f"WhatsApp: Received message from {From}: '{Body[:30]}...'")

    try:
        from twilio.twiml.messaging_response import MessagingResponse
        from src.rag.pipeline import generate_reply

        # 1. Process message through our Smart RAG Pipeline
        # Note: 'country' defaults to 'zm' for WhatsApp for now
        answer, sources = generate_reply(
            message=Body,
            country=settings.DEFAULT_COUNTRY
        )

        # 2. Format the response for WhatsApp (Twilio TwiML)
        final_text = answer
        if sources:
            source_names = [str(s).split('\\')[-1].split('/')[-1] for s in sources if s]
            final_text += f"\n\nSources: {', '.join(source_names)}"

        twiml_response = MessagingResponse()
        twiml_response.message(final_text)

        logger.info(f"WhatsApp: Sending reply to {From}")
        
        # Return the XML response required by Twilio
        return Response(
            content=str(twiml_response), 
            media_type="application/xml"
        )

    except Exception as e:
        logger.error(f"WhatsApp: Webhook failed: {e}")
        from twilio.twiml.messaging_response import MessagingResponse

        error_msg = MessagingResponse()
        error_msg.message("I'm sorry, I encountered an error. Please try again later.")
        return Response(
            content=str(error_msg), 
            media_type="application/xml"
        )
