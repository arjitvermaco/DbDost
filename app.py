from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Dict, Optional
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
    return {"schema": chat_instance._get_schema_info()}

@app.get("/sample-queries")
async def get_sample_queries():
    """Get sample queries"""
    return {"queries": chat_instance._get_sample_queries()}

@app.post("/query")
async def process_query(query_request: QueryRequest) -> Dict:
    """Process a chat query"""
    try:
        result = chat_instance.process_query(query_request.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 