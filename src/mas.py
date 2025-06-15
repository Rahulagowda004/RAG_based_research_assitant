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

class CreateRagAgent:
    
    def __init__(self, retriever):
        self.retriever = retriever
        self.llm = llm
        self.system_prompt = """
        you are TAZMIC, a research assistant specialized in providing information from a **document**, and provide concise and accurate response in **friendly** and **formal** manner to user queries only based on the content of the document.
        
        If you do not have enough information to answer the question, you should say "I don't know" or "I found no relevant information in the document." instead of making up an answer.
        """
        
        load_dotenv()
        self.memory = MemorySaver()
        self.config = {"configurable": {"thread_id": "1"}}
        
        # Initialize tools and agent
        self._setup_tools()
        self._setup_agent()
    
    def _setup_tools(self):
        """Setup the retriever tool"""
        @tool
        def retriever_tool(query: str) -> str:
            """
            This tool searches and returns the information from the document.
            """
            docs = self.retriever.invoke(query)

            if not docs:
                return "I found no relevant information in the document."
            
            results = []
            for i, doc in enumerate(docs):
                results.append(f"Document {i+1}:\n{doc.page_content}")
            
            return "\n\n".join(results)
        
        self.tools = [retriever_tool]
        self.tools_dict = {tool.name: tool for tool in self.tools}
        self.llm_with_tools = self.llm.bind_tools(self.tools)
    
    def _setup_agent(self):
        """Setup the LangGraph agent"""
        class AgentState(TypedDict):
            messages: Annotated[Sequence[BaseMessage], add_messages]
        
        self.AgentState = AgentState
        
        # Create the graph
        self.graph = StateGraph(AgentState)
        self.graph.add_node("llm", self._call_llm)
        self.graph.add_node("retriever_agent", self._take_action)

        self.graph.add_conditional_edges(
            "llm",
            self._should_continue,
            {True: "retriever_agent", False: END}
        )
        self.graph.add_edge("retriever_agent", "llm")
        self.graph.set_entry_point("llm")

        self.rag_agent = self.graph.compile(checkpointer=self.memory)
    
    def _should_continue(self, state):
        """Check if the last message contains tool calls."""
        result = state['messages'][-1]
        return hasattr(result, 'tool_calls') and len(result.tool_calls) > 0

    def _call_llm(self, state):
        """Function to call the LLM with the current state."""
        messages = list(state['messages'])
        messages = [SystemMessage(content=self.system_prompt)] + messages
        message = self.llm_with_tools.invoke(messages)
        return {'messages': [message]}

    def _take_action(self, state):
        """Execute tool calls from the LLM's response."""
        tool_calls = state['messages'][-1].tool_calls
        results = []
        
        for t in tool_calls:
            print(f"Calling Tool: {t['name']} with query: {t['args'].get('query', 'No query provided')}")
            
            if t['name'] not in self.tools_dict:
                print(f"\nTool: {t['name']} does not exist.")
                result = "Incorrect Tool Name, Please Retry and Select tool from List of Available tools."
            else:
                result = self.tools_dict[t['name']].invoke(t['args'].get('query', ''))
                print(f"Result length: {len(str(result))}")
                
            # Appends the Tool Message
            results.append(ToolMessage(tool_call_id=t['id'], name=t['name'], content=str(result)))

        print("Tools Execution Complete. Back to the model!")
        return {'messages': results}

    def query_agent(self, user_input: str) -> str:
        """
        Process a single user query and return the response.
        """
        messages = [HumanMessage(content=user_input)]
        
        events = self.rag_agent.stream(
            {"messages": messages},
            self.config,
            stream_mode="values",
        )
        
        final_response = ""
        for event in events:
            last_message = event["messages"][-1]
            if hasattr(last_message, 'content') and hasattr(last_message, 'type'):
                if last_message.type == "ai":
                    final_response = last_message.content
        
        return final_response

    def run_console_agent(self):
        """
        Console version of the agent for testing.
        """
        print("\n=== RAG AGENT ===")
        
        while True:
            user_input = input("\nWhat is your question: ")
            if user_input.lower() in ['exit', 'quit']:
                break
                
            response = self.query_agent(user_input)
            print(f"\nAssistant: {response}")