"""Entry point: ``python -m biz_scout`` launches the Streamlit UI."""
import logging
from pathlib import Path

import httpx
import microcore as mc
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction
from streamlit.web import bootstrap
from .logging import setup_logging
from .check_models_startup import check_models_startup

def main() -> None:
    setup_logging()
    logging.info("Starting BizScout...")
    mc.configure(
        DOT_ENV_FILE=".env",
        EMBEDDING_DB_FUNCTION=OllamaEmbeddingFunction(
            url="http://ollama:11434/api/embeddings",
            model_name="paraphrase-multilingual",
        )
    )
    check_models_startup()
    ui = Path(__file__).with_name("ui.py")
    bootstrap.run(str(ui), is_hello=False, args=[], flag_options={})


if __name__ == "__main__":
    main()
