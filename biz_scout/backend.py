import logging
from collections.abc import Iterator

import microcore as mc
from microcore.ai_func import ai_func, ToolSet

@ai_func()
def index(company_name: str) -> Iterator[str]:
    logging.info(f"Indexing company: {company_name}")
    yield "\nIndexing company: {company_name}...  \n"
    mc.texts.save("companies", "company_name")
    yield "\nDone"

@ai_func()
def answer_question(company_name: str, question: str) -> Iterator[str]:
    """
    Answer any question about the target company.
    """
    logging.info(f"Answering question about: {company_name}... Question: {question}")
    yield "\nHere is your answer"

def process_user_request(history: list[mc.Msg]) -> Iterator[str]:
    tools = ToolSet([index, answer_question])
    sys_msg = mc.tpl(
        "system_prompt.jinja2",
        tools = tools
    ).as_system
    logging.info(f"Received question: {history[-1].content}")

    output = ""
    def capture_all(chunk):
        nonlocal output
        output += chunk
    conversation_gen = mc.llm_stream([sys_msg, *history], callback=capture_all)
    first_chunk = next(conversation_gen)
    if first_chunk == ">>>":
        yield from conversation_gen
    else:
        for chunk in conversation_gen: pass
        cmd, args, kwargs = tools.extract_tool_params(output)
        mcd_gen = tools.call(cmd, *args, **kwargs)
        yield from mcd_gen
    logging.info(f"Answer: {output}")
