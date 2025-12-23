"""
RAG Engine for KidneyCompanion
Handles document ingestion, vector storage, and semantic retrieval
"""

import os
import glob
from typing import List, Dict, Any
import google.generativeai as genai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import FastEmbedEmbeddings
from dotenv import load_dotenv

load_dotenv()

class RAGEngine:
    def __init__(self, persist_directory="data/chroma_db", knowledge_dir="data/medical_knowledge"):
        self.persist_directory = persist_directory
        self.knowledge_dir = knowledge_dir
        self.api_key = os.getenv('GEMINI_API_KEY')
        
        # Initialize Embeddings
        # Switching to FastEmbed to avoid PyTorch hangs on Windows
        # This uses ONNX Runtime which is lighter and faster
        self.embeddings = FastEmbedEmbeddings()
        
        # Initialize Vector Store
        self._init_vector_store()
        
    def _init_vector_store(self):
        """Initialize or load the ChromaDB vector store"""
        if os.path.exists(self.persist_directory):
            self.vector_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
        else:
            # Create empty if not exists, will be populated on ingest
            self.vector_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
            
    def ingest_documents(self):
        """Load and process all documents from the knowledge directory"""
        documents = []
        
        # Load PDFs
        pdf_files = glob.glob(os.path.join(self.knowledge_dir, "*.pdf"))
        for pdf_path in pdf_files:
            try:
                loader = PyPDFLoader(pdf_path)
                documents.extend(loader.load())
                print(f"Loaded PDF: {pdf_path}")
            except Exception as e:
                print(f"Error loading PDF {pdf_path}: {e}")
                
        # Load Text Files
        txt_files = glob.glob(os.path.join(self.knowledge_dir, "*.txt"))
        for txt_path in txt_files:
            try:
                loader = TextLoader(txt_path)
                documents.extend(loader.load())
                print(f"Loaded Text: {txt_path}")
            except Exception as e:
                print(f"Error loading Text {txt_path}: {e}")
                
        if not documents:
            print("No documents found to ingest.")
            return False
            
        # Split text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
        
        splits = text_splitter.split_documents(documents)
        print(f"Created {len(splits)} chunks from documents.")
        
        # Add to vector store
        self.vector_store.add_documents(documents=splits)
        self.vector_store.persist()
        print("Knowledge base updated and persisted.")
        return True
        
    def search(self, query: str, k: int = 3) -> List[str]:
        """Search for relevant context for a query"""
        try:
            docs = self.vector_store.similarity_search(query, k=k)
            return [doc.page_content for doc in docs]
        except Exception as e:
            print(f"Error during RAG search: {e}")
            return []
            
            return []
            
# Singleton instance
_rag_engine_instance = None

def get_rag_engine():
    """Factory function to get or create the singleton RAG engine"""
    global _rag_engine_instance
    if _rag_engine_instance is None:
        print("Initializing RAGEngine Singleton...")
        _rag_engine_instance = RAGEngine()
    else:
        print("Using existing RAGEngine Singleton.")
    return _rag_engine_instance
