"""Entry point: ``python -m biz_scout`` launches the Streamlit UI."""

import os
import logging
from pathlib import Path

import microcore as mc
from microcore.ui import magenta, bright, normal, reset
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction
from streamlit.web import bootstrap

from .bootstrap.logging import setup_logging
from .bootstrap.wait_for_models import wait_for_models
from .bootstrap.perplexity_connection import init_perplexity


def main() -> None:
    setup_logging()
    logging.info(
        f"{magenta} ---===[ {bright}Starting BizScout{normal}... ]===--- {reset}"
    )
    init_perplexity()
    mc.configure(
        DOT_ENV_FILE=".env",
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
    mc.logging.LoggingConfig.OUTPUT_METHOD = logging.info
    wait_for_models()
    ui = Path(__file__).with_name("ui.py")
    bootstrap.run(str(ui), is_hello=False, args=[], flag_options={})


if __name__ == "__main__":
    main()
