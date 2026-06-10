import logging
import time
import microcore as mc
import httpx


def wait_for_models():
    started = time.monotonic()

    logging.info("Waiting for embedding model warmup....")
    while True:
        try:
            mc.texts.save("embedding_model_test", "ok")
            break
        except httpx.TimeoutException:
            logging.warning("Ollama embedding API not available yet, retrying...")
    embedding_wait = time.monotonic() - started
    logging.info(mc.ui.green("[OK] ") + "Embedding model is available.")

    logging.info("Waiting for LLM warmup....")
    while True:
        try:
            res = mc.llm('Answer with "OK"')
            if "OK" in res.strip().upper():
                break
            logging.error("Wrong response from LLM, expected 'OK', got: %s", res)
        except mc.BadAIAnswer as e:
            logging.warning("LLM not available yet, retrying... (%s)", e)
            continue
    llm_wait = time.monotonic() - started - embedding_wait
    logging.info(mc.ui.green("[OK] ") + "LLM is available.")

    total_wait = time.monotonic() - started
    logging.info(
        "Model warmup wait times — embedding: %.1fs, LLM: %.1fs, total: %.1fs",
        embedding_wait,
        llm_wait,
        total_wait,
    )
