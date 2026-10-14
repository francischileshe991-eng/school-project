#!/usr/bin/env python3
"""
Generator component for Zedchatbot.
Expert RAG Generator with Multi-Provider support (Ollama, Gemini, OpenAI, Groq) and grounded fallback.
"""

import re
from typing import Optional, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.core.logger import logger
from src.configs.settings import settings


REFUSAL_PATTERN = re.compile(
    r"("
    r"do\s+not\s+have|"
    r"don't\s+have|"
    r"no\s+official\s+record|"
    r"not\s+in\s+my\s+database|"
    r"not\s+found\s+in\s+(the\s+)?(provided\s+)?context|"
    r"not\s+mentioned\s+in\s+(the\s+)?(provided\s+)?context|"
    r"does\s+not\s+contain|"
    r"doesn't\s+contain|"
    r"cannot\s+find\s+(any\s+)?information|"
    r"can't\s+find\s+(any\s+)?information|"
    r"no\s+information\s+(is\s+)?provided|"
    r"not\s+specified\s+in\s+the\s+context"
    r")",
    re.IGNORECASE
)


def _is_refusal(text: Optional[str]) -> bool:
    """Detects whether a model response is a refusal/gap assertion rather than a factual answer."""
    if not text:
        return True
    cleaned = text.strip()
    return bool(REFUSAL_PATTERN.search(cleaned)) and len(cleaned) < 400


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
            "1. The user's question may be phrased in English, icibemba, chiNyanja, or chiShona, while the Context is in English. "
            "   Understand the semantic intent of the question across these languages and match it to the provided Context. "
            "2. DO NOT restate or repeat the user's question. "
            "3. Answer immediately and directly with clean, highly readable structure. "
            "4. For step-by-step procedures, guidelines, or applications: "
            "   - Break them down into distinct numbered steps with a blank line between each step (e.g., 'Step 1: ...'). "
            "   - Put each sub-requirement, document, or office on its own separate bullet point line ('- '). "
            "   - NEVER cram multiple steps, offices, or bullet points onto a single line. "
            "5. ALWAYS answer in ENGLISH (this will be translated to the user's selected language later if requested). "
            "6. If the info is truly not in the context, politely state that you do not have that official record yet."
        )


        self.ollama_llm = self._init_ollama()
        self.gemini_llm = self._init_gemini()
        self.openai_llm = self._init_openai()
        self.groq_llm = self._init_groq()

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

            gemini_model = getattr(settings, "GEMINI_MODEL", "gemini-3.8-flash")
            logger.info(f"Generator: Initializing Google Gemini ({gemini_model})")
            return ChatGoogleGenerativeAI(
                model=gemini_model,
                google_api_key=api_key,
                temperature=0.1,
                timeout=10.0,
                max_retries=0,
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
                temperature=0.1,
                timeout=10.0,
                max_retries=0,
            )
        except Exception as e:
            logger.warning(f"Generator: Failed to initialize OpenAI: {e}")
            return None

    def _init_groq(self) -> Optional[Any]:
        """Initializes Groq cloud model instance via OpenAI-compatible API."""
        api_key = getattr(settings, "GROQ_API_KEY", None)
        if not api_key or "your_" in api_key.lower():
            return None
        try:
            from langchain_openai import ChatOpenAI

            groq_model = getattr(settings, "GROQ_MODEL", "llama-3.3-70b-versatile")
            logger.info(f"Generator: Initializing Groq ({groq_model})")
            return ChatOpenAI(
                model=groq_model,
                api_key=api_key,
                base_url="https://api.groq.com/openai/v1",
                temperature=0.1,
                timeout=30.0,
                max_retries=1,
            )
        except Exception as e:
            logger.warning(f"Generator: Failed to initialize Groq: {e}")
            return None

    def _invoke_llm(self, llm: Any, query: str, context: str, country: str, prompt_override: Optional[str] = None) -> Optional[str]:
        """Helper to invoke an LLM chain with standard system prompt or custom override."""
        try:
            sys_prompt = prompt_override or self.system_prompt
            prompt = ChatPromptTemplate.from_messages([
                ("system", sys_prompt),
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

    def _invoke_gemini(self, query: str, context: str, country: str, prompt_override: Optional[str] = None) -> Optional[str]:
        """Invokes Gemini with primary model and immediate fast fallback."""
        if self.gemini_llm:
            res = self._invoke_llm(self.gemini_llm, query, context, country, prompt_override=prompt_override)
            if res:
                return res

        api_key = getattr(settings, "GOOGLE_API_KEY", None)
        if not api_key or "your_" in api_key.lower():
            return None

        try:
            from langchain_google_genai import ChatGoogleGenerativeAI

            configured_model = getattr(settings, "GEMINI_MODEL", "gemini-3.8-flash")
            alt_model = getattr(settings, "GEMINI_FALLBACK_MODEL", "gemini-flash-lite-latest")
            if alt_model == configured_model:
                return None
            try:
                llm = ChatGoogleGenerativeAI(
                    model=alt_model,
                    google_api_key=api_key,
                    temperature=0.1,
                    timeout=10.0,
                    max_retries=0,
                )
                res = self._invoke_llm(llm, query, context, country, prompt_override=prompt_override)
                if res:
                    logger.info(f"Generator: Gemini fallback succeeded with model {alt_model}")
                    return res
            except Exception as e:
                logger.debug(f"Generator: Gemini alternate model {alt_model} failed: {e}")
        except Exception as e:
            logger.warning(f"Generator: Gemini fallback initialization failed: {e}")

        return None

    def _generate_with_cascade(
        self, query: str, context: str, country: str, prompt_override: Optional[str] = None
    ) -> Optional[str]:
        """Runs generation through configured LLM providers in priority order.

        Primary cascade (default / 'gemini' / 'auto'):
            Gemini (primary cloud) -> Groq (secondary cloud) -> Ollama (local edge).

        Explicit single-provider modes ('ollama', 'openai', 'groq') are still honoured.
        """
        # --- Explicit local-only mode: Ollama ---
        if self.provider == "ollama":
            if self.ollama_llm:
                return self._invoke_llm(
                    self.ollama_llm, query, context, country, prompt_override=prompt_override
                )
            return None

        # --- Explicit OpenAI-only mode ---
        if self.provider == "openai":
            if self.openai_llm:
                return self._invoke_llm(
                    self.openai_llm, query, context, country, prompt_override=prompt_override
                )
            return None

        # --- Explicit Groq-primary mode: Groq -> Ollama ---
        if self.provider == "groq":
            if self.groq_llm:
                res = self._invoke_llm(
                    self.groq_llm, query, context, country, prompt_override=prompt_override
                )
                if res:
                    return res
            if self.ollama_llm:
                logger.info("Generator: Groq unavailable, falling back to local Ollama...")
                return self._invoke_llm(
                    self.ollama_llm, query, context, country, prompt_override=prompt_override
                )
            return None

        # --- Primary cascade: Gemini -> Groq -> Ollama ---
        # 1. Gemini (primary cloud)
        res = self._invoke_gemini(query, context, country, prompt_override=prompt_override)
        if res:
            return res

        # 2. Groq (secondary cloud)
        if self.groq_llm:
            logger.info("Generator: Gemini unavailable, falling back to Groq...")
            res = self._invoke_llm(
                self.groq_llm, query, context, country, prompt_override=prompt_override
            )
            if res:
                return res

        # 3. Ollama (local edge fallback)
        if self.ollama_llm:
            logger.info("Generator: Cloud providers unavailable, falling back to local Ollama...")
            res = self._invoke_llm(
                self.ollama_llm, query, context, country, prompt_override=prompt_override
            )
            if res:
                return res

        return None

    def generate(self, query: str, context: str, country: str, language: str) -> str:
        """Generates a response based on query and retrieved context using provider cascade with refusal consistency."""
        has_context = bool(context and context.strip() and "No specific documents found" not in context)
        if not has_context:
            return "I'm sorry, I don't have that specific official record in my database yet."

        # Pass 1: Primary generation attempt
        answer = self._generate_with_cascade(query, context, country)

        # Refusal-consistency check:
        # If retrieval returned relevant context chunks but model answers with refusal phrasing,
        # retry generation once with explicit cross-lingual extraction guidance.
        if answer and _is_refusal(answer):
            logger.warning(
                "Generator: Potential false refusal detected despite available context. "
                "Retrying generation once with explicit cross-lingual guidance..."
            )
            retry_prompt = (
                self.system_prompt
                + "\n\nCRITICAL DIRECTIVE: The retrieved Context contains relevant statutory information. "
                "Even though the user's question may be phrased in a local African language (chiNyanja, icibemba, chiShona) "
                "and the Context is in English, extract the matching factual requirements, steps, or rules. "
                "Do NOT assert that you lack records. Answer directly in English using the facts from the Context."
            )
            retry_answer = self._generate_with_cascade(query, context, country, prompt_override=retry_prompt)
            if retry_answer and not _is_refusal(retry_answer):
                logger.info("Generator: Refusal-consistency retry succeeded in answering user query.")
                return retry_answer

            # If it still refuses after retry, return the grounded official excerpt fallback
            logger.warning("Generator: Model continued refusal after retry. Falling back to grounded context excerpt.")
            return f"According to official public records:\n\n{_clean_truncate(context, 600)}"

        # If primary answer is valid and non-refusal
        if answer:
            return answer

        # Grounded Fallback if LLM provider cascade failed / offline
        logger.info("Generator: Providing grounded context fallback from official records.")
        return f"According to official public records:\n\n{_clean_truncate(context, 600)}"

