from typing import Any, NoReturn, Tuple
import os
import sys
from dotenv import load_dotenv
from rich.console import Console
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain.chains.sql_database.query import create_sql_query_chain
from langchain_core.prompts import ChatPromptTemplate

# Initialize console for rich output
console = Console()

def setup_environment() -> Tuple[SQLDatabase, Any]:
    """Setup database and LLM connections."""
    load_dotenv()
    
    # Validate environment variables
    required_vars = ["DB_USER", "DB_PASSWORD", "DB_NAME", "OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    # Create database URL and connection
    db_url = (f"mysql+mysqlconnector://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
              f"@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}"
              f"/{os.getenv('DB_NAME')}")
    
    try:
        db = SQLDatabase.from_uri(db_url)
        llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        chain = create_sql_query_chain(llm, db, prompt=None)
        return db, chain
    except Exception as e:
        raise ConnectionError(f"Failed to initialize: {str(e)}")

def process_query(chain: Any, db: SQLDatabase, query: str) -> Tuple[str, Any]:
    """Process a natural language query."""
    try:
        # Get SQL query from chain
        sql_query = chain.invoke({"question": query})
        
        # Clean up the query by removing any "SQLQuery:" prefix
        if isinstance(sql_query, str) and sql_query.startswith("SQLQuery:"):
            sql_query = sql_query.replace("SQLQuery:", "").strip()
            
        # Execute the cleaned query
        result = db.run(sql_query)
        return sql_query, result
    except Exception as e:
        raise RuntimeError(f"Error processing query: {str(e)}")

def print_results(sql_query: str, results: Any):
    """Print results in a formatted way."""
    console.print("\n[bold green]Generated SQL:[/bold green]")
    console.print(sql_query)
    
    console.print("\n[bold green]Results:[/bold green]")
    console.print(results)

def main() -> NoReturn:
    """Main application entry point."""
    try:
        # Initialize components
        db, chain = setup_environment()
        
        # Print welcome message
        console.print("[bold blue]Welcome to Database Chat![/bold blue]")
        console.print("Type your questions in natural language or 'exit' to quit.\n")
        
        while True:
            # Get user input
            user_input = console.input("\n[bold yellow]Ask a question:[/bold yellow] ").strip()
            
            if user_input.lower() in ('exit', 'quit'):
                console.print("[bold blue]Goodbye![/bold blue]")
                sys.exit(0)
                
            try:
                sql_query, results = process_query(chain, db, user_input)
                print_results(sql_query, results)
            except Exception as e:
                console.print(f"[bold red]Error:[/bold red] {str(e)}")

    except Exception as e:
        console.print(f"[bold red]Fatal Error:[/bold red] {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 