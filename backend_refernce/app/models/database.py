"""
Database models for AMAW MVP
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class Node(Base):
    """Node model for storing canvas nodes"""
    __tablename__ = "nodes"
    
    id = Column(String, primary_key=True, index=True)
    type = Column(String, nullable=False)  # youtube, text, document, image, website, code, ai_chat
    position_x = Column(Integer, nullable=False)
    position_y = Column(Integer, nullable=False)
    data = Column(JSON)  # Store node-specific data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Content(Base):
    """Content model for storing extracted content"""
    __tablename__ = "content"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    node_id = Column(String, nullable=False, index=True)
    source_url = Column(String)  # YouTube URL, website URL, etc.
    platform = Column(String)  # youtube, website, document, etc.
    title = Column(String)
    description = Column(Text)
    thumbnail_url = Column(String)
    extra_data = Column(JSON)  # Additional platform-specific metadata
    content_text = Column(Text)  # Extracted text content
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Embedding(Base):
    """Embedding model for storing vector embeddings"""
    __tablename__ = "embeddings"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    content_id = Column(Integer, nullable=False, index=True)
    node_id = Column(String, nullable=False, index=True)
    embedding_vector = Column(LargeBinary)  # Store embedding as binary
    embedding_model = Column(String)  # Model used for embedding
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ChatSession(Base):
    """Chat session model for AI conversations"""
    __tablename__ = "chat_sessions"
    
    id = Column(String, primary_key=True, index=True)
    node_id = Column(String, nullable=False, index=True)  # AI Chat Node ID
    messages = Column(JSON)  # Store chat messages
    context_nodes = Column(JSON)  # Connected nodes providing context
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class GeneratedImage(Base):
    """Generated image model for AI-generated content"""
    __tablename__ = "generated_images"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    node_id = Column(String, nullable=False, index=True)
    prompt = Column(Text)
    image_data = Column(LargeBinary)  # Store image as binary
    image_url = Column(String)  # URL if stored externally
    model_used = Column(String)  # Gemini, DALL-E, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
