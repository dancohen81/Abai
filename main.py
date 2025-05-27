"""
main.py

Main entry point for the Ableton AI Controller application.
Handles user input and orchestrates the multi-agent system.
"""

import asyncio
import json # Import json module
from agents.orchestrator import route_request
from ableton_api_wrapper import get_session_info # Import get_session_info
from utils import update_session_metadata # Import update_session_metadata

async def main():
    """
    Main asynchronous function to run the Ableton AI Controller.
    Manages conversation history and current mode.
    """
    # RAGSystem is initialized globally in rag_system.py and prints its own initialization message.
    # No need to re-initialize or print here.

    conversation_history = []
    current_mode = "default" # Initial mode

    # Retrieve initial session information
    initial_session_info = {}
    try:
        print("Retrieving initial Ableton session information...")
        initial_session_info = await get_session_info()
        print("Initial session information retrieved.")
    except Exception as e:
        print(f"Warning: Could not retrieve initial session information: {e}. Continuing without it.")
    
    # Add initial session info to conversation history as a system message
    if initial_session_info:
        conversation_history.append({"role": "system", "content": f"Initial Ableton Session Info: {json.dumps(initial_session_info)}"})
        
        # Update the session metadata file
        update_session_metadata(initial_session_info)

        # Check for and display song name
        song_name = initial_session_info.get("song_name") or initial_session_info.get("project_name")
        if song_name:
            print(f"Current Ableton Project: {song_name}")
        else:
            print("Song name not found in initial session info.")

    print("Ableton AI Controller started. Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break

        # Check for explicit mode change command
        if user_input.lower().startswith("set mode to "):
            new_mode = user_input.lower().replace("set mode to ", "").strip()
            current_mode = new_mode
            print(f"AI: Mode set to '{current_mode}'.")
            continue
        
        # Check for explicit save project command
        if user_input.lower().startswith("save project to "):
            save_path = user_input.lower().replace("save project to ", "").strip()
            try:
                from ableton_api_wrapper import save_project
                await save_project(save_path)
                print(f"AI: Project saved to '{save_path}'.")
            except Exception as e:
                print(f"AI: Failed to save project: {e}")
            continue

        # Add user's prompt to conversation history
        conversation_history.append({"role": "user", "content": user_input})

        # Pass conversation history, current mode, and initial session info to the orchestrator
        response = await route_request(user_input, conversation_history, current_mode, initial_session_info)
        print(f"AI: {response}")

        # Add AI's response to conversation history
        # This assumes the response is a string. If it's a JSON, you might need to extract the relevant part.
        conversation_history.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    asyncio.run(main())
