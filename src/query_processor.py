from typing import Dict, Any, Tuple
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

def process_query(chain, db, query: str) -> Tuple[str, Any]:
    """Process a natural language query and return SQL and results."""
    try:
        # Generate SQL query
        sql_query = chain.invoke(query)
        
        # Execute the query
        result = db.run(sql_query)
        
        return sql_query, result
    except Exception as e:
        raise RuntimeError(f"Error processing query: {str(e)}") 