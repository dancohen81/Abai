import json
import asyncio
import re
from config import MODEL_NAME
from rag_system import retrieve_knowledge
from llm_utils import get_llm_response
from typing import List, Dict, Union # Import for type hinting

# Import all necessary Ableton API functions
from ableton_api_wrapper import (
    create_midi_track, set_track_name, create_clip, add_notes_to_clip,
    set_clip_name, set_tempo, load_instrument_or_effect, fire_clip,
    get_session_info, set_track_volume, create_return_track, set_send_level,
    delete_track, create_audio_track, set_track_pan, load_drum_kit,
    set_device_parameter, stop_clip, start_playback, stop_playback,
    duplicate_clip, delete_clip, move_clip, set_clip_loop_attributes,
    set_clip_start_end, update_notes_in_clip, delete_notes_from_clip,
    set_clip_quantization, get_track_info, get_browser_tree, get_browser_items_at_path
)

# Centralized dictionary for all system prompts
SYSTEM_PROMPTS = {}

# Load the single super agent system prompt
try:
    with open("prompts/super_agent_system_prompt.txt", "r") as f:
        SYSTEM_PROMPTS["super_agent"] = f.read()
except FileNotFoundError:
    SYSTEM_PROMPTS["super_agent"] = "Error: Super agent system prompt file not found."

# Define all Ableton API functions available to the super agent
ABLETON_API_FUNCTIONS = {
    "create_midi_track": create_midi_track,
    "set_track_name": set_track_name,
    "create_clip": create_clip,
    "add_notes_to_clip": add_notes_to_clip,
    "set_clip_name": set_clip_name,
    "set_tempo": set_tempo,
    "load_instrument_or_effect": load_instrument_or_effect,
    "fire_clip": fire_clip,
    "get_session_info": get_session_info,
    "set_track_volume": set_track_volume,
    "create_return_track": create_return_track,
    "set_send_level": set_send_level,
    "delete_track": delete_track,
    "create_audio_track": create_audio_track,
    "set_track_pan": set_track_pan,
    "load_drum_kit": load_drum_kit,
    "set_device_parameter": set_device_parameter,
    "stop_clip": stop_clip,
    "start_playback": start_playback,
    "stop_playback": stop_playback,
    "duplicate_clip": duplicate_clip,
    "delete_clip": delete_clip,
    "move_clip": move_clip,
    "set_clip_loop_attributes": set_clip_loop_attributes,
    "set_clip_start_end": set_clip_start_end,
    "update_notes_in_clip": update_notes_in_clip,
    "delete_notes_from_clip": delete_notes_from_clip,
    "set_clip_quantization": set_clip_quantization,
    "get_track_info": get_track_info,
    "get_browser_tree": get_browser_tree,
    "get_browser_items_at_path": get_browser_items_at_path
}

async def _execute_ableton_commands(commands_to_execute: List[Dict]) -> List[str]:
    """
    Helper function to execute a list of Ableton API commands.
    """
    results = []
    last_created_track_index = None # To handle create_clip with -1 track_index

    for command in commands_to_execute:
        cmd_type = command.get("command_type")
        params = command.get("params", {})

        # Special handling for track management's create_clip with -1 track_index
        if cmd_type == "create_clip" and params.get("track_index") == -1:
            if last_created_track_index is not None:
                params["track_index"] = last_created_track_index
            else:
                results.append(f"Failed to execute {cmd_type}: Cannot create clip, no track index specified and no track was created recently.")
                continue

        if cmd_type in ABLETON_API_FUNCTIONS:
            try:
                result = await ABLETON_API_FUNCTIONS[cmd_type](**params)
                results.append(f"Executed {cmd_type}: {result}")
                if cmd_type == "create_midi_track" or cmd_type == "create_audio_track":
                    if isinstance(result, dict) and "index" in result:
                        last_created_track_index = result["index"]
                    else:
                        print(f"Warning: {cmd_type} did not return track index. Cannot infer for subsequent commands.")
            except Exception as e:
                results.append(f"Failed to execute {cmd_type}: {str(e)}")
        else:
            results.append(f"Super Agent: Unknown command type '{cmd_type}' from LLM.")
    return results

