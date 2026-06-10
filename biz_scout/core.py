import os
import logging
import textwrap
from collections.abc import Iterator

import microcore as mc
from microcore.ai_func import ai_func, ToolSet
from microcore.configuration import get_bool_from_env

from .company import normalise_company_name, collection_id
from .data_collector import collect_company_info_perplexity

DOCUMENTS_IN_CONTEXT = int(os.getenv("DOCUMENTS_IN_CONTEXT", 20))
MAX_COMPANIES_IN_PROMPT = int(os.getenv("MAX_COMPANIES_IN_PROMPT", 30))
MAX_DOC_CHARS = int(os.getenv("MAX_DOC_CHARS", 2000))
TOKEN__STREAM_IT_TO_USER = ">>"

def is_indexed(company_name_norm: str) -> bool:
    records = mc.texts.search(
        "companies",
        query=company_name_norm,
        where={"company_name": company_name_norm},
        n_results=1,
    )
    return len(records) > 0


def mark_indexed(company_name_norm: str):
    mc.texts.save("companies", company_name_norm, {"company_name": company_name_norm})


@ai_func()
def index(
    company_name: str,  # Normalised company name using latin characters only, without legal suffixes like "Inc", "Ltd", etc. For example, "microsoft"
) -> Iterator[str]:
    """
    Index the target company by fetching relevant information and storing it in the database.
    (only for companies that are not listed,
    use it when user clearly indicates that he wants to index target company)
    """

    company_name = normalise_company_name(company_name)
    cid = collection_id(company_name)

    yield f"\nCollecting information on company: {company_name}...  \n"
    mc.texts.clear(cid)
    facts: list[tuple[str, str]] = collect_company_info_perplexity(company_name)
    yield f"\nCollected {len(facts)} facts.  \n"

    yield f"\nIndexing facts...  \n"

    facts_and_metadata = [(fact, {"src": src}) for fact, src in facts]
    mc.texts.save_many(cid, facts_and_metadata)
    mark_indexed(company_name)
    yield "\nDone"


def grounding_check(question: str, docs: list[str]) -> bool:
    """Check if the retrieved documents contain the information needed to answer the question."""
    check_prompt = mc.tpl(
        "check_answer_existence.jinja2", question=question, docs=docs
    ).to_llm()
    return "Y" in check_prompt


@ai_func()
def answer_question(
    company_name: str,  # Normalised company name using latin characters only, without legal suffixes like "Inc", "Ltd", etc. For example, "microsoft"
    question: str,
) -> Iterator[str]:
    """
    Answer any question about the target company.
    """
    company_name = normalise_company_name(company_name)
    logging.info(f"Answering question about: {company_name}... Question: {question}")
    if not is_indexed(company_name):
        yield textwrap.dedent(f"""
            Company \"{company_name}\" not found in the database.
            Do you want me to collect the relevant information in the internet
            and build knowledge base?
            """)
        return
    docs = mc.texts.search(
        collection_id(company_name), question, n_results=DOCUMENTS_IN_CONTEXT
    )
    need_grounding_check = get_bool_from_env("RAG_GROUNDING_CHECK", default=False)
    if need_grounding_check and grounding_check(question, docs):
        yield textwrap.dedent("""
            I'm sorry, but I couldn't find the information needed to answer your question
            in the database.  
            """)
    else:
        yield from mc.llm_stream(
            mc.tpl(
                "answer_question.jinja2",
                question=question,
                docs=docs,
                max_doc_chars=MAX_DOC_CHARS,
            )
        )


def process_user_request(history: list[mc.Msg]) -> Iterator[str]:
    """Stream user-facing text and append the assistant turn to *history*:
    .content = raw LLM generation (what the model sees next turn),
    .display = text shown to the user (not a dataclass field, never sent to LLM).
    """
    msg = mc.AssistantMsg()
    msg.display = ""
    for chunk in _process_user_request(history, msg):
        msg.display += chunk
        yield chunk
    msg.content = msg.content.strip() or TOKEN__STREAM_IT_TO_USER + msg.display.strip()
    history.append(msg)


def _process_user_request(history: list[mc.Msg], msg: mc.AssistantMsg) -> Iterator[str]:
    tools = ToolSet([index, answer_question])
    user_question = history[-1].content
    available_companies = mc.texts.search(
        "companies", user_question, n_results=MAX_COMPANIES_IN_PROMPT
    )
    sys_msg = mc.tpl(
        "front_ai_system_prompt.jinja2",
        tools=tools,
        available_companies=available_companies,
        TOKEN__STREAM_IT_TO_USER=TOKEN__STREAM_IT_TO_USER,
        user_question=user_question,
    ).as_system
    logging.info(f"Received question: {history[-1].content}")

    def capture_all(chunk):
        msg.content += chunk

    msgs = []
    for m in history:
        if msgs and msgs[-1].role == m.role:
            msgs[-1] = m
        elif msgs or m.role == mc.Role.USER:
            msgs.append(m)

    conversation_generator = mc.llm_stream([sys_msg, *msgs], callback=capture_all)

    try:
        first_chunk = next(conversation_generator)
    except StopIteration:
        yield "I didn't get a response — please try again."
        return

    if first_chunk and first_chunk.startswith(TOKEN__STREAM_IT_TO_USER):
        # Re-emit the peeked first chunk (minus the marker) so we don't drop it.
        yield first_chunk[len(TOKEN__STREAM_IT_TO_USER):]
        yield from conversation_generator
        logging.info(f"Answer: {msg.content}")
        return

    for _ in conversation_generator:
        pass

    logging.info(f"LLM Response: {msg.content}")
    try:
        name, args, kwargs = tools.extract_tool_params(msg.content)
        yield f" -> **{name}**({', '.join(k+':'+v for k,v in kwargs.items())})  \n  \n"
    except Exception:
        yield "Error: Model generated an invalid tool call. \n \n"
        return
    try:
        tool_call_generator = tools.call(name, args, kwargs)
        yield from tool_call_generator
    except Exception as e:
        yield f"Error calling tool {name}: {e}"
