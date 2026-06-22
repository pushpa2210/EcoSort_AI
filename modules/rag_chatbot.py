"""
RAG Chatbot Module for Waste Management Knowledge Base
Uses FAISS for vector storage and HuggingFace embeddings
"""

import os
import pickle
from pathlib import Path
from typing import List, Dict, Any
import streamlit as st
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import HuggingFaceHub
from langchain_classic.chains import ConversationalRetrievalChain  # type: ignore
from langchain_classic.memory import ConversationBufferMemory  # type: ignore
from langchain_classic.prompts import PromptTemplate  # type: ignore


class WasteManagementRAG:
    """RAG Chatbot for Waste Management Knowledge Base"""
    
    def __init__(self, data_folder: str = "data"):
        """Initialize the RAG chatbot"""
        self.data_folder = Path(data_folder).resolve()
        self.vector_store = None
        self.conversation_chain = None
        self.embeddings = None
        # Use absolute path for vector store
        vector_store_dir = self.data_folder.parent / "fassi_db"
        vector_store_dir.mkdir(exist_ok=True)
        self.vector_store_path = str(vector_store_dir / "waste_management_vectorstore.pkl")
        
    def load_pdf_documents(self) -> List[Dict[str, Any]]:
        """Load all PDF documents from the data folder"""
        documents = []
        data_path = Path(self.data_folder)
        
        if not data_path.exists():
            st.error(f"Data folder '{self.data_folder}' not found!")
            return documents
        
        pdf_files = list(data_path.glob("*.pdf"))
        
        if not pdf_files:
            st.warning(f"No PDF files found in '{self.data_folder}'")
            return documents
        
        for pdf_file in pdf_files:
            try:
                pdf_reader = PdfReader(str(pdf_file))
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                
                documents.append({
                    "content": text,
                    "metadata": {
                        "source": pdf_file.name,
                        "page_count": len(pdf_reader.pages)
                    }
                })
                
            except Exception as e:
                st.warning(f"Error reading {pdf_file.name}: {str(e)}")
        
        return documents
    
    def create_text_chunks(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Split documents into smaller chunks"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        
        chunks = []
        for doc in documents:
            splits = text_splitter.split_text(doc["content"])
            for i, split in enumerate(splits):
                chunks.append({
                    "content": split,
                    "metadata": {
                        **doc["metadata"],
                        "chunk_id": i
                    }
                })
        
        return chunks
    
    def create_vector_store(self, force_rebuild: bool = False):
        """Create or load FAISS vector store"""
        
        # Check if vector store already exists
        if os.path.exists(self.vector_store_path) and not force_rebuild:
            try:
                with open(self.vector_store_path, 'rb') as f:
                    self.vector_store = pickle.load(f)
                st.success("✅ Loaded existing vector store")
                return
            except Exception as e:
                st.warning(f"Could not load existing vector store: {str(e)}")
        
        # Create embeddings
        with st.spinner("🔄 Initializing embeddings model..."):
            # Disable tqdm progress bars to avoid stderr issues in Streamlit
            os.environ['TQDM_DISABLE'] = '1'
            
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'show_progress_bar': False}
            )
        
        # Load and process documents
        with st.spinner("📄 Loading PDF documents..."):
            documents = self.load_pdf_documents()
            
        if not documents:
            st.error("No documents loaded!")
            return
        
        st.info(f"📚 Loaded {len(documents)} documents")
        
        # Create chunks
        with st.spinner("✂️ Creating text chunks..."):
            chunks = self.create_text_chunks(documents)
        
        st.info(f"📦 Created {len(chunks)} text chunks")
        
        # Create vector store
        with st.spinner("🔍 Building vector store (this may take a few minutes)..."):
            texts = [chunk["content"] for chunk in chunks]
            metadatas = [chunk["metadata"] for chunk in chunks]
            
            self.vector_store = FAISS.from_texts(
                texts=texts,
                embedding=self.embeddings,
                metadatas=metadatas
            )
        
        # Save vector store
        os.makedirs(os.path.dirname(self.vector_store_path), exist_ok=True)
        with open(self.vector_store_path, 'wb') as f:
            pickle.dump(self.vector_store, f)
        
        st.success("✅ Vector store created and saved successfully!")
    
    def setup_conversation_chain(self, huggingface_api_key: str | None = None):
        """Setup the conversational retrieval chain"""
        
        if self.vector_store is None:
            st.error("Vector store not initialized!")
            return
        
        # Initialize embeddings if not already done
        if self.embeddings is None:
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'}
            )
        
        # Create custom prompt template
        prompt_template = """You are an expert assistant for waste management and sustainability. 
        Use the following context to answer the question. If you don't know the answer based on the context, 
        say so honestly. Always provide practical and actionable advice.

        Context: {context}

        Question: {question}

        Answer: """
        
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        # Setup memory
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
        
        # Setup LLM (using HuggingFace Hub)
        if huggingface_api_key:
            os.environ["HUGGINGFACEHUB_API_TOKEN"] = huggingface_api_key
            llm = HuggingFaceHub(
                repo_id="google/flan-t5-large",
                model_kwargs={"temperature": 0.7, "max_length": 512}
            )
        else:
            # Fallback to a simple retrieval-only mode
            st.warning("⚠️ No HuggingFace API key provided. Using retrieval-only mode.")
            llm = None
        
        # Create conversation chain
        if llm:
            self.conversation_chain = ConversationalRetrievalChain.from_llm(
                llm=llm,
                retriever=self.vector_store.as_retriever(search_kwargs={"k": 3}),
                memory=memory,
                combine_docs_chain_kwargs={"prompt": PROMPT},
                return_source_documents=True
            )
        else:
            # Simple retrieval without LLM
            self.conversation_chain = None
    
    def get_response(self, question: str) -> Dict[str, Any]:
        """Get response for a user question"""
        
        if self.vector_store is None:
            return {
                "answer": "Please initialize the knowledge base first.",
                "sources": []
            }
        
        # Retrieve relevant documents
        docs = self.vector_store.similarity_search(question, k=3)
        
        if self.conversation_chain:
            # Use full RAG chain with LLM
            response = self.conversation_chain({"question": question})
            return {
                "answer": response["answer"],
                "sources": response.get("source_documents", [])
            }
        else:
            # Simple retrieval mode - return relevant chunks
            answer = "Based on the waste management documents, here are the relevant sections:\n\n"
            for i, doc in enumerate(docs, 1):
                answer += f"{i}. {doc.page_content[:300]}...\n\n"
                answer += f"   (Source: {doc.metadata.get('source', 'Unknown')})\n\n"
            
            return {
                "answer": answer,
                "sources": docs
            }
    
    def clear_conversation_history(self):
        """Clear the conversation history"""
        if self.conversation_chain and hasattr(self.conversation_chain, 'memory'):
            self.conversation_chain.memory.clear()

# Made with Bob
