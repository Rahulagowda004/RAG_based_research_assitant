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

# Determine the correct path for vector database
import os
if os.path.exists("/app/artifacts/Vector_databases/biology"):
    persist_directory = "/app/artifacts/Vector_databases/biology"
else:
    persist_directory = "artifacts/Vector_databases/biology"

vectorstore = Chroma(
    collection_name="biology",
    embedding_function=embedding_model,
    persist_directory=persist_directory,
)
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 20}
)
    
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
    you are TAZMIC, a research assistant specialized in providing information from a **document**, and provide concise and accurate response in **friendly** and **formal** manner to user queries only based on the content of the document.
    
    If you do not have enough information to answer the question, you should say "I don't know" or "I found no relevant information in the document." instead of making up an answer.
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
        
        try:
            if t['name'] not in tools_dict:
                print(f"\nTool: {t['name']} does not exist.")
                result = "Incorrect Tool Name, Please Retry and Select tool from List of Available tools."
            else:
                result = tools_dict[t['name']].invoke(t['args'].get('query', ''))
                print(f"Result length: {len(str(result))}")
                
            # Always append the Tool Message with proper ID
            results.append(ToolMessage(tool_call_id=t['id'], name=t['name'], content=str(result)))
            
        except Exception as e:
            print(f"Error in tool execution: {e}")
            # Even on error, we must respond to the tool call
            error_result = f"Tool execution failed: {str(e)}"
            results.append(ToolMessage(tool_call_id=t['id'], name=t['name'], content=error_result))

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

def query_agent(user_input: str) -> str:
    """
    Process a single user query and return the response.
    """
    messages = [HumanMessage(content=user_input)]
    
    events = rag_agent.stream(
        {"messages": messages},
        config,
        stream_mode="values",
    )
    
    final_response = ""
    for event in events:
        last_message = event["messages"][-1]
        if hasattr(last_message, 'content') and hasattr(last_message, 'type'):
            if last_message.type == "ai":
                final_response = last_message.content
    
    return final_response

def running_agent():
    """
    Console version of the agent for testing.
    """
    print("\n=== RAG AGENT===")
    
    while True:
        user_input = input("\nWhat is your question: ")
        if user_input.lower() in ['exit', 'quit']:
            break
            
        response = query_agent(user_input)
        print(f"\nAssistant: {response}")

# Only run the console version if this file is executed directly
if __name__ == "__main__":
    running_agent()
