import os
from typing import Dict, List, Optional
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import Tool
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain.agents.agent_types import AgentType
from langchain_community.agent_toolkits import SQLDatabaseToolkit

load_dotenv()

class EcommerceDBChat:
    def __init__(self):
        self.db = self._setup_database()
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0,
            max_tokens=1000
        )
        self.toolkit = SQLDatabaseToolkit(
            db=self.db,
            llm=self.llm
        )
        
        custom_prefix = """You are an expert SQL analyst helping users query an e-commerce database.
        When you receive a question:
        1. First, understand what tables and relationships are needed
        2. Write a clear, efficient SQL query
        3. Execute the query and explain the results
        
        If you're not sure about something, ask for clarification.
        Always verify your SQL before executing."""
        
        custom_suffix = """Remember to use proper JOIN conditions and handle NULL values.
        Format your responses clearly with the SQL query and results separated."""
        
        self.agent_executor = create_sql_agent(
            llm=self.llm,
            toolkit=self.toolkit,
            verbose=True,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION
        )

    def _setup_database(self) -> SQLDatabase:
        """Setup database connection"""
        url = f"mysql+mysqlconnector://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
        engine = create_engine(url)
        return SQLDatabase(engine)

    def _get_schema_info(self) -> str:
        """Get detailed schema information"""
        return self.db.get_table_info()

    def _get_sample_queries(self) -> List[str]:
        """Return a list of sample queries users can ask"""
        return [
            "What are the top 5 selling products by quantity?",
            "Show me the total revenue for each product category",
            "What's the average order value per customer?",
            "List products with stock quantity less than 10",
            "Show me product categories and their subcategories",
            "What are the top-rated products with at least 3 reviews?",
            "Show me monthly sales trends",
            "List customers who made purchases above $500",
            "What's the distribution of order statuses?",
            "Show me the most popular products in each category"
        ]

    def _enhance_query_with_context(self, query: str) -> str:
        """Enhance the query with database context"""
        schema_info = self._get_schema_info()
        return f"""Using this database schema:
        {schema_info}
        
        Question: {query}
        
        Steps to follow:
        1. Identify the relevant tables: Look at the schema and determine which tables are needed
        2. Write the SQL query:
           - Use appropriate JOINs to connect tables
           - Handle NULL values with COALESCE or IFNULL when needed
           - Use proper aggregation functions (SUM, COUNT, AVG) if required
           - Format dates and numbers for readability
        3. Execute the query and verify the results make sense
        
        Please provide a clear and detailed answer."""

    def process_query(self, query: str) -> Dict:
        """Process a natural language query"""
        try:
            # First, try with the enhanced query
            enhanced_query = self._enhance_query_with_context(query)
            result = self.agent_executor.invoke(
                {
                    "input": enhanced_query,
                    "top_k": 10
                }
            )
            
            # Check if result is empty or unclear
            if not result.get("output") or "I don't know" in result.get("output", ""):
                raise ValueError("Unclear or empty response")
            
            return {
                "status": "success",
                "result": result["output"],
                "schema_used": True
            }
            
        except Exception as e:
            # Provide specific error handling
            if "iteration limit" in str(e).lower():
                return {
                    "status": "error",
                    "result": (
                        "The query is too complex. Please try breaking it down into simpler questions. "
                        "For example, instead of asking for everything at once, you could ask:\n"
                        + "\n".join(f"- {q}" for q in self._get_sample_queries()[:3])
                    ),
                    "schema_used": True
                }
            else:
                return {
                    "status": "error",
                    "result": (
                        "I'm having trouble understanding that query. Could you rephrase it? For example:\n"
                        + "\n".join(f"- {q}" for q in self._get_sample_queries()[:3])
                    ),
                    "schema_used": True
                }

    def run(self):
        """Run the interactive chat session"""
        print("\nWelcome to E-commerce Database Chat!")
        print("You can ask questions about products, orders, customers, and more.")
        print("Type 'help' to see example queries, 'schema' to see the database structure, or 'exit' to quit.\n")
        
        while True:
            query = input("\nYour question: ").strip()
            
            if query.lower() == 'exit':
                print("Goodbye!")
                break
                
            if query.lower() == 'help':
                print("\nExample queries you can ask:")
                for q in self._get_sample_queries():
                    print(f"- {q}")
                continue
                
            if query.lower() == 'schema':
                print("\nDatabase Schema:")
                print(self._get_schema_info())
                continue
                
            if not query:
                continue
                
            try:
                result = self.process_query(query)
                if result["status"] == "error":
                    print("\nError:", result["result"])
                else:
                    if result["schema_used"]:
                        print("\n(Used schema information to enhance the response)")
                    print(f"\nResult:\n{result['result']}")
            except Exception as e:
                print(f"\nError: Something went wrong. Try rephrasing your question or type 'help' for examples.")

if __name__ == "__main__":
    chat = EcommerceDBChat()
    chat.run()