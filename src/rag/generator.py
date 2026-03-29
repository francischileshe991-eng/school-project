#!/usr/bin/env python3
"""
Generator component for Zedchatbot.
Responsible for generating final responses using LLMs or simulated logic.
"""

from typing import Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.core.logger import logger
from src.configs.settings import settings

class ZedGenerator:
    """Handles response generation for the RAG pipeline."""

    def __init__(self, use_gemini: bool = False):
        self.use_gemini = use_gemini
        self.model_name = "gemini-2.0-flash" # Updated model
        
        # System instructions
        self.system_prompt = (
            "You are a helpful and professional community assistant exclusively for the country of {country_code}. "
            "Your goal is to provide accurate information based ONLY on the provided context. "
            "If the answer is not in the context, politely state that you do not have that information. "
            "CRITICAL REQUIREMENT: You MUST write your final response exactly in the following language code: {language_code}."
        )

        if self.use_gemini and settings.GOOGLE_API_KEY:
            from langchain_google_genai import ChatGoogleGenerativeAI
            
            # Debug: Log key presence (but NOT the key itself)
            logger.info(f"Generator: Initializing Gemini with {self.model_name}. API Key present: {bool(settings.GOOGLE_API_KEY)}")
            
            self.llm = ChatGoogleGenerativeAI(
                model=self.model_name,
                google_api_key=settings.GOOGLE_API_KEY,
                temperature=0.2
            )
        else:
            logger.info("Generator: Operating in SIMULATED mode.")
            self.llm = None

    def generate(self, query: str, context: str, country: str, language: str) -> str:
        """Generates a response based on query and retrieved context."""
        
        if not context:
            return "I'm sorry, I couldn't find any specific information about that in our official records."

        if self.llm:
            try:
                # Real LLM Call using LangChain
                prompt = ChatPromptTemplate.from_messages([
                    ("system", self.system_prompt),
                    ("user", "Context: {context}\n\nQuestion: {query}")
                ])
                chain = prompt | self.llm | StrOutputParser()
                return chain.invoke({
                    "context": context, 
                    "query": query,
                    "country_code": country.upper(),
                    "language_code": language
                })
            except Exception as e:
                logger.error(f"Generator: Gemini call failed: {e}")
                return self._simulated_response(context)
        else:
            return self._simulated_response(context)

    def _simulated_response(self, context: str) -> str:
        """Provides a basic answer by extracting text from the context."""
        # Clean up the context a bit for the mock response
        clean_context = context.replace("ï»¿", "").strip()
        return f"Based on our Zambian records: {clean_context[:500]}..."
