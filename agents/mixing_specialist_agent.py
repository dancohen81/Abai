"""
mixing_specialist_agent.py

Specialized agent for mixing tasks (volume, panning, sends).
"""

import json
import asyncio # Import asyncio for async operations
from config import MODEL_NAME
from rag_system import retrieve_knowledge
from ableton_api_wrapper import (
    set_track_volume, set_send_level, set_track_pan,
)
import asyncio # Import asyncio for async operations
from llm_utils import get_llm_response # Import the LLM utility function

# Placeholder for Mixing Specialist Agent's system prompt (to be loaded from file)
SYSTEM_PROMPT = ""
try:
    with open("ableton_ai_controller/prompts/mixing_specialist_system_prompt.txt", "r") as f:
        SYSTEM_PROMPT = f.read()
except FileNotFoundError:
    SYSTEM_PROMPT = "Error: Mixing Specialist system prompt file not found."

async def process_request(user_input: str, conversation_history: list, current_mode: str, initial_session_info: dict, context_knowledge: str = None) -> str:
    """
    Processes a request related to mixing using an LLM.
    """
    print(f"MixingSpecialistAgent: Processing request for '{user_input}' using LLM (Mode: {current_mode})...")

    # Construct the system message for the Mixing Specialist LLM, including the current mode and initial session info
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
        if llm_response_str.startswith("```json") and llm_response_str.endswith("```"):
            llm_response_str = llm_response_str[7:-3].strip()
        
        parsed_response = json.loads(llm_response_str)

        if isinstance(parsed_response, dict) and parsed_response.get("clarification_needed"):
            return f"Mixing Specialist: Clarification needed: {parsed_response.get('question')}"
        elif isinstance(parsed_response, list):
            commands_to_execute = parsed_response
        else:
            raise ValueError("LLM response is neither a list of commands nor a clarification request.")

        ableton_api_functions = {
            "set_track_volume": set_track_volume,
            "set_send_level": set_send_level,
            "set_track_pan": set_track_pan,
            "create_return_track": create_return_track,
            "set_track_name": set_track_name,
            "load_instrument_or_effect": load_instrument_or_effect
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
                results.append(f"MixingSpecialistAgent: Unknown command type '{cmd_type}' from LLM.")
        
        return "Mixing Specialist: " + "\n".join(results)

    except json.JSONDecodeError:
        return f"Mixing Specialist: LLM response was not valid JSON. Raw response: {llm_response_str}"
    except Exception as e:
        return f"Mixing Specialist: Error during LLM processing: {str(e)}"
