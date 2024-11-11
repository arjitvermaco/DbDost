# SQL Database Chat Assistant

## Overview
This project implements an intelligent SQL database chat assistant using LangChain and OpenAI's GPT models. It allows users to interact with SQL databases using natural language, making database querying more accessible to non-technical users.

### Key Features
- Natural language to SQL query conversion
- Context-aware database interactions
- Support for SQLite and other SQL databases
- Advanced chat capabilities with memory
- Environment variable configuration
- Web interface using FastAPI

### Use Cases
- Database exploration without SQL knowledge
- Quick data analysis and reporting
- Teaching SQL concepts interactively
- Database administration assistance
- Data validation and verification

## Installation

### Prerequisites
- Python 3.8+
- pip
- Virtual environment tool (optional but recommended)
- OpenAI API key

### Setup Instructions

1. Clone the repository:

Here's the markdown formatted version:

## Project Setup

```bash
git clone https://github.com/arjitvermaco/
cd sql-database-chat
```

## Environment Setup

```bash
python -m venv .venv
source .venv/bin/activate
# On Windows: .venv\Scripts\activate
```

## Install Dependencies

```bash
pip install langchain langchain-community langchain-core python-dotenv fastapi uvicorn openai sqlite3 pydantic
```

## Configuration

```bash
cp .env.example .env
```

Create `.env` file with:
```plaintext
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-4-0125-preview
DATABASE_URL=sqlite:///your_database.db
```

## Core Functions

**Database Chain**
```python
def get_db_chain()
    # Initialize the database chain

def process_query(query: str)
    # Process natural language queries

def get_table_info()
    # Retrieve database schema information
```

**Memory Management**
```python
def setup_memory()
    # Initialize conversation memory

def process_chat()
    # Process chat messages with context

def get_relevant_context()
    # Retrieve relevant context for queries
```

**API Endpoints**
```python
@app.post("/chat")
    # Process chat messages

@app.websocket("/ws/chat")
    # Real-time chat communication

@app.get("/tables")
    # Get database schema information
```

## API Request Format

```json
{
    "query": "Show me all users who joined last month",
    "context": "optional previous context"
}
```

## API Response Format

```json
{
    "response": "Here are the users who joined last month...",
    "sql_query": "SELECT FROM users WHERE...",
    "results": [...]
}
```

## Schema Response Format

```json
{
    "tables": [
        {
            "name": "users",
            "columns": ["id", "name", "email", "joined_date"]
        }
    ]
}
```

## Usage Examples

**Basic Query**
```python
from sqlite_chat import get_db_chain

# Initialize the chain
db_chain = get_db_chain()

# Ask a question
response = db_chain.run("How many users registered last month?")
print(response)
```

**Advanced Chat**
```python
from advanced_chat import AdvancedDatabaseChat

chat = AdvancedDatabaseChat()

# Have a conversation
response = chat.chat("Show me sales trends for the last quarter")
print(response)
```

## Error Response Format

```json
{
    "error": "Database connection failed",
    "details": "Could not connect to SQLite database: database is locked",
    "code": "DB_CONNECTION_ERROR"
}
```

Citations:
[1] https://github.com/yourusername/sql-database-chat

## Security Considerations

- SQL injection prevention through parameterized queries
- Input validation using Pydantic models
- Environment variable validation
- Rate limiting on API endpoints
- Proper error handling to prevent information leakage

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support:
- Open an issue in the GitHub repository
- Contact maintainers
- Check documentation

## Acknowledgments

- LangChain team for the framework
- OpenAI for GPT models
- Contributors and maintainers