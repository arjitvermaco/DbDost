from typing import NoReturn
import sys
from .config import get_database_url, get_llm
from .database import create_db_connection, get_schema_info, setup_query_chain
from .query_processor import process_query
from .cli import print_welcome_message, print_results, get_user_input, console

def main() -> NoReturn:
    """Main application entry point."""
    try:
        # Initialize components
        db_url = get_database_url()
        llm = get_llm()
        db = create_db_connection(db_url)
        chain = setup_query_chain(db, llm)
        
        # Start CLI interface
        print_welcome_message()
        
        while True:
            user_input = get_user_input()
            
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