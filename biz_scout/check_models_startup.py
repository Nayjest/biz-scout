import logging
import microcore as mc
import httpx


def check_models_startup():
    logging.info("Checking models startup....")
    while True:
        try:
            mc.texts.save("embedding_model_test", "ok")
        except httpx.TimeoutException:
            logging.warning("Ollama embedding API not available yet, retrying...")
        break
    logging.info(mc.ui.green("[OK] ") + "Embedding model is available.")
    while True:
        res = mc.llm("Answer with \"OK\"")
        if "OK" not in res.strip().upper():
            logging.error("Wrong response from LLM, expected 'OK', got: %s", res)
            continue
        break
    logging.info(mc.ui.green("[OK] ") + "LLM is available.")
