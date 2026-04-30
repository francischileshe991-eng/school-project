#!/usr/bin/env python3
"""
Generator component for Zedchatbot.
Responsible for generating final responses using Local Ollama LLM.
"""

import os
from typing import Optional
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.core.logger import logger
from src.configs.settings import settings

class ZedGenerator:
    """Handles response generation for the RAG pipeline supporting multiple providers."""

    def __init__(self, use_ollama: bool = True):
        self.provider = settings.LLM_PROVIDER.lower()
        self.model_name = settings.MODEL_NAME
        
        self.system_prompt = (
            "You are an expert Zambian Community Assistant. "
            "You will be provided with specific 'Context' from official documents. "
            "Your task: Extract ONLY the information relevant to the user's question. "
            "If the user asks about a specific benefit (like maternity), focus ONLY on that. "
            "IGNORE irrelevant information in the context like fees or registration unless asked. "
            "You MUST answer in a natural, detailed way in the SAME LANGUAGE the user used. "
            "If the information is not in the Context, politely say you don't have those specific records yet."
        )

        try:
            if self.provider == "google":
                api_key = settings.GOOGLE_API_KEY
                if not api_key:
                    raise ValueError("GOOGLE_API_KEY not found in settings")
                
                logger.info(f"Generator: Initializing Google Gemini with {self.model_name}")
                self.llm = ChatGoogleGenerativeAI(
                    model=self.model_name,
                    google_api_key=api_key,
                    temperature=0.2
                )
            else:
                logger.info(f"Generator: Initializing local Ollama with {self.model_name}")
                self.llm = ChatOllama(
                    model=self.model_name,
                    temperature=0.2
                )
        except Exception as e:
            logger.error(f"Generator: Failed to initialize LLM ({self.provider}): {e}")
            self.llm = None

    def generate(self, query: str, context: str, country: str, language: str) -> str:
        """Generates a response based on query and retrieved context."""
        
        # If no context is found, we still want a casual greeting
        safe_context = context if context else "No specific documents found for this query."

        if self.llm:
            try:
                # Real Local LLM Call using LangChain
                prompt = ChatPromptTemplate.from_messages([
                    ("system", self.system_prompt),
                    ("user", "CONTEXT: {context}\n\nQUESTION: {query}\n\nFINAL ANSWER BASED ONLY ON CONTEXT:")
                ])
                chain = prompt | self.llm | StrOutputParser()
                
                # Note: We tell the LLM to stay in English because our 
                # NLLB model is much better at the final translation.
                return chain.invoke({
                    "context": safe_context, 
                    "query": query,
                    "country_code": country.upper()
                })
            except Exception as e:
                logger.error(f"Generator: Ollama call failed: {e}")
                return self._simulated_response(safe_context)
        else:
            return self._simulated_response(safe_context)

    def _simulated_response(self, context: str) -> str:
        """Provides a basic answer or a friendly greeting if context is empty."""
        if not context or "No specific documents found" in context:
            return "Hello! I am here to help you. How can I assist you with information about Zambia or Zimbabwe today?"
            
        # Clean up the context for the mock response
        clean_context = context.replace("ï»¿", "").strip()
        # If we have actual content, return it clearly
        if len(clean_context) > 20:
            return f"According to our Zambian records: {clean_context[:500]}..."
            
        return "I'm sorry, I don't have that specific official record in my database yet."
