import os
from typing import Callable
import logging

import microcore as mc
from microcore import ui

_llm_func: Callable | None = None


def init_perplexity():
    """Initialize the connection to Perplexity."""
    global _llm_func
    try:
        if not _llm_func:
            logging.info("Initializing perplexity...")
            mc.configure(
                LLM_API_TYPE=mc.ApiType.OPENAI,
                LLM_API_PLATFORM=mc.ApiPlatform.PERPLEXITY,
                LLM_API_BASE=os.getenv("PERPLEXITY_API_BASE"),
                LLM_API_KEY=os.getenv("PERPLEXITY_API_KEY"),
                MODEL=os.getenv("PERPLEXITY_MODEL"),
                EMBEDDING_DB_TYPE=mc.EmbeddingDbType.NONE,
                USE_LOGGING=False,
            )
            _llm_func = mc.env().llm_async_function
            logging.info(f"[ {ui.green('Done')} ]")
    except Exception as e:
        logging.error(e)
        return


async def perplexity(prompt: str | list | mc.Msg, *args, **kwargs) -> mc.LLMResponse:
    """Query Perplexity."""
    global _llm_func
    try:
        init_perplexity()
        logging.info(f"Querying Perplexity:\n{ui.green(repr(prompt))}")
        result = await _llm_func(prompt, *args, **kwargs)
        logging.info(f"Perplexity response:\n{ui.green(str(result))}")
        return result
    except Exception as e:
        raise mc.BadAIAnswer(f"Error querying Perplexity: {e}") from e
