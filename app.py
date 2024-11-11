from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Dict, Optional, Union, List, Any
from advanced_chat import EcommerceDBChat

app = FastAPI()

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Initialize chat instance
chat_instance = EcommerceDBChat()

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    type: str  # 'text', 'table', 'error', 'sql', 'schema', 'sample_queries'
    content: Any
    sql_query: Optional[str] = None
    thought_process: Optional[Dict[str, Any]] = None  # Changed from str to Dict
    metadata: Optional[Dict[str, Any]] = None

    model_config = {
        "arbitrary_types_allowed": True
    }

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the chat interface"""
    return templates.TemplateResponse(
        "chat.html",
        {"request": request}
    )

@app.get("/schema")
async def get_schema():
    """Get database schema information"""
    try:
        schema_info = chat_instance._get_schema_info()
        return QueryResponse(
            type="schema",
            content=schema_info,
            metadata={"tables": len(schema_info.split("CREATE TABLE"))-1}
        )
    except Exception as e:
        return QueryResponse(
            type="error",
            content=str(e)
        )

@app.get("/sample-queries")
async def get_sample_queries():
    """Get sample queries"""
    try:
        queries = chat_instance._get_sample_queries()
        return QueryResponse(
            type="sample_queries",
            content=queries,
            metadata={"count": len(queries)}
        )
    except Exception as e:
        return QueryResponse(
            type="error",
            content=str(e)
        )

@app.post("/query")
async def process_query(query_request: QueryRequest) -> QueryResponse:
    """Process a chat query"""
    try:
        result = chat_instance.process_query(query_request.query)
        
        if isinstance(result, dict) and "result" in result:
            content = result["result"]
            thought_process = None
            sql_query = None
            agent_steps = []

            # Extract the complete agent steps
            if "Entering new SQL Agent Executor chain..." in content:
                # Get everything between "Entering new..." and "Final Answer:"
                full_process = content.split("Entering new SQL Agent Executor chain...")[1]
                steps_text = full_process.split("Final Answer:")[0]
                final_answer = full_process.split("Final Answer:")[1].strip() if "Final Answer:" in full_process else None
                
                # Process each step
                current_step = {}
                for line in steps_text.strip().split('\n'):
                    line = line.strip()
                    if not line:  # Skip empty lines
                        continue
                    if line.startswith('Action:'):
                        if current_step:
                            agent_steps.append(current_step)
                        current_step = {'action': line.replace('Action:', '').strip()}
                    elif line.startswith('Action Input:'):
                        current_step['input'] = line.replace('Action Input:', '').strip()
                    elif current_step and 'action' in current_step:
                        if 'observation' not in current_step:
                            current_step['observation'] = line
                        else:
                            current_step['observation'] += '\n' + line

                if current_step:
                    agent_steps.append(current_step)

                thought_process = {
                    'steps': agent_steps,
                    'final_answer': final_answer
                }

                print("Thought process:", thought_process)  # Debug print

            # Extract SQL query if present
            if "SQL Query:" in content:
                sql_parts = content.split("SQL Query:", 1)
                sql_query = sql_parts[1].split("\n")[0].strip()
                
            # Determine response type and format
            if "| " in content and "\n|" in content:
                return QueryResponse(
                    type="table",
                    content=content,
                    sql_query=sql_query,
                    thought_process=thought_process
                )
            
            return QueryResponse(
                type="text",
                content=thought_process['final_answer'] if thought_process else content,
                sql_query=sql_query,
                thought_process=thought_process
            )
        
        return QueryResponse(
            type="error",
            content="Invalid response format from chat instance"
        )
        
    except Exception as e:
        print(f"Error processing query: {str(e)}")  # Debug print
        return QueryResponse(
            type="error",
            content=str(e)
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 