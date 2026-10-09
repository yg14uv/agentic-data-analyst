import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.agents.data_analyst import run_data_analyst
from backend.memory.store import clear_history, get_history


app = FastAPI()


FRONTEND_URL = os.getenv("FRONTEND_URL")

allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

if FRONTEND_URL:
    allowed_origins.append(FRONTEND_URL.rstrip("/"))


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


@app.get("/")
def root():
    return {
        "message": "Agentic Data Analyst API is running"
    }


@app.post("/chat")
def chat(request: ChatRequest):
    return run_data_analyst(
        user_message=request.message,
        session_id=request.session_id
    )


@app.get("/memory/{session_id}")
def memory(session_id: str):
    return {
        "session_id": session_id,
        "history": get_history(session_id)
    }


@app.delete("/memory/{session_id}")
def delete_memory(session_id: str):
    clear_history(session_id)

    return {
        "success": True,
        "session_id": session_id,
        "message": "Conversation memory cleared."
    }