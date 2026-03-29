#!/usr/bin/env python3
"""
Test script for the Zedchatbot API endpoints.
Verifies Web Chat and WhatsApp webhook functionality.
"""

import requests
import sys
import time

def test_api_health(base_url):
    print("\n--- Testing API Health ---")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Health test failed: {e}")

def test_web_chat(base_url):
    print("\n--- Testing Web Chat (/chat) ---")
    payload = {
        "message": "How do I register for NHIMA?",
        "country": "zm",
        "language": "en"
    }
    try:
        response = requests.post(f"{base_url}/chat", json=payload)
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Answer: {data.get('answer')[:100]}...")
        print(f"Sources: {data.get('sources')}")
    except Exception as e:
        print(f"Web chat test failed: {e}")

def test_whatsapp_webhook(base_url):
    print("\n--- Testing WhatsApp Webhook (/whatsapp) ---")
    # Simulate a Twilio Form-data post
    payload = {
        "Body": "Kodi NRC ndi chiyani?",
        "From": "whatsapp:+260970000000"
    }
    try:
        response = requests.post(f"{base_url}/whatsapp", data=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Content Type: {response.headers.get('Content-Type')}")
        print(f"TwiML Preview: {response.text[:100]}...")
    except Exception as e:
        print(f"WhatsApp webhook test failed: {e}")

def main():
    BASE_URL = "http://127.0.0.1:8000"
    
    print("Zedchatbot API Testing Utility")
    print(f"Targeting: {BASE_URL}")
    
    test_api_health(BASE_URL)
    test_web_chat(BASE_URL)
    test_whatsapp_webhook(BASE_URL)

if __name__ == "__main__":
    main()
