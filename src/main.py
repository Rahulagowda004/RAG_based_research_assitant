from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, ToolMessage
from operator import add as add_messages
from langchain_core.tools import tool
from model import llm, embedding_model
from retriever import retriever
from langchain_chroma import Chroma
from langgraph.checkpoint.memory import MemorySaver
import os

load_dotenv()

memory = MemorySaver()

if os.path.exists(r"R:\TAZMIC\artifacts\Vector_databases\biology"):
    vectorstore = Chroma(
        collection_name="biology",
        embedding_function=embedding_model,
        persist_directory=r"R:\TAZMIC\artifacts\Vector_databases\biology",
    )
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 20}
    )
else:
    pass
    retriever = retriever(markdown_path=r"R:\TAZMIC\artifacts\research_papers\biology\content.md",directory=r"artifacts\Vector_databases\biology",collection_name="biology")
    
@tool
def retriever_tool(query: str) -> str:
    """
    This tool searches and returns the information from the document.
    """

    docs = retriever.invoke(query)

    if not docs:
        return "I found no relevant information in the document."
    
    results = []
    for i, doc in enumerate(docs):
        results.append(f"Document {i+1}:\n{doc.page_content}")
    
    return "\n\n".join(results)


tools = [retriever_tool]

llm = llm.bind_tools(tools)

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    
def should_continue(state: AgentState):
    """Check if the last message contains tool calls."""
    result = state['messages'][-1]
    return hasattr(result, 'tool_calls') and len(result.tool_calls) > 0

system_prompt = """
you are a research assistant specialized in providing information from a document,
"""

tools_dict = {our_tool.name: our_tool for our_tool in tools}
tools_dict

def call_llm(state: AgentState) -> AgentState:
    """Function to call the LLM with the current state."""
    messages = list(state['messages'])
    messages = [SystemMessage(content=system_prompt)] + messages
    message = llm.invoke(messages)
    return {'messages': [message]}

# Retriever Agent
def take_action(state: AgentState) -> AgentState:
    """Execute tool calls from the LLM's response."""

    tool_calls = state['messages'][-1].tool_calls
    results = []
    for t in tool_calls:
        print(f"Calling Tool: {t['name']} with query: {t['args'].get('query', 'No query provided')}")
        
        if not t['name'] in tools_dict: # Checks if a valid tool is present
            print(f"\nTool: {t['name']} does not exist.")
            result = "Incorrect Tool Name, Please Retry and Select tool from List of Available tools."
        
        else:
            result = tools_dict[t['name']].invoke(t['args'].get('query', ''))
            print(f"Result length: {len(str(result))}")
            
        # Appends the Tool Message
        results.append(ToolMessage(tool_call_id=t['id'], name=t['name'], content=str(result)))

    print("Tools Execution Complete. Back to the model!")
    return {'messages': results}

graph = StateGraph(AgentState)
graph.add_node("llm", call_llm)
graph.add_node("retriever_agent", take_action)

graph.add_conditional_edges(
    "llm",
    should_continue,
    {True: "retriever_agent", False: END}
)
graph.add_edge("retriever_agent", "llm")
graph.set_entry_point("llm")

rag_agent = graph.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "1"}}

def running_agent():
    print("\n=== RAG AGENT===")
    
    while True:
        user_input = input("\nWhat is your question: ")
        if user_input.lower() in ['exit', 'quit']:
            break
            
        messages = [HumanMessage(content=user_input)]

        events = rag_agent.stream(
            {"messages": messages},
            config,
            stream_mode="values",
        )
        for event in events:
            # Check if the last message has pretty_print method
            last_message = event["messages"][-1]
            if hasattr(last_message, 'pretty_print'):
                last_message.pretty_print()
            else:
                print(f"Message: {last_message}")
            
running_agent()