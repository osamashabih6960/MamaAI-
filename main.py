from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from router import handle

app = FastAPI(title="MamaAI")


class QueryRequest(BaseModel):
    message: str


@app.post("/ask")
def ask(request: QueryRequest):
    return handle(request.message)


@app.get("/health")
def health_check():
    return {"status": "ok", "app": "MamaAI"}


@app.get("/", response_class=HTMLResponse)
def ui():
    with open("ui.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

# Run: uvicorn main:app --reload --port 8000