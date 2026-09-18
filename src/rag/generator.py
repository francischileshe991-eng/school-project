#!/usr/bin/env python3
"""
Generator component for Zedchatbot.
Expert RAG Generator with Multi-Provider support (Ollama, Gemini, OpenAI) and grounded fallback.
"""

from typing import Optional, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.core.logger import logger
from src.configs.settings import settings


def _clean_truncate(text: str, max_len: int = 600) -> str:
    """Truncates text at a clean sentence or word boundary without slicing words mid-token."""
    clean = text.strip()
    if len(clean) <= max_len:
        return clean
    candidate = clean[:max_len]
    for sep in [". ", ".\n", "\n\n", "\n", "? ", "! "]:
        idx = candidate.rfind(sep)
        if idx >= max_len // 2:
            end_offset = 1 if sep.startswith(".") else len(sep)
            return candidate[: idx + end_offset].strip()
    idx = candidate.rfind(" ")
    if idx >= max_len // 2:
        return candidate[:idx].strip() + "..."
    return candidate + "..."


class ZedGenerator:
    """Handles response generation with multi-provider fallback for native multilingual support."""

    def __init__(self):
        self.model_name = settings.MODEL_NAME
        self.provider = getattr(settings, "LLM_PROVIDER", "auto").lower()

        # Expert curated prompt: strict adherence to grounded facts with high-readability formatting
        self.system_prompt = (
            "You are an expert Zambian Community Assistant. "
            "Your task is to answer the user's question using ONLY the provided 'Context'. "
            "1. DO NOT restate or repeat the user's question. "
            "2. Answer immediately and directly with clean, highly readable structure. "
            "3. For step-by-step procedures, guidelines, or applications: "
            "   - Break them down into distinct numbered steps with a blank line between each step (e.g., 'Step 1: ...'). "
            "   - Put each sub-requirement, document, or office on its own separate bullet point line ('- '). "
            "   - NEVER cram multiple steps, offices, or bullet points onto a single line. "
            "4. ALWAYS answer in ENGLISH (this will be translated to the user's selected language later if requested). "
            "5. If the info is not in the context, politely state that you do not have that official record yet."
        )

        self.ollama_llm = self._init_ollama()
        self.gemini_llm = self._init_gemini()
        self.openai_llm = self._init_openai()

    def _init_ollama(self) -> Optional[Any]:
        """Initializes local Ollama model instance."""
        try:
            from langchain_ollama import ChatOllama

            logger.info(f"Generator: Initializing local Ollama with model '{self.model_name}'")
            return ChatOllama(
                model=self.model_name,
                temperature=0.1
            )
        except Exception as e:
            logger.warning(f"Generator: Could not initialize Ollama client: {e}")
            return None

    def _init_gemini(self) -> Optional[Any]:
        """Initializes Google Gemini model instance if API key is provided."""
        api_key = getattr(settings, "GOOGLE_API_KEY", None)
        if not api_key or "your_" in api_key.lower():
            return None
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI

            gemini_model = getattr(settings, "GEMINI_MODEL", "gemini-3.5-flash")
            logger.info(f"Generator: Initializing Google Gemini ({gemini_model})")
            return ChatGoogleGenerativeAI(
                model=gemini_model,
                google_api_key=api_key,
                temperature=0.1
            )
        except Exception as e:
            logger.warning(f"Generator: Failed to initialize Google Gemini: {e}")
            return None

    def _init_openai(self) -> Optional[Any]:
        """Initializes OpenAI model instance if API key is provided."""
        api_key = getattr(settings, "OPENAI_API_KEY", None)
        if not api_key or "your_" in api_key.lower():
            return None
        try:
            from langchain_openai import ChatOpenAI

            openai_model = getattr(settings, "OPENAI_MODEL", "gpt-4o-mini")
            logger.info(f"Generator: Initializing OpenAI ({openai_model})")
            return ChatOpenAI(
                model=openai_model,
                api_key=api_key,
                temperature=0.1
            )
        except Exception as e:
            logger.warning(f"Generator: Failed to initialize OpenAI: {e}")
            return None

    def _invoke_llm(self, llm: Any, query: str, context: str, country: str) -> Optional[str]:
        """Helper to invoke an LLM chain with standard system prompt."""
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.system_prompt),
                ("user", "CONTEXT:\n{context}\n\nQUESTION: {query}\n\nFINAL ANSWER:")
            ])
            chain = prompt | llm | StrOutputParser()
            return chain.invoke({
                "context": context,
                "query": query,
                "country_code": country.upper()
            })
        except Exception as e:
            logger.warning(f"Generator: Provider invocation failed: {e}")
            return None

    def _invoke_gemini(self, query: str, context: str, country: str) -> Optional[str]:
        """Invokes Gemini with multi-model fallback to handle temporary 503 capacity spikes."""
        if self.gemini_llm:
            res = self._invoke_llm(self.gemini_llm, query, context, country)
            if res:
                return res

        api_key = getattr(settings, "GOOGLE_API_KEY", None)
        if not api_key or "your_" in api_key.lower():
            return None

        try:
            from langchain_google_genai import ChatGoogleGenerativeAI

            candidate_models = [
                "gemini-3.5-flash-lite",
                "gemini-3.5-flash",
                "gemini-3.6-flash",
                "gemini-3.7-flash",
            ]
            for model in candidate_models:
                try:
                    llm = ChatGoogleGenerativeAI(
                        model=model,
                        google_api_key=api_key,
                        temperature=0.1,
                    )
                    res = self._invoke_llm(llm, query, context, country)
                    if res:
                        logger.info(f"Generator: Gemini fallback succeeded with model {model}")
                        return res
                except Exception as e:
                    logger.debug(f"Generator: Gemini model {model} attempt failed: {e}")
                    continue
        except Exception as e:
            logger.warning(f"Generator: Gemini fallback initialization failed: {e}")

        return None

    def generate(self, query: str, context: str, country: str, language: str) -> str:
        """Generates a response based on query and retrieved context using provider cascade."""
        if not context or "No specific documents found" in context:
            return "I'm sorry, I don't have that specific official record in my database yet."

        # 1. Direct provider selection if explicitly configured
        if self.provider == "gemini":
            res = self._invoke_gemini(query, context, country)
            if res:
                return res
            # Fallback cascade if Gemini encounters cloud error
            if self.ollama_llm:
                logger.info("Generator: Gemini cloud unavailable, falling back to local Ollama...")
                res = self._invoke_llm(self.ollama_llm, query, context, country)
                if res:
                    return res
            if self.openai_llm:
                logger.info("Generator: Falling back to OpenAI...")
                res = self._invoke_llm(self.openai_llm, query, context, country)
                if res:
                    return res

        if self.provider == "openai" and self.openai_llm:
            res = self._invoke_llm(self.openai_llm, query, context, country)
            if res:
                return res

        if self.provider == "ollama" and self.ollama_llm:
            res = self._invoke_llm(self.ollama_llm, query, context, country)
            if res:
                return res

        # 2. 'Auto' cascade: Gemini (Primary Cloud) -> Ollama (Edge Local) -> OpenAI -> Context Excerpt
        if self.provider == "auto":
            # Attempt 1: Google Gemini (Primary high-speed cloud engine)
            logger.info("Generator: Attempting Google Gemini generation...")
            res = self._invoke_gemini(query, context, country)
            if res:
                return res

            # Attempt 2: Local Ollama (Edge offline fallback)
            if self.ollama_llm:
                logger.info("Generator: Cascading to local Ollama generation...")
                res = self._invoke_llm(self.ollama_llm, query, context, country)
                if res:
                    return res

            # Attempt 3: OpenAI
            if self.openai_llm:
                logger.info("Generator: Cascading to OpenAI generation...")
                res = self._invoke_llm(self.openai_llm, query, context, country)
                if res:
                    return res

        # 3. Grounded Fallback if no LLM was able to produce an answer
        if context:
            logger.info("Generator: Providing grounded context fallback from official records.")
            return f"According to official public records:\n\n{_clean_truncate(context, 600)}"

        return "I'm sorry, my AI brain is currently offline and no records were found."
