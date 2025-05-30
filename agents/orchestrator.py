"""
orchestrator.py

The Orchestrator Agent (Router).
Analyzes user input, identifies intent, and delegates to appropriate specialized agents.
"""

import json
import asyncio # Import asyncio for async operations
from config import MODEL_NAME
from rag_system import retrieve_knowledge
from llm_utils import get_llm_response # Import the LLM utility function

# Import specialized agents
from .rolling_bass_agent import process_request as rolling_bass_agent_process_request
from .arrangement_agent import process_request as arrangement_agent_process_request
from .cutter_editor_agent import process_request as cutter_editor_agent_process_request
from .sound_design_agent import process_request as sound_design_agent_process_request
from .mixing_specialist_agent import process_request as mixing_specialist_agent_process_request
from .general_session_info_agent import process_request as general_session_info_agent_process_request
from .track_management_agent import process_request as track_management_agent_process_request

ORCHESTRATOR_SYSTEM_PROMPT = ""
try:
    with open("prompts/orchestrator_system_prompt.txt", "r") as f:
        ORCHESTRATOR_SYSTEM_PROMPT = f.read()
except FileNotFoundError:
    ORCHESTRATOR_SYSTEM_PROMPT = "Error: Orchestrator system prompt file not found."

async def route_request(user_input: str, conversation_history: list, current_mode: str, initial_session_info: dict) -> str:
    """
    Analyzes user input and routes the request to the appropriate specialized agent using an LLM.
    """
    print(f"Orchestrator: Routing request for '{user_input}' using LLM (Mode: {current_mode})...")

    # Construct the system message for the Orchestrator LLM, including the current mode and initial session info
    orchestrator_system_message = f"{ORCHESTRATOR_SYSTEM_PROMPT}\n\nCurrent Mode: {current_mode}\nInitial Ableton Session Info: {json.dumps(initial_session_info)}"

    messages_for_llm = [
        {"role": "system", "content": orchestrator_system_message}
    ] + conversation_history + [ # Include conversation history
        {"role": "user", "content": user_input}
    ]

    try:
        llm_response_str = await get_llm_response(messages_for_llm)
        # Attempt to parse the LLM's response as JSON
        llm_response_str = llm_response_str.strip()
        # Use regex to extract JSON content from markdown code block
        import re
        json_match = re.search(r"```json\s*(.*?)\s*```", llm_response_str, re.DOTALL)
        if json_match:
            json_content = json_match.group(1)
        else:
            json_content = llm_response_str # Assume it's just JSON if no markdown block

        parsed_response = json.loads(json_content)
        
        agent_name = parsed_response.get("agent")
        message_to_agent = parsed_response.get("message", user_input) # Use 'message' field from LLM response

        if agent_name == "rolling_bass_specialist_agent":
            return await rolling_bass_agent_process_request(message_to_agent, conversation_history, current_mode, initial_session_info)
        elif agent_name == "arrangement_specialist_agent":
            return await arrangement_agent_process_request(message_to_agent, conversation_history, current_mode, initial_session_info)
        elif agent_name == "cutter_editor_specialist_agent":
            return await cutter_editor_agent_process_request(message_to_agent, conversation_history, current_mode, initial_session_info)
        elif agent_name == "sound_design_specialist_agent":
            return await sound_design_agent_process_request(message_to_agent, conversation_history, current_mode, initial_session_info)
        elif agent_name == "mixing_specialist_agent":
            return await mixing_specialist_agent_process_request(message_to_agent, conversation_history, current_mode, initial_session_info)
        elif agent_name == "general_session_info_agent":
            return await general_session_info_agent_process_request(message_to_agent, conversation_history, current_mode, initial_session_info)
        elif agent_name == "track_management_agent":
            return await track_management_agent_process_request(message_to_agent, conversation_history, current_mode, initial_session_info)
        else:
            return f"Orchestrator: Unknown agent specified by LLM: {agent_name}. Please refine your request."

    except json.JSONDecodeError:
        return f"Orchestrator: LLM response was not valid JSON. Raw response: {llm_response_str}"
    except Exception as e:
        return f"Orchestrator: Error during LLM routing: {str(e)}"
