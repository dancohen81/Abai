"""
sound_design_agent.py

Specialized agent for sound design tasks (instrument/effect loading, parameter automation).
"""

import json
import asyncio # Import asyncio for async operations
from config import MODEL_NAME
from rag_system import retrieve_knowledge
from ableton_api_wrapper import (
    load_instrument_or_effect, load_drum_kit, set_device_parameter, get_track_info
)
from llm_utils import get_llm_response # Import the LLM utility function

# Placeholder for Sound Design Agent's system prompt (to be loaded from file)
SYSTEM_PROMPT = ""
try:
    with open("ableton_ai_controller/prompts/sound_design_system_prompt.txt", "r") as f:
        SYSTEM_PROMPT = f.read()
except FileNotFoundError:
    SYSTEM_PROMPT = "Error: Sound Design system prompt file not found."

async def process_request(user_input: str, conversation_history: list, current_mode: str, initial_session_info: dict, context_knowledge: str = None) -> str:
    """
    Processes a request related to sound design using an LLM.
    """
    print(f"SoundDesignSpecialistAgent: Processing request for '{user_input}' using LLM (Mode: {current_mode})...")

    # Construct the system message for the Sound Design LLM, including the current mode and initial session info
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
            return f"Sound Design Specialist: Clarification needed: {parsed_response.get('question')}"
        elif isinstance(parsed_response, list):
            commands_to_execute = parsed_response
        else:
            raise ValueError("LLM response is neither a list of commands nor a clarification request.")

        ableton_api_functions = {
            "load_instrument_or_effect": load_instrument_or_effect,
            "load_drum_kit": load_drum_kit,
            "set_device_parameter": set_device_parameter,
            "get_track_info": get_track_info
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
                results.append(f"SoundDesignSpecialistAgent: Unknown command type '{cmd_type}' from LLM.")
        
        return "Sound Design Specialist: " + "\n".join(results)

    except json.JSONDecodeError:
        return f"Sound Design Specialist: LLM response was not valid JSON. Raw response: {llm_response_str}"
    except Exception as e:
        return f"Sound Design Specialist: Error during LLM processing: {str(e)}"
