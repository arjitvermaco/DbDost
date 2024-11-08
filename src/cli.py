from typing import Optional
import sys
from rich.console import Console
from rich.table import Table

console = Console()

def print_welcome_message():
    """Print welcome message and instructions."""
    console.print("[bold blue]Welcome to Database Chat![/bold blue]")
    console.print("Type your questions in natural language or 'exit' to quit.\n")

def print_results(sql_query: str, results: Any):
    """Print SQL query and results in a formatted way."""
    console.print("\n[bold green]Generated SQL:[/bold green]")
    console.print(sql_query)
    
    console.print("\n[bold green]Results:[/bold green]")
    if isinstance(results, str):
        console.print(results)
    else:
        # Attempt to format as table if possible
        try:
            table = Table(show_header=True)
            # Add columns and rows based on results structure
            console.print(table)
        except:
            console.print(results)

def get_user_input() -> str:
    """Get input from user."""
    return console.input("\n[bold yellow]Ask a question:[/bold yellow] ").strip() 