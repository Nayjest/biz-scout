import os
import logging

import microcore as mc
from microcore.ui import magenta, bright, normal, reset
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction

from .perplexity_connection import init_perplexity
from .logging_setup import setup_logging
from .wait_for_models import wait_for_models

def bootstrap(dot_env_file: str = ".env", warmup: bool = True):
    setup_logging()
    logging.info(
        f"{magenta} ---===[ {bright}Starting BizScout{normal}... ]===--- {reset}"
    )
    mc.configure(
        DOT_ENV_FILE=dot_env_file,
        LLM_API_TYPE=os.getenv("LLM_API_TYPE", "openai"),
        LLM_API_BASE=os.getenv("LLM_API_BASE", "ollama:11434/api"),
        LLM_API_KEY=os.getenv("LLM_API_KEY", "ollama"),
        MODEL=os.getenv("MODEL", "gemma4:12b"),
        EMBEDDING_DB_FUNCTION=OllamaEmbeddingFunction(
            url=os.getenv("EMBEDDING_API_URL", "http://ollama:11434/api/embeddings"),
            model_name=os.getenv("EMBEDDING_MODEL", "paraphrase-multilingual"),
        ),
        USE_LOGGING=True,
    )
    if warmup:
        wait_for_models()
