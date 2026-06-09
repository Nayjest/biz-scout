from typing import Callable
import logging

import microcore as mc

_llm_func: Callable | None = None


def init_perplexity():
    global _llm_func
    try:
        if not _llm_func:
            logging.info('Initializing perplexity...')
            mc.configure('.env.perplexity')
            _llm_func = mc.env().llm_async_function
    except Exception  as e:
        logging.error(e)
        return


async def perplexity(*args, **kwargs) -> mc.LLMResponse:
    global _llm_func
    try:
        init_perplexity()
        return await _llm_func(*args, **kwargs)
    except Exception as e:
        raise mc.BadAIAnswer(f"Error querying Perplexity: {e}") from e
