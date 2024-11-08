from dotenv import load_dotenv
import os
from typing import Optional
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI

load_dotenv()

def get_database_url() -> str:
    """Get database URL from environment variables."""
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "3306")
    database = os.getenv("DB_NAME")
    
    if not all([user, password, database]):
        raise ValueError("Missing required database environment variables")
        
    return f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"

def get_llm() -> BaseChatModel:
    """Initialize and return the LLM."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")
        
    return ChatOpenAI(
        model="gpt-4-turbo-preview",
        temperature=0,
        api_key=api_key
    ) 