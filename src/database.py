from typing import Any, Dict, Optional
from sqlalchemy import create_engine, inspect
from langchain_community.utilities import SQLDatabase
from langchain_core.language_models import BaseChatModel
from langchain.chains import create_sql_query_chain
from langchain_core.output_parsers import StrOutputParser

def create_db_connection(database_url: str) -> SQLDatabase:
    """Create and return a SQLDatabase instance."""
    try:
        return SQLDatabase.from_uri(database_url)
    except Exception as e:
        raise ConnectionError(f"Failed to connect to database: {str(e)}")

def get_schema_info(db: SQLDatabase) -> str:
    """Get database schema information."""
    inspector = inspect(db.engine)
    schema_info = []
    
    for table_name in inspector.get_table_names():
        columns = inspector.get_columns(table_name)
        column_info = [f"{col['name']} ({col['type']})" for col in columns]
        schema_info.append(f"Table: {table_name}\nColumns: {', '.join(column_info)}\n")
    
    return "\n".join(schema_info)

def setup_query_chain(db: SQLDatabase, llm: BaseChatModel):
    """Create and return a SQL query chain."""
    return create_sql_query_chain(llm, db) 