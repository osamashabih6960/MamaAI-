from fastapi import FastAPI
from pydantic import BaseModel
from router import handle

app = FastAPI(title="MamaAI", description="AI assistant for Mumzworld moms", version="1.0.0")


class QueryRequest(BaseModel):
    message: str


@app.post("/ask")
def ask(request: QueryRequest):
    """
    Main endpoint. Send any mom query — MamaAI routes it to the right module.
    """
    result = handle(request.message)
    return result


@app.get("/health")
def health_check():
    return {"status": "ok", "app": "MamaAI"}


# Run locally:
# uvicorn main:app --reload --port 8000