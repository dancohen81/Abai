from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import json
import sys
import os

# Add the parent directory to the sys.path to allow imports from the main project
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.orchestrator import route_request
from ableton_api_wrapper import get_session_info, save_project
from utils import update_session_metadata

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:5173", # Allow requests from the Vite development server
    "http://localhost:5174", # Allow requests from the Vite development server on port 5174
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for conversation history and mode (for simplicity, can be replaced with a proper session management)
# This will be per-server instance, not per-user. For a multi-user app, this needs to be more robust.
session_data = {
    "conversation_history": [],
    "current_mode": "default",
    "initial_session_info": {}
}

class ChatRequest(BaseModel):
    user_input: str

@app.on_event("startup")
async def startup_event():
    """
    Retrieve initial Ableton session information on startup.
    """
    print("Attempting to retrieve initial Ableton session information on startup...")
    try:
        initial_session_info = await get_session_info()
        session_data["initial_session_info"] = initial_session_info
        session_data["conversation_history"].append({"role": "system", "content": f"Initial Ableton Session Info: {json.dumps(initial_session_info)}"})
        update_session_metadata(initial_session_info)
        print("Initial session information retrieved successfully.")
    except Exception as e:
        print(f"Warning: Could not retrieve initial session information on startup: {e}. Continuing without it.")

@app.get("/")
async def read_root():
    return {"message": "Ableton AI Controller Backend is running!"}

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    user_input = request.user_input

    if user_input.lower() == 'exit':
        return {"response": "Exiting conversation. Please refresh the page to start a new session."}

    # Check for explicit mode change command
    if user_input.lower().startswith("set mode to "):
        new_mode = user_input.lower().replace("set mode to ", "").strip()
        session_data["current_mode"] = new_mode
        return {"response": f"Mode set to '{session_data['current_mode']}'."}
    
    # Check for explicit save project command
    if user_input.lower().startswith("save project to "):
        save_path = user_input.lower().replace("save project to ", "").strip()
        try:
            await save_project(save_path)
            return {"response": f"Project saved to '{save_path}'."}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save project: {e}")

    session_data["conversation_history"].append({"role": "user", "content": user_input})

    try:
        response = await route_request(
            user_input,
            session_data["conversation_history"],
            session_data["current_mode"],
            session_data["initial_session_info"]
        )
        session_data["conversation_history"].append({"role": "assistant", "content": response})
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {e}")

@app.get("/session_info")
async def get_current_session_info():
    return {"session_info": session_data["initial_session_info"]}

@app.get("/conversation_history")
async def get_conversation_history():
    return {"history": session_data["conversation_history"]}

@app.get("/current_mode")
async def get_current_mode():
    return {"mode": session_data["current_mode"]}
