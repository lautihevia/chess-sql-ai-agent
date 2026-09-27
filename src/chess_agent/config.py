"""Carga de configuración y secretos desde el entorno (`.env`).

Centraliza el acceso a las variables sensibles (Anthropic, Supabase, LangSmith) para que el
resto del código no lea `os.environ` directamente. Los secretos viven fuera del repo (Principio II
de la constitución): en `.env` durante el desarrollo y en los secrets del entorno al desplegar.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv

# Carga `.env` una sola vez al importar el módulo. `override=False`: las variables ya presentes
# en el entorno (p. ej. secrets de Streamlit Cloud) tienen prioridad sobre el archivo.
load_dotenv(override=False)


class ConfigError(RuntimeError):
    """Falta una variable de entorno obligatoria o tiene un valor inválido."""


def _require(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ConfigError(
            f"Falta la variable de entorno obligatoria '{name}'. "
            "Copiá .env.example a .env y completá los valores."
        )
    return value


def _flag(name: str, default: bool = False) -> bool:
    raw = os.getenv(name, "").strip().lower()
    if not raw:
        return default
    return raw in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    """Configuración inmutable del proyecto, resuelta desde el entorno."""

    # --- Claude API (Anthropic) ---
    anthropic_api_key: str
    anthropic_model: str

    # --- Supabase (Postgres + pgvector) ---
    supabase_db_url: str
    supabase_url: str
    supabase_key: str

    # --- LangSmith (observabilidad) ---
    langsmith_api_key: str
    langsmith_tracing: bool
    langsmith_project: str


def configure_langsmith() -> bool:
    """Activa el trazado en LangSmith exportando las variables que LangChain/LangGraph leen.

    Idempotente. Devuelve `True` si el trazado quedó activo, `False` si está desactivado (por
    falta de API key o de `LANGSMITH_TRACING`). Llamar antes de ejecutar el grafo (Principio IV).
    """
    settings = get_settings()
    if not settings.langsmith_tracing:
        os.environ["LANGSMITH_TRACING"] = "false"
        os.environ["LANGCHAIN_TRACING_V2"] = "false"
        return False

    # LangSmith reconoce las variables LANGSMITH_*; se replican en LANGCHAIN_* por compatibilidad.
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGSMITH_API_KEY"] = settings.langsmith_api_key
    os.environ["LANGCHAIN_API_KEY"] = settings.langsmith_api_key
    os.environ["LANGSMITH_PROJECT"] = settings.langsmith_project
    os.environ["LANGCHAIN_PROJECT"] = settings.langsmith_project
    return True


#lru_cache es un decorador de python que sirve para guardad el resultado de una funciona, y luego la proxima
#llamada lo toma cacheado. Significa Last recently used, el size es para que guarde un solo resultado.
@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Devuelve la configuración validada (cacheada).

    Lanza `ConfigError` si falta algún secreto obligatorio. LangSmith es opcional: si no hay
    API key, se desactiva el trazado en vez de fallar.
    """
    langsmith_api_key = os.getenv("LANGSMITH_API_KEY", "").strip()
    langsmith_tracing = _flag("LANGSMITH_TRACING") and bool(langsmith_api_key)

    return Settings(
        anthropic_api_key=_require("ANTHROPIC_API_KEY"),
        anthropic_model=os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5").strip(),
        supabase_db_url=_require("SUPABASE_DB_URL"),
        supabase_url=_require("SUPABASE_URL"),
        supabase_key=_require("SUPABASE_KEY"),
        langsmith_api_key=langsmith_api_key,
        langsmith_tracing=langsmith_tracing,
        langsmith_project=os.getenv("LANGSMITH_PROJECT", "chess-sql-ai-agent").strip(),
    )
