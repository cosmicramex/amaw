"""
Database initialization script
"""

from app.database.connection import create_tables, engine
from app.models.database import Base
from app.database.vector_db import get_chroma_client
import os

def init_database():
    """Initialize database and create tables"""
    print("Initializing database...")
    
    # Create tables
    create_tables()
    print("✅ Database tables created successfully")
    
    # Initialize ChromaDB
    try:
        chroma_client = get_chroma_client()
        print("✅ ChromaDB initialized successfully")
    except Exception as e:
        print(f"❌ ChromaDB initialization failed: {e}")
    
    print("🎉 Database initialization completed!")

if __name__ == "__main__":
    init_database()
