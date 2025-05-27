"""
ableton_api_wrapper.py

Provides actual interaction with Ableton Live's API via socket connection.
"""

import socket
import json
import logging
import asyncio # Import asyncio
from dataclasses import dataclass
from typing import List, Dict, Any, Union

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AbletonAPIWrapper")

@dataclass
class AbletonConnection:
    host: str
    port: int
    sock: socket.socket = None

    def connect(self) -> bool:
        """Connect to the Ableton Remote Script socket server"""
        if self.sock:
            return True

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            logger.info(f"Connected to Ableton at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Ableton: {str(e)}")
            self.sock = None
            return False

    def disconnect(self):
        """Disconnect from the Ableton Remote Script"""
        if self.sock:
            try:
                self.sock.close()
            except Exception as e:
                logger.error(f"Error disconnecting from Ableton: {str(e)}")
            finally:
                self.sock = None

    def receive_full_response(self, sock, buffer_size=8192):
        """Receive the complete response, potentially in multiple chunks"""
        chunks = []
        sock.settimeout(15.0)  # Increased timeout for operations that might take longer

        try:
            while True:
                try:
                    chunk = sock.recv(buffer_size)
                    if not chunk:
                        if not chunks:
                            raise Exception("Connection closed before receiving any data")
                        break

                    chunks.append(chunk)

                    # Check if we've received a complete JSON object
                    try:
                        data = b''.join(chunks)
                        json.loads(data.decode('utf-8'))
                        logger.info(f"Received complete response ({len(data)} bytes)")
                        return data
                    except json.JSONDecodeError:
                        # Incomplete JSON, continue receiving
                        continue
                except socket.timeout:
                    logger.warning("Socket timeout during chunked receive")
                    break
                except (ConnectionError, BrokenPipeError, ConnectionResetError) as e:
                    logger.error(f"Socket connection error during receive: {str(e)}")
                    raise
        except Exception as e:
            logger.error(f"Error during receive: {str(e)}")
            raise

        # If we get here, we either timed out or broke out of the loop
        if chunks:
            data = b''.join(chunks)
            logger.info(f"Returning data after receive completion ({len(data)} bytes)")
            try:
                json.loads(data.decode('utf-8'))
                return data
            except json.JSONDecodeError:
                raise Exception("Incomplete JSON response received")
        else:
            raise Exception("No data received")

    async def send_command(self, command_type: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a command to Ableton and return the response"""
        if not self.sock and not self.connect():
            raise ConnectionError("Not connected to Ableton")

        command = {
            "type": command_type,
            "params": params or {}
        }

        # Check if this is a state-modifying command
        is_modifying_command = command_type in [
            "create_midi_track", "create_audio_track", "set_track_name",
            "create_clip", "add_notes_to_clip", "set_clip_name",
            "set_tempo", "fire_clip", "stop_clip", "set_device_parameter",
            "start_playback", "stop_playback", "load_instrument_or_effect",
            "create_return_track", "set_send_level", "set_track_volume",
            "set_track_pan", "duplicate_clip", "delete_clip", "move_clip",
            "set_clip_loop_attributes", "set_clip_start_end", "set_clip_quantization",
            "update_notes_in_clip", "delete_notes_from_clip", "delete_track",
            "save_project"
        ]

        try:
            logger.info(f"Sending command: {command_type} with params: {params}")

            # Send the command
            self.sock.sendall(json.dumps(command).encode('utf-8'))
            logger.info(f"Command sent, waiting for response...")

            # For state-modifying commands, add a small delay to give Ableton time to process
            if is_modifying_command:
                await asyncio.sleep(0.1)  # 100ms delay

            # Set timeout based on command type
            timeout = 15.0 if is_modifying_command else 10.0
            self.sock.settimeout(timeout)

            # Receive the response
            response_data = self.receive_full_response(self.sock)
            logger.info(f"Received {len(response_data)} bytes of data")

            # Parse the response
            response = json.loads(response_data.decode('utf-8'))
            logger.info(f"Response parsed, status: {response.get('status', 'unknown')}")

            if response.get("status") == "error":
                logger.error(f"Ableton error: {response.get('message')}")
                raise Exception(response.get("message", "Unknown error from Ableton"))

            # For state-modifying commands, add another small delay after receiving response
            if is_modifying_command:
                await asyncio.sleep(0.1)  # 100ms delay

            return response.get("result", {})
        except socket.timeout:
            logger.error("Socket timeout while waiting for response from Ableton")
            self.sock = None
            raise Exception("Timeout waiting for Ableton response")
        except (ConnectionError, BrokenPipeError, ConnectionResetError) as e:
            logger.error(f"Socket connection error: {str(e)}")
            self.sock = None
            raise Exception(f"Connection to Ableton lost: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from Ableton: {str(e)}")
            if 'response_data' in locals() and response_data:
                logger.error(f"Raw response (first 200 bytes): {response_data[:200]}")
            self.sock = None
            raise Exception(f"Invalid response from Ableton: {str(e)}")
        except Exception as e:
            logger.error(f"Error communicating with Ableton: {str(e)}")
            self.sock = None
            raise Exception(f"Communication error with Ableton: {str(e)}")

# Global Ableton connection instance
ableton_connection = AbletonConnection(host="localhost", port=9877)

# Wrapper functions for Ableton API commands
async def get_session_info():
    """Get detailed information about the current Ableton session."""
    return await ableton_connection.send_command("get_session_info")

async def get_track_info(track_index: int):
    """Get detailed information about a specific track."""
    return await ableton_connection.send_command("get_track_info", {"track_index": track_index})

async def create_midi_track(index: int = -1):
    """Create a new MIDI track."""
    return await ableton_connection.send_command("create_midi_track", {"index": index})

async def set_track_name(track_index: int, name: str):
    """Set the name of a track."""
    return await ableton_connection.send_command("set_track_name", {"track_index": track_index, "name": name})

async def create_clip(track_index: int, clip_index: int, length: float = 4.0):
    """Create a new MIDI clip."""
    return await ableton_connection.send_command("create_clip", {"track_index": track_index, "clip_index": clip_index, "length": length})

async def add_notes_to_clip(track_index: int, clip_index: int, notes: List[Dict[str, Union[int, float, bool]]]):
    """Add MIDI notes to a clip."""
    return await ableton_connection.send_command("add_notes_to_clip", {"track_index": track_index, "clip_index": clip_index, "notes": notes})

async def set_clip_name(track_index: int, clip_index: int, name: str):
    """Set the name of a clip."""
    return await ableton_connection.send_command("set_clip_name", {"track_index": track_index, "clip_index": clip_index, "name": name})

async def set_tempo(tempo: float):
    """Set the tempo of the Ableton session."""
    return await ableton_connection.send_command("set_tempo", {"tempo": tempo})

async def fire_clip(track_index: int, clip_index: int):
    """Start playing a clip."""
    return await ableton_connection.send_command("fire_clip", {"track_index": track_index, "clip_index": clip_index})

async def stop_clip(track_index: int, clip_index: int):
    """Stop playing a clip."""
    return await ableton_connection.send_command("stop_clip", {"track_index": track_index, "clip_index": clip_index})

async def start_playback():
    """Start playing the Ableton session."""
    return await ableton_connection.send_command("start_playback")

async def stop_playback():
    """Stop playing the Ableton session."""
    return await ableton_connection.send_command("stop_playback")

async def get_browser_tree(category_type: str = "all"):
    """Get a hierarchical tree of browser categories from Ableton."""
    return await ableton_connection.send_command("get_browser_tree", {"category_type": category_type})

async def get_browser_items_at_path(path: str):
    """Get browser items at a specific path in Ableton's browser."""
    return await ableton_connection.send_command("get_browser_items_at_path", {"path": path})

async def load_instrument_or_effect(track_index: int, uri: str):
    """Load an instrument or effect onto a track using its URI."""
    return await ableton_connection.send_command("load_instrument_or_effect", {"track_index": track_index, "uri": uri})

async def load_drum_kit(track_index: int, rack_uri: str, kit_path: str):
    """Load a drum rack and then load a specific drum kit into it."""
    return await ableton_connection.send_command("load_drum_kit", {"track_index": track_index, "rack_uri": rack_uri, "kit_path": kit_path})

async def create_return_track(index: int = -1):
    """Create a new return track."""
    return await ableton_connection.send_command("create_return_track", {"index": index})

async def set_send_level(source_track_index: int, destination_return_track_index: int, level: float):
    """Set the send level from a track to a return track."""
    return await ableton_connection.send_command("set_send_level", {"source_track_index": source_track_index, "destination_return_track_index": destination_return_track_index, "level": level})

async def set_track_volume(track_index: int, volume: float):
    """Set the volume of a track."""
    return await ableton_connection.send_command("set_track_volume", {"track_index": track_index, "volume": volume})

# New commands from prompt files (if not already in the list)
# These were identified from the prompt files, and need to be added to the send_command's is_modifying_command list
# set_track_pan
async def set_track_pan(track_index: int, pan: float):
    """Set the pan of a track."""
    return await ableton_connection.send_command("set_track_pan", {"track_index": track_index, "pan": pan})

# update_notes_in_clip (hypothetical, as noted in prompt)
async def update_notes_in_clip(track_index: int, clip_index: int, updates: List[Dict[str, Union[int, float, bool]]]):
    """Modify existing notes in a clip."""
    logger.warning("update_notes_in_clip is a hypothetical command and may not be directly supported by Ableton API.")
    return await ableton_connection.send_command("update_notes_in_clip", {"track_index": track_index, "clip_index": clip_index, "updates": updates})

# delete_notes_from_clip (hypothetical, as noted in prompt)
async def delete_notes_from_clip(track_index: int, clip_index: int, note_indices: List[int]):
    """Delete specific notes from a clip by their index."""
    logger.warning("delete_notes_from_clip is a hypothetical command and may not be directly supported by Ableton API.")
    return await ableton_connection.send_command("delete_notes_from_clip", {"track_index": track_index, "clip_index": clip_index, "note_indices": note_indices})

# set_device_parameter (hypothetical, as noted in prompt)
async def set_device_parameter(track_index: int, device_index: int, parameter_name: str, value: float):
    """Set a parameter of a device."""
    logger.warning("set_device_parameter is a hypothetical command and may not be directly supported by Ableton API.")
    return await ableton_connection.send_command("set_device_parameter", {"track_index": track_index, "device_index": device_index, "parameter_name": parameter_name, "value": value})

# duplicate_clip
async def duplicate_clip(track_index: int, clip_index: int, target_track_index: int = None, target_clip_index: int = None):
    """Duplicates a clip."""
    params = {"track_index": track_index, "clip_index": clip_index}
    if target_track_index is not None:
        params["target_track_index"] = target_track_index
    if target_clip_index is not None:
        params["target_clip_index"] = target_clip_index
    return await ableton_connection.send_command("duplicate_clip", params)

# delete_clip
async def delete_clip(track_index: int, clip_index: int):
    """Deletes a clip."""
    return await ableton_connection.send_command("delete_clip", {"track_index": track_index, "clip_index": clip_index})

# move_clip
async def move_clip(track_index: int, clip_index: int, new_start_time: float):
    """Moves a clip to a new start time on the same track."""
    return await ableton_connection.send_command("move_clip", {"track_index": track_index, "clip_index": clip_index, "new_start_time": new_start_time})

# set_clip_loop_attributes
async def set_clip_loop_attributes(track_index: int, clip_index: int, loop_start: float, loop_end: float, loop_enabled: bool):
    """Sets loop points for a clip."""
    return await ableton_connection.send_command("set_clip_loop_attributes", {"track_index": track_index, "clip_index": clip_index, "loop_start": loop_start, "loop_end": loop_end, "loop_enabled": loop_enabled})

# set_clip_start_end
async def set_clip_start_end(track_index: int, clip_index: int, start_time: float, end_time: float):
    """Adjusts the start and end point of a clip."""
    return await ableton_connection.send_command("set_clip_start_end", {"track_index": track_index, "clip_index": clip_index, "start_time": start_time, "end_time": end_time})

# set_clip_quantization
async def set_clip_quantization(track_index: int, clip_index: int, quantization_value: float):
    """Quantizes notes within a clip."""
    return await ableton_connection.send_command("set_clip_quantization", {"track_index": track_index, "clip_index": clip_index, "quantization_value": quantization_value})

# create_audio_track (from arrangement prompt)
async def create_audio_track(index: int = -1):
    """Create a new audio track."""
    return await ableton_connection.send_command("create_audio_track", {"index": index})

async def delete_track(track_index: int):
    """Delete a track."""
    return await ableton_connection.send_command("delete_track", {"track_index": track_index})

async def save_project(path: str):
    """Save the current Ableton Live project to a specified path."""
    return await ableton_connection.send_command("save_project", {"path": path})
