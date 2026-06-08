import logging
import microcore as mc
import httpx


def check_models_startup():
    logging.info("Waiting for embedding model warmup....")
    while True:
        try:
            mc.texts.save("embedding_model_test", "ok")
            break
        except httpx.TimeoutException:
            logging.warning("Ollama embedding API not available yet, retrying...")
    logging.info(mc.ui.green("[OK] ") + "Embedding model is available.")

    logging.info("Waiting for LLM warmup....")
    while True:
        try:
            res = mc.llm("Answer with \"OK\"")
            if "OK" in res.strip().upper():
                break
            logging.error("Wrong response from LLM, expected 'OK', got: %s", res)
        except mc.BadAIAnswer as e:
            logging.warning("LLM not available yet, retrying... (%s)", e)
            continue
    logging.info(mc.ui.green("[OK] ") + "LLM is available.")
