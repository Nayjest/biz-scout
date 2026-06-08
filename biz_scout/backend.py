import logging
from collections.abc import Iterator

import microcore as mc

SYS_MSG = mc.SysMsg(
    "You are BizScout. Answer questions about a target company "
    "from the local knowledge base."
)

def index(company_name: str) -> Iterator[str]:
    logging.info(f"Indexing company: {company_name}")
    yield "\nIndexing company: {company_name}...  \n"
    mc.texts.save("companies", "company_name")
    yield "\nDone"


def answer_question(history: list[mc.Msg]) -> Iterator[str]:
    sys_msg = mc.tpl("system_prompt.jinja2").as_system
    logging.info(f"Received question: {history[-1].content}")

    output = ""
    def capture_all(chunk):
        nonlocal output
        output += chunk

    yield from mc.llm_stream([sys_msg, *history], callbacks=capture_all)
    logging.info(f"Answer: {output}")
