"""
track_management_agent.py

Specialized agent for managing tracks (e.g., deleting, creating, renaming).
"""

import json
import re
import asyncio # Import asyncio for async operations
import sys # Import sys for debug mode
from config import MODEL_NAME
from rag_system import retrieve_knowledge
from ableton_api_wrapper import (
    delete_track, create_midi_track, create_audio_track, set_track_name, create_clip
)
from llm_utils import get_llm_response # Import the LLM utility function

# Placeholder for Track Management Agent's system prompt (to be loaded from file)
SYSTEM_PROMPT = ""
try:
    with open("ableton_ai_controller/prompts/track_management_system_prompt.txt", "r") as f:
        SYSTEM_PROMPT = f.read()
except FileNotFoundError:
    SYSTEM_PROMPT = "Error: Track Management system prompt file not found."

async def process_request(user_input: str, conversation_history: list, current_mode: str, context_knowledge: str = None) -> str:
    """
    Processes a request related to track management using an LLM.
    """
    print(f"TrackManagementAgent: Processing request for '{user_input}' using LLM (Mode: {current_mode})...")

    # Construct the system message for the Track Management LLM, including the current mode
    agent_system_message = f"{SYSTEM_PROMPT}\n\nCurrent Mode: {current_mode}"

    messages_for_llm = [
        {"role": "system", "content": agent_system_message}
    ] + conversation_history + [ # Include conversation history
        {"role": "user", "content": user_input}
    ]

    if "--debug" in sys.argv:
        print(f"[DEBUG] Sending to LLM with prompt: {agent_system_message[:500]}...") # Log first 500 chars of system prompt
        
    try:
        llm_response_str = await get_llm_response(messages_for_llm)
        
        if "--debug" in sys.argv:
            print(f"[DEBUG] LLM Response: {llm_response_str[:500]}...") # Log first 500 chars of LLM response

        # Attempt to parse the LLM's response as JSON
        llm_response_str = llm_response_str.strip()
        
        json_content = llm_response_str
        start_marker = "```json"
        end_marker = "```"

        start_index = llm_response_str.find(start_marker)
        end_index = llm_response_str.rfind(end_marker) # Use rfind to get the last occurrence

        if start_index != -1 and end_index != -1 and end_index > start_index:
            # Extract content between markers
            # Add len(start_marker) to start_index to get past the marker
            # Use end_index directly as it's the start of the end_marker
            json_content = llm_response_str[start_index + len(start_marker) : end_index].strip()
        
        parsed_response = json.loads(json_content)

        if isinstance(parsed_response, dict) and parsed_response.get("clarification_needed"):
            return f"Track Management Agent: Clarification needed: {parsed_response.get('question')}"
        elif isinstance(parsed_response, list):
            commands_to_execute = parsed_response
        else:
            raise ValueError("LLM response is neither a list of commands nor a clarification request.")

        ableton_api_functions = {
            "delete_track": delete_track,
            "create_midi_track": create_midi_track,
            "create_audio_track": create_audio_track,
            "set_track_name": set_track_name,
            "create_clip": create_clip
        }

        results = []
        last_created_track_index = None # To store the index of the last created track

        for command in commands_to_execute:
            cmd_type = command.get("command_type")
            params = command.get("params", {})

            # If the command is create_clip and track_index is -1, use the last created track's index
            if cmd_type == "create_clip" and params.get("track_index") == -1:
                if last_created_track_index is not None:
                    params["track_index"] = last_created_track_index
                else:
                    results.append(f"Failed to execute {cmd_type}: Cannot create clip, no track index specified and no track was created recently.")
                    continue # Skip this command

            if cmd_type in ableton_api_functions:
                try:
                    result = await ableton_api_functions[cmd_type](**params)
                    results.append(f"Executed {cmd_type}: {result}")

                    # If a track was just created, store its index
                    if cmd_type == "create_midi_track" or cmd_type == "create_audio_track":
                        if isinstance(result, dict) and "index" in result:
                            last_created_track_index = result["index"]
                        else:
                            # Fallback if API doesn't return index directly, might need get_session_info
                            # For now, log a warning
                            print(f"Warning: {cmd_type} did not return track index. Cannot infer for subsequent commands.")

                except Exception as e:
                    results.append(f"Failed to execute {cmd_type}: {str(e)}")
            else:
                results.append(f"TrackManagementAgent: Unknown command type '{cmd_type}' from LLM.")
        
        return "Track Management Agent: " + "\n".join(results)

    except json.JSONDecodeError:
        return f"TrackManagementAgent: LLM response was not valid JSON. Raw response: {llm_response_str}"
    except Exception as e:
        return f"TrackManagementAgent: Error during LLM processing: {str(e)}"
