import streamlit as st
import sys
import os
from pathlib import Path

# Add src directory to path to import from main.py
src_path = Path(__file__).parent / "src"
sys.path.append(str(src_path))

from main import query_agent

with st.sidebar:
    st.write("🔬 RAG Research Assistant")
    st.write("This chatbot uses your research documents to answer questions.")
    "[View the source code](https://github.com/streamlit/llm-examples/blob/main/Chatbot.py)"

st.title("🔬 RAG Research Assistant")
st.caption("🚀 A Streamlit chatbot powered by your research documents")
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Hello! I'm your research assistant. I can help you find information from your research documents. What would you like to know?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    # Add user message to session state
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    # Get response from RAG agent
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            # Show a spinner while processing
            with st.spinner("Searching through research documents..."):
                response = query_agent(prompt)
            
            # Display the response
            if response:
                message_placeholder.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            else:
                error_message = "I couldn't find relevant information in the documents. Please try rephrasing your question."
                message_placeholder.markdown(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})
            
        except Exception as e:
            error_message = f"Sorry, I encountered an error: {str(e)}"
            message_placeholder.markdown(error_message)
            st.session_state.messages.append({"role": "assistant", "content": error_message})