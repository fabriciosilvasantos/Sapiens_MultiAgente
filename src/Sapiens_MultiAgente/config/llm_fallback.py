"""
FallbackLLM — wrapper sobre crewai.LLM com fallback automático para Groq.

Fluxo:
  1. Tenta o provider primário (OpenRouter) até `max_retries` vezes.
  2. Se falhar com erro recuperável (429, 5xx, timeout), aguarda e retenta.
  3. Se todas as tentativas primárias falharem, ativa o Groq como fallback.
  4. Se o Groq também falhar, levanta RuntimeError com diagnóstico.

Uso:
    from .llm_fallback import build_llm
    llm = build_llm(model_cfg, groq_api_key)
"""
import logging
import time
from typing import Any, List, Optional

from crewai import LLM
from pydantic import PrivateAttr

logger = logging.getLogger(__name__)

_RETRYABLE_KEYWORDS = (
    "429", "500", "502", "503", "504",
    "timeout", "rate limit", "rate_limit",
    "overloaded", "service unavailable",
    "bad gateway", "gateway timeout",
    "connection error", "too many requests",
    "context deadline exceeded",
)


def _is_retryable(exc: Exception) -> bool:
    msg = str(exc).lower()
    return any(kw in msg for kw in _RETRYABLE_KEYWORDS)


class FallbackLLM(LLM):
    """
    Subclasse de LLM com retry automático e fallback para Groq.

    Os atributos privados são configurados após a instanciação via
    `configure_fallback()` para contornar a validação Pydantic.
    """

    _fallback: Optional[LLM] = PrivateAttr(default=None)
    _max_retries: int = PrivateAttr(default=2)
    _retry_delay: float = PrivateAttr(default=2.0)

    def configure_fallback(
        self,
        fallback_llm: Optional[LLM],
        max_retries: int = 2,
        retry_delay: float = 2.0,
    ) -> "FallbackLLM":
        """Configura o LLM de fallback e parâmetros de retry."""
        self._fallback = fallback_llm
        self._max_retries = max_retries
        self._retry_delay = retry_delay
        return self

    def call(self, messages: List[dict], **kwargs) -> Any:
        last_exc: Optional[Exception] = None

        # --- Tentativas no provider primário (OpenRouter) ---
        for attempt in range(self._max_retries):
            try:
                return super().call(messages, **kwargs)
            except Exception as exc:
                last_exc = exc
                if _is_retryable(exc):
                    logger.warning(
                        "[FallbackLLM] OpenRouter falhou "
                        "(tentativa %d/%d): %s",
                        attempt + 1, self._max_retries, exc,
                    )
                    if attempt < self._max_retries - 1:
                        time.sleep(self._retry_delay)
                else:
                    logger.warning(
                        "[FallbackLLM] Erro não recuperável no OpenRouter: %s", exc
                    )
                    break

        # --- Fallback: Groq ---
        if self._fallback is not None:
            logger.warning(
                "[FallbackLLM] Ativando Groq como fallback. "
                "Último erro OpenRouter: %s",
                last_exc,
            )
            groq_exc: Optional[Exception] = None
            for attempt in range(self._max_retries):
                try:
                    return self._fallback.call(messages, **kwargs)
                except Exception as exc:
                    groq_exc = exc
                    logger.warning(
                        "[FallbackLLM] Groq falhou (tentativa %d/%d): %s",
                        attempt + 1, self._max_retries, exc,
                    )
                    if attempt < self._max_retries - 1:
                        time.sleep(self._retry_delay)

            raise RuntimeError(
                f"[SAPIENS] OpenRouter e Groq falharam. "
                f"OpenRouter: {last_exc} | Groq: {groq_exc}"
            )

        raise RuntimeError(
            f"[SAPIENS] OpenRouter falhou e nenhum fallback configurado. "
            f"Erro: {last_exc}. "
            f"Configure GROQ_API_KEY no .env para habilitar fallback automático."
        )


def build_llm(
    model_cfg: dict,
    openrouter_api_key: str,
    openrouter_base_url: str,
    groq_api_key: Optional[str] = None,
    max_retries: int = 2,
    retry_delay: float = 2.0,
) -> LLM:
    """
    Constrói um FallbackLLM se GROQ_API_KEY estiver disponível,
    caso contrário retorna um LLM simples.

    Args:
        model_cfg: dict com model_id, temperatura e (opcional) groq_fallback.
        openrouter_api_key: chave da API OpenRouter.
        openrouter_base_url: base URL do OpenRouter.
        groq_api_key: chave da API Groq (None = fallback desabilitado).
        max_retries: tentativas por provider.
        retry_delay: segundos entre tentativas.

    Returns:
        FallbackLLM (com Groq) ou LLM simples.
    """
    primary = FallbackLLM(
        model=model_cfg["model_id"],
        temperature=model_cfg.get("temperatura", 0.7),
        api_key=openrouter_api_key,
        base_url=openrouter_base_url,
    )

    groq_model_id = model_cfg.get("groq_fallback")
    if groq_api_key and groq_model_id:
        groq_llm = LLM(
            model=groq_model_id,
            temperature=model_cfg.get("temperatura", 0.7),
            api_key=groq_api_key,
            base_url="https://api.groq.com/openai/v1",
        )
        primary.configure_fallback(groq_llm, max_retries=max_retries, retry_delay=retry_delay)
        logger.info(
            "[FallbackLLM] %s → fallback: %s",
            model_cfg["model_id"], groq_model_id,
        )
    else:
        primary.configure_fallback(None, max_retries=max_retries, retry_delay=retry_delay)
        if not groq_api_key:
            logger.debug("[FallbackLLM] GROQ_API_KEY não definida — fallback desabilitado.")

    return primary
