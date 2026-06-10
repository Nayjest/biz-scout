"""Streamlit chat UI for BizScout. Launched via ``python -m biz_scout``."""

import os
from collections import deque

import microcore as mc
import streamlit as st

from biz_scout.core import process_user_request

# Keep only the most recent N messages in the conversation sent to the LLM.
MAX_CONVERSATION_MESSAGES = int(os.environ.get("MAX_CONVERSATION_MESSAGES") or 10)

st.set_page_config(page_title="BizScout", page_icon="🔎")

st.title("🔎 BizScout")
st.caption(
    "Ask questions about a target company — answered offline from a local knowledge base."
)

if "messages" not in st.session_state:
    # deque(maxlen=N) auto-drops the oldest message once the cap is reached.
    st.session_state.messages = deque(maxlen=MAX_CONVERSATION_MESSAGES)

for message in st.session_state.messages:
    with st.chat_message(message.role):
        st.markdown(getattr(message, "display", message.content))

if question := st.chat_input("Ask about the company…"):
    st.session_state.messages.append(mc.UserMsg(question))
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        st.write_stream(process_user_request(st.session_state.messages))
