import logging
import textwrap
from collections.abc import Iterator

import microcore as mc
from microcore.ai_func import ai_func, ToolSet

from .company import normalise_company_name, collection_id
from .data_collector import collect_company_info_perplexity




@ai_func()
def index(
    company_name: str,  # Normalised company name using latin characters only, without legal suffixes like "Inc", "Ltd", etc. For example, "microsoft"
) -> Iterator[str]:
    """Index the target company by fetching relevant information and storing it in the database."""

    company_name = normalise_company_name(company_name)
    yield f"\nCollecting information on company: {company_name}...  \n"

    facts: list[tuple[str,str]] = collect_company_info_perplexity(company_name)
    yield f"\nCollected {len(facts)} facts.  \n"

    yield f"\nIndexing facts...  \n"
    cid = collection_id(company_name)
    mc.texts.clear(cid)
    mc.texts.save("companies", company_name)
    facts_and_metadata = [(fact, {"src": src}) for fact, src in facts]
    mc.texts.save_many(cid, facts_and_metadata)
    yield "\nDone"

@ai_func()
def answer_question(
    company_name: str,  # Normalised company name using latin characters only, without legal suffixes like "Inc", "Ltd", etc. For example, "microsoft"
    question: str
) -> Iterator[str]:
    """
    Answer any question about the target company.
    """
    company_name = normalise_company_name(company_name)
    logging.info(f"Answering question about: {company_name}... Question: {question}")
    if not mc.texts.find_one("companies", where={"company_name": company_name.lower().strip()}):
        yield textwrap.dedent(
            f"""
            Company \"{company_name}\" not found in the database.
            Do you want me to collect the relevant information in the internet
            and build knowledge base?
            """
        )
        return
    yield "\nHere is your answer:"

def process_user_request(history: list[mc.Msg]) -> Iterator[str]:
    tools = ToolSet([index, answer_question])
    sys_msg = mc.tpl(
        "front_ai_system_prompt.jinja2",
        tools = tools
    ).as_system
    logging.info(f"Received question: {history[-1].content}")

    output = ""
    def capture_all(chunk):
        nonlocal output
        output += chunk
    conversation_gen = mc.llm_stream([sys_msg, *history], callback=capture_all)
    first_chunk = next(conversation_gen)
    if first_chunk == ">>":
        yield from conversation_gen
        logging.info(f"Answer: {output}")
    else:
        for chunk in conversation_gen: pass
        output = output.replace('▁▁"', '"')
        logging.info(f"LLM Response: {output}")
        name, args, kwargs = tools.extract_tool_params(output)
        yield f" -> **{name}**({', '.join(k+':'+v for k,v in kwargs.items())})\n"
        mcd_gen = tools.call(name, args, kwargs)
        yield from mcd_gen

