"""
cutter_editor_agent.py

Specialized agent for clip manipulation (cutting, editing, duplicating, moving, adjusting notes).
"""

import json
import asyncio # Import asyncio for async operations
import re # Import re for regex operations
from config import MODEL_NAME
from rag_system import retrieve_knowledge
from ableton_api_wrapper import (
    create_clip, add_notes_to_clip, set_clip_name, get_track_info,
    set_clip_quantization, set_clip_start_end, move_clip,
    update_notes_in_clip, delete_notes_from_clip, duplicate_clip, delete_clip
)
from llm_utils import get_llm_response # Import the LLM utility function

# Placeholder for Cutter/Editor Agent's system prompt (to be loaded from file)
SYSTEM_PROMPT = ""
try:
    with open("prompts/cutter_editor_system_prompt.txt", "r") as f:
        SYSTEM_PROMPT = f.read()
except FileNotFoundError:
    SYSTEM_PROMPT = "Error: Cutter/Editor system prompt file not found."

async def process_request(user_input: str, conversation_history: list, current_mode: str, initial_session_info: dict, context_knowledge: str = None) -> str:
    """
    Processes a request related to clip manipulation using an LLM.
    """
    print(f"CutterEditorSpecialistAgent: Processing request for '{user_input}' using LLM (Mode: {current_mode})...")

    # Construct the system message for the Cutter/Editor LLM, including the current mode and initial session info
    agent_system_message = f"{SYSTEM_PROMPT}\n\nCurrent Mode: {current_mode}\nInitial Ableton Session Info: {json.dumps(initial_session_info)}"

    messages_for_llm = [
        {"role": "system", "content": agent_system_message}
    ] + conversation_history + [ # Include conversation history
        {"role": "user", "content": user_input}
    ]

    try:
        llm_response_str = await get_llm_response(messages_for_llm)
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
            return f"Cutter/Editor Specialist: Clarification needed: {parsed_response.get('question')}"
        elif isinstance(parsed_response, list):
            commands_to_execute = parsed_response
        else:
            raise ValueError("LLM response is neither a list of commands nor a clarification request.")

        ableton_api_functions = {
            "create_clip": create_clip,
            "add_notes_to_clip": add_notes_to_clip,
            "set_clip_name": set_clip_name,
            "get_track_info": get_track_info,
            "set_clip_quantization": set_clip_quantization,
            "set_clip_start_end": set_clip_start_end,
            "move_clip": move_clip,
            "update_notes_in_clip": update_notes_in_clip,
            "delete_notes_from_clip": delete_notes_from_clip,
            "duplicate_clip": duplicate_clip,
            "delete_clip": delete_clip
        }

        results = []
        for command in commands_to_execute:
            cmd_type = command.get("command_type")
            params = command.get("params", {})

            if cmd_type in ableton_api_functions:
                try:
                    result = await ableton_api_functions[cmd_type](**params)
                    results.append(f"Executed {cmd_type}: {result}")
                except Exception as e:
                    results.append(f"Failed to execute {cmd_type}: {str(e)}")
            else:
                results.append(f"CutterEditorSpecialistAgent: Unknown command type '{cmd_type}' from LLM.")
        
        return "Cutter/Editor Specialist: " + "\n".join(results)

    except json.JSONDecodeError:
        return f"Cutter/Editor Specialist: LLM response was not valid JSON. Raw response: {llm_response_str}"
    except Exception as e:
        return f"Cutter/Editor Specialist: Error during LLM processing: {str(e)}"
