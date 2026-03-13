"""
ChromaDB vector database configuration
"""

import chromadb
from chromadb.config import Settings
import os
from dotenv import load_dotenv

load_dotenv()

# ChromaDB configuration
CHROMA_PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")

# Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(
    path=CHROMA_PERSIST_DIRECTORY,
    settings=Settings(
        anonymized_telemetry=False,
        allow_reset=True
    )
)

# Collection for content embeddings
content_collection = chroma_client.get_or_create_collection(
    name="content_embeddings",
    metadata={"description": "Content embeddings for AMAW MVP"}
)

# Collection for chat context
chat_collection = chroma_client.get_or_create_collection(
    name="chat_context",
    metadata={"description": "Chat context embeddings for AI conversations"}
)

def get_chroma_client():
    """Get ChromaDB client instance"""
    return chroma_client

def get_content_collection():
    """Get content embeddings collection"""
    return content_collection

def get_chat_collection():
    """Get chat context collection"""
    return chat_collection