async def process_request(user_input: str, conversation_history: list, current_mode: str, initial_session_info: dict) -> str:
    """
    The Super Agent.
    Analyzes user input and processes the request directly using a single comprehensive prompt.
    """
    print(f"Super Agent: Processing request for '{user_input}' (Mode: {current_mode})...")

    # Retrieve relevant knowledge from RAG system
    retrieved_knowledge = retrieve_knowledge(user_input)
    if retrieved_knowledge:
        print(f"Super Agent: Retrieved knowledge from RAG:\n{retrieved_knowledge}")
        rag_context = f"\n\nRelevant past actions or session info from RAG:\n{retrieved_knowledge}"
    else:
        rag_context = ""

    super_agent_system_message = f"{SYSTEM_PROMPTS['super_agent']}\n\nCurrent Mode: {current_mode}\nInitial Ableton Session Info: {json.dumps(initial_session_info)}{rag_context}"

    messages_for_llm = [
        {"role": "system", "content": super_agent_system_message}
    ] + conversation_history + [
        {"role": "user", "content": user_input}
    ]

    try:
        llm_response_str = await get_llm_response(messages_for_llm)
        llm_response_str = llm_response_str.strip()
        print(f"Raw Super Agent LLM response: {llm_response_str}")
        
        json_match = re.search(r"```json\s*(.*?)\s*```", llm_response_str, re.DOTALL)
        if json_match:
            json_content = json_match.group(1)
            print(f"Extracted Super Agent JSON content: {json_content}")
        else:
            json_content = llm_response_str
            print(f"No JSON markdown block found. Using raw response as JSON: {json_content}")

        parsed_response = json.loads(json_content)

        if isinstance(parsed_response, dict) and parsed_response.get("clarification_needed"):
            return f"Super Agent: Clarification needed: {parsed_response.get('question')}"
        elif isinstance(parsed_response, list):
            commands_to_execute = []
            
            user_requested_single_track = bool(re.search(r"\ba\s+midi\s+track\b|\bone\s+midi\s+track\b|\beinen\s+neuen\s+midi\s+track\b|\beine\s+midi\s+spur\b|\beinen\s+midi\s+track\b", user_input, re.IGNORECASE))
            
            # Extract number of clips requested by the user
            clips_match = re.search(r"with\s+(\d+)\s+empty\s+clips", user_input, re.IGNORECASE)
            user_requested_clip_count = int(clips_match.group(1)) if clips_match else 0

            if user_requested_single_track:
                first_midi_track_found = False
                clips_added_to_actual_track = 0
                current_clip_index_offset = 0 # For sequential indexing on the single actual track

                for command in parsed_response:
                    if command.get("command_type") == "create_midi_track":
                        if not first_midi_track_found:
                            commands_to_execute.append(command)
                            first_midi_track_found = True
                        else:
                            print(f"Warning: User requested a single MIDI track, but LLM generated multiple 'create_midi_track' commands. Skipping subsequent ones.")
                    elif command.get("command_type") == "create_clip":
                        if first_midi_track_found and clips_added_to_actual_track < user_requested_clip_count:
                            modified_command = command.copy()
                            modified_command["params"]["track_index"] = -1 # Route to the single created track
                            modified_command["params"]["clip_index"] = current_clip_index_offset
                            current_clip_index_offset += 1
                            commands_to_execute.append(modified_command)
                            clips_added_to_actual_track += 1
                        else:
                            print(f"Warning: Skipping extra 'create_clip' command as user requested {user_requested_clip_count} clips for a single track.")
                    else:
                        commands_to_execute.append(command)
            else:
                commands_to_execute = parsed_response # If not a single track request, process all commands as is
            
            results = await _execute_ableton_commands(commands_to_execute)
            return "Super Agent: " + "\n".join(results)
        else:
            raise ValueError("LLM response is neither a list of commands nor a clarification request.")

    except json.JSONDecodeError:
        return f"Super Agent: LLM response was not valid JSON. Raw response: {llm_response_str}"
    except Exception as e:
        return f"Super Agent: Error during LLM processing: {str(e)}"
