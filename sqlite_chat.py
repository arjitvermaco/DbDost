import os
from typing import Dict, List
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain.agents.agent_types import AgentType
from langchain_community.agent_toolkits import SQLDatabaseToolkit

load_dotenv()

def setup_database() -> SQLDatabase:
    """Initialize SQLite database with sample e-commerce data"""
    # Using SQLite in-memory for demo purposes
    db = SQLDatabase.from_uri("sqlite:///ecommerce.db")
    
    # Create tables if they don't exist
    db.run("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT,
            price DECIMAL(10,2),
            stock_quantity INTEGER
        )
    """)
    
    db.run("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            order_date TEXT,
            total_amount DECIMAL(10,2),
            status TEXT
        )
    """)
    
    # Insert sample data if tables are empty
    if not db.run("SELECT COUNT(*) FROM products")[0][0]:
        db.run("""
            INSERT INTO products (name, category, price, stock_quantity) VALUES
            ('Laptop', 'Electronics', 999.99, 50),
            ('Smartphone', 'Electronics', 599.99, 100),
            ('Coffee Maker', 'Appliances', 79.99, 30),
            ('Running Shoes', 'Sports', 89.99, 200)
        """)
    
    if not db.run("SELECT COUNT(*) FROM orders")[0][0]:
        db.run("""
            INSERT INTO orders (customer_id, order_date, total_amount, status) VALUES
            (1, '2024-03-01', 999.99, 'Completed'),
            (2, '2024-03-02', 679.98, 'Processing'),
            (3, '2024-03-03', 169.98, 'Completed')
        """)
    
    return db

def get_sample_queries() -> List[str]:
    """Return a list of example queries"""
    return [
        "What are all products in the Electronics category?",
        "Show me the total sales by category",
        "List orders with their total amounts",
        "Which products have less than 50 items in stock?",
        "What's the average order value?"
    ]

def process_query(agent_executor: any, query: str) -> Dict:
    """Process a natural language query"""
    try:
        result = agent_executor.invoke({"input": query})
        return {
            "status": "success",
            "result": result["output"]
        }
    except Exception as e:
        return {
            "status": "error",
            "result": (
                "I'm having trouble with that query. Try one of these examples:\n"
                + "\n".join(f"- {q}" for q in get_sample_queries()[:3])
            )
        }

def run_chat():
    """Run the interactive chat session"""
    # Initialize components
    db = setup_database()
    llm = ChatOpenAI(
        model="gpt-4-turbo-preview",
        temperature=0
    )
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    
    agent_executor = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=True,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION
    )

    # Start chat interface
    print("\nWelcome to SQLite E-commerce Chat!")
    print("You can ask questions about products and orders.")
    print("Type 'help' for example queries or 'exit' to quit.\n")
    
    while True:
        query = input("\nYour question: ").strip()
        
        if query.lower() == 'exit':
            print("Goodbye!")
            break
            
        if query.lower() == 'help':
            print("\nExample queries you can ask:")
            for q in get_sample_queries():
                print(f"- {q}")
            continue
            
        if not query:
            continue
            
        result = process_query(agent_executor, query)
        if result["status"] == "error":
            print("\nError:", result["result"])
        else:
            print(f"\nResult:\n{result['result']}")

if __name__ == "__main__":
    run_chat() 