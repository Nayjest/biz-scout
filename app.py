"""Streamlit chat UI for BizScout.

Run locally:   uv run streamlit run app.py
"""

import streamlit as st

from biz_scout.backend import answer_question

st.set_page_config(page_title="BizScout", page_icon="🔎")

st.title("🔎 BizScout")
st.caption("Ask questions about a target company — answered offline from a local knowledge base.")

# Conversation history persists across reruns in session state.
if "messages" not in st.session_state:
    st.session_state.messages = []

# Replay the transcript so far.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if question := st.chat_input("Ask about the company…"):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        # write_stream consumes the generator, renders chunks live, and returns the
        # fully assembled markdown so we can store it in history.
        answer = st.write_stream(answer_question(question))

    st.session_state.messages.append({"role": "assistant", "content": answer})
