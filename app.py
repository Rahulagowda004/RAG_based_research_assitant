import streamlit as st
import sys
import os
from pathlib import Path

src_path = Path(__file__).parent / "src"
sys.path.append(str(src_path))

from main import query_agent

# Configure page
st.set_page_config(
    page_title="TAZMIC - Research Assistant",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar with enhanced content
with st.sidebar:
    st.markdown("# 🔬 TAZMIC")
    st.markdown("### *Transformer Analysis & Zero-shot Multi-modal Intelligence Chat*")
    
    st.markdown("---")
    
    st.markdown("### � About")
    st.markdown("""
    **TAZMIC** is an advanced RAG-powered research assistant that specializes in:
    - 🧠 **AI Research Analysis**
    - 🔍 **Document Q&A**
    - 📊 **Multi-modal Understanding**
    - 💡 **Intelligent Retrieval**
    """)
    
    st.markdown("---")
    
    st.markdown("### 🎯 Current Focus")
    st.info("Analyzing: *On the Biology of a Large Language Model* from Transformer Circuits")
    
    st.markdown("### 🔗 Resources")
    st.markdown("""
    - [📄 Source Paper](https://transformer-circuits.pub/2025/attribution-graphs/biology.html)
    - [💻 GitHub Repository](https://github.com/Rahulagowda004/TAZMIC)
    - [🏗️ View Architecture](pictures/workflow.png)
    """)
    
    st.markdown("---")
    
    st.markdown("### 💡 Example Questions")
    st.markdown("""
    Try asking:
    - *"What is this research about?"*
    - *"Explain the key findings"*
    - *"What methods were used?"*
    - *"How does this relate to AI safety?"*
    """)
    
    st.markdown("---")
    st.caption("Powered by Azure OpenAI & LangGraph")

# Main interface
col1, col2 = st.columns([3, 1])

with col1:
    st.title("🔬 TAZMIC Research Assistant")
    st.markdown("### *Intelligent Analysis of AI Research Papers*")

with col2:
    st.markdown("### 📊 Stats")
    
    # Custom styled info boxes instead of metrics
    st.markdown("""
    <div style="background-color: #1e1e1e; padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 1px solid #333;">
        <h4 style="color: #ffffff; margin: 0; font-size: 14px;">📄 Document Source</h4>
        <p style="color: #00d4aa; margin: 5px 0 0 0; font-size: 16px; font-weight: bold;">Transformer Circuits</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background-color: #1e1e1e; padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 1px solid #333;">
        <h4 style="color: #ffffff; margin: 0; font-size: 14px;">🤖 AI Model</h4>
        <p style="color: #ff6b6b; margin: 5px 0 0 0; font-size: 16px; font-weight: bold;">gpt 4o</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Feature highlights
st.markdown("### 🚀 What I Can Help You With")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    **🔍 Research Analysis**
    - Deep paper insights
    - Key concept extraction
    - Methodology explanation
    """)

with col2:
    st.markdown("""
    **🧠 AI Understanding**
    - Neural network mechanisms
    - Training methodologies
    - Model interpretability
    """)

with col3:
    st.markdown("""
    **📊 Data Insights**
    - Experimental results
    - Performance metrics
    - Comparative analysis
    """)

with col4:
    st.markdown("""
    **💡 Learning Support**
    - Concept clarification
    - Related work connections
    - Future research directions
    """)

st.markdown("---")

# Chat interface
st.markdown("### 💬 Ask Me Anything About the Research")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "assistant", 
            "content": """👋 **Welcome to TAZMIC!** 

I'm your AI research assistant, specialized in analyzing the paper *"On the Biology of a Large Language Model"* from Anthropic's Transformer Circuits team.

🎯 **I can help you:**
- Understand complex AI concepts from the paper
- Explain experimental methodologies
- Discuss implications for AI safety and interpretability
- Connect findings to broader AI research

**Try asking me something specific about the research!** 🚀"""
        }
    ]

# Display chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input with enhanced UX
if prompt := st.chat_input("💭 Ask me about the research... (e.g., 'What are the main findings?')"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            with st.spinner("🔍 Analyzing research documents and generating response..."):
                response = query_agent(prompt)
            
            if response and response.strip():
                message_placeholder.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            else:
                error_message = """❌ **No Relevant Information Found**
                
I couldn't find specific information about your question in the research document. 

**Try:**
- 🔄 Rephrasing your question with different keywords
- 🎯 Being more specific about what aspect interests you
- 📚 Asking about core concepts from the paper (transformers, neural circuits, interpretability)
                """
                message_placeholder.markdown(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})
            
        except Exception as e:
            error_str = str(e)
            
            # Handle specific tool_calls error
            if "tool_calls" in error_str and "tool_call_id" in error_str:
                error_message = """🔧 **Agent Processing Issue**
                
The system encountered a coordination issue between components. This usually resolves itself.

**Please try:**
- 🔄 **Ask your question again** - the system will reset automatically
- 💬 **Rephrase slightly** if the issue persists
- 🎯 **Use simpler language** for complex queries

*This is a temporary technical issue, not a problem with your question.*
                """
            else:
                error_message = f"""⚠️ **System Error**
                
I encountered a technical issue: `{error_str}`

**Please:**
- 🔄 Try your question again
- 📝 Simplify your query if it was complex
- 🛠️ Contact support if the issue persists
                """
            
            message_placeholder.markdown(error_message)
            st.session_state.messages.append({"role": "assistant", "content": error_message})

# Add some CSS for better styling
st.markdown("""
<style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
    }f
    .stExpander {
        background-color: #f8f9fa;
        border-left: 4px solid #007acc;
    }
    
    /* Ensure proper text rendering in dark mode */
    .stMarkdown {
        color: inherit;
    }
    
    /* Custom stat cards styling */
    .stat-card {
        background-color: #1e1e1e;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        border: 1px solid #333;
    }
    
    .stat-title {
        color: #ffffff;
        margin: 0;
        font-size: 14px;
        font-weight: 600;
    }
    
    .stat-value {
        margin: 5px 0 0 0;
        font-size: 16px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)