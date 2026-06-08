import logging
from collections.abc import Iterator

import microcore as mc


def answer_question(question: str) -> Iterator[str]:
    logging.info(f"Received question: {question}")
    # yield from mc.llm_stream(question)
    chunks = []
    for chunk in mc.llm_stream(question):
        chunks.append(chunk)
        yield chunk
    logging.info(f"Answer: {''.join(chunks)}")
