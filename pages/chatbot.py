"""
Waste Management Knowledge Base Chatbot Page
RAG-based chatbot for answering questions about waste management
"""

import streamlit as st
import sys
import os
from pathlib import Path

# Add parent directory to path
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

from modules.rag_chatbot import WasteManagementRAG


def initialize_chatbot():
    """Initialize the chatbot in session state"""
    if 'rag_chatbot' not in st.session_state:
        # Use absolute path to data folder
        data_folder = parent_dir / "data"
        st.session_state.rag_chatbot = WasteManagementRAG(data_folder=str(data_folder))
        st.session_state.chat_history = []
        st.session_state.vector_store_initialized = False


def main():
    st.set_page_config(
        page_title="Waste Management Chatbot",
        page_icon="🤖",
        layout="wide"
    )
    
    # Initialize chatbot
    initialize_chatbot()
    
    # Header
    st.title("🤖 Waste Management Knowledge Assistant")
    st.markdown("""
    Ask me anything about waste management, recycling rules, and sustainability practices!
    I'm trained on official waste management guidelines and regulations.
    """)
    
    # Sidebar for settings
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Vector store initialization
        st.subheader("📚 Knowledge Base")
        
        if not st.session_state.vector_store_initialized:
            st.warning("⚠️ Knowledge base not initialized")
            
            if st.button("🔄 Initialize Knowledge Base", type="primary"):
                with st.spinner("Initializing knowledge base..."):
                    st.session_state.rag_chatbot.create_vector_store(force_rebuild=False)
                    st.session_state.vector_store_initialized = True
                    st.rerun()
        else:
            st.success("✅ Knowledge base ready")
            
            if st.button("🔄 Rebuild Knowledge Base"):
                with st.spinner("Rebuilding knowledge base..."):
                    st.session_state.rag_chatbot.create_vector_store(force_rebuild=True)
                    st.success("Knowledge base rebuilt!")
                    st.rerun()
        
        st.divider()
        
        # Optional: HuggingFace API Key
        st.subheader("🔑 Advanced Settings")
        st.markdown("*Optional: For enhanced AI responses*")
        
        hf_api_key = st.text_input(
            "HuggingFace API Key",
            type="password",
            help="Enter your HuggingFace API key for AI-powered responses. Leave empty for retrieval-only mode."
        )
        
        if hf_api_key:
            st.session_state.rag_chatbot.setup_conversation_chain(hf_api_key)
            st.success("✅ AI mode enabled")
        else:
            st.info("ℹ️ Using retrieval-only mode")
        
        st.divider()
        
        # Clear chat history
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            if hasattr(st.session_state.rag_chatbot, 'clear_conversation_history'):
                st.session_state.rag_chatbot.clear_conversation_history()
            st.rerun()
        
        st.divider()
        
        # Information
        st.subheader("ℹ️ About")
        st.markdown("""
        This chatbot uses:
        - **RAG** (Retrieval-Augmented Generation)
        - **FAISS** vector database
        - **HuggingFace** embeddings
        - Official waste management PDFs
        """)
        
        # Document sources
        st.subheader("📄 Knowledge Sources")
        st.markdown("""
        - BMW Rules
        - E-waste Rules
        - PWM Rules
        - SBM Guidelines
        - Solid Waste Management Rules
        - Waste Segregation Guidelines
        """)
    
    # Main chat interface
    if not st.session_state.vector_store_initialized:
        st.info("👈 Please initialize the knowledge base from the sidebar to start chatting!")
        
        # Show example questions
        st.subheader("💡 Example Questions")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            - What are the BMW rules?
            - How should I segregate waste?
            - What are the e-waste disposal guidelines?
            - What is the penalty for improper waste disposal?
            """)
        
        with col2:
            st.markdown("""
            - How to manage plastic waste?
            - What are the SBM guidelines?
            - How to set up a waste collection system?
            - What are the best practices for recycling?
            """)
    else:
        # Display chat history
        chat_container = st.container()
        
        with chat_container:
            for i, message in enumerate(st.session_state.chat_history):
                if message["role"] == "user":
                    with st.chat_message("user", avatar="👤"):
                        st.markdown(message["content"])
                else:
                    with st.chat_message("assistant", avatar="🤖"):
                        st.markdown(message["content"])
                        
                        # Show sources if available
                        if "sources" in message and message["sources"]:
                            with st.expander("📚 View Sources"):
                                for j, source in enumerate(message["sources"][:3], 1):
                                    st.markdown(f"**Source {j}:** {source.metadata.get('source', 'Unknown')}")
                                    st.text(source.page_content[:200] + "...")
                                    st.divider()
        
        # Chat input
        user_question = st.chat_input("Ask a question about waste management...")
        
        if user_question:
            # Add user message to history
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_question
            })
            
            # Get response
            with st.spinner("🤔 Thinking..."):
                response = st.session_state.rag_chatbot.get_response(user_question)
            
            # Add assistant response to history
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response["answer"],
                "sources": response.get("sources", [])
            })
            
            # Rerun to display new messages
            st.rerun()
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: gray; font-size: 0.9em;'>
        💡 Tip: The more specific your question, the better the answer!
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

# Made with Bob
