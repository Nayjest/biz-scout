"""Streamlit chat UI for BizScout. Launched via ``python -m biz_scout``."""

import microcore as mc
import streamlit as st

from biz_scout.backend import answer_question

st.set_page_config(page_title="BizScout", page_icon="🔎")

st.title("🔎 BizScout")
st.caption("Ask questions about a target company — answered offline from a local knowledge base.")

# st.session_state is this project's equivalent of the Telegram bot's `deque`:
# it survives Streamlit's top-to-bottom rerun on every interaction, but is
# scoped to a single browser session rather than shared across all users.
# We store microcore messages directly so this list is the single source of
# truth — it both renders the transcript and is fed to the model for context.
if "messages" not in st.session_state:
    st.session_state.messages = []

# Replay the transcript so far. mc.Role is a str subclass equal to
# "user"/"assistant", so it works directly with st.chat_message.
for message in st.session_state.messages:
    with st.chat_message(message.role):
        st.markdown(message.content)

if question := st.chat_input("Ask about the company…"):
    st.session_state.messages.append(mc.UserMsg(question))
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        # write_stream consumes the generator, renders chunks live, and returns the
        # fully assembled markdown. We pass the whole history so the model has
        # the dialogue context, not just the latest question.
        answer = st.write_stream(answer_question(st.session_state.messages))

    st.session_state.messages.append(mc.AssistantMsg(answer))
