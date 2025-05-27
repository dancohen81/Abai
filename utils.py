import json
import os
from typing import Dict, Any

TEMP_DIR = "ableton_ai_controller/temp"
SESSION_METADATA_FILE = os.path.join(TEMP_DIR, "session_metadata.json")

def update_session_metadata(session_info: Dict[str, Any]):
    """
    Writes the current Ableton session information to a temporary JSON file.
    """
    os.makedirs(TEMP_DIR, exist_ok=True)
    with open(SESSION_METADATA_FILE, "w") as f:
        json.dump(session_info, f, indent=4)
    print(f"Session metadata updated in {SESSION_METADATA_FILE}")

def get_session_metadata() -> Dict[str, Any]:
    """
    Reads the Ableton session information from the temporary JSON file.
    Returns an empty dictionary if the file does not exist.
    """
    if os.path.exists(SESSION_METADATA_FILE):
        with open(SESSION_METADATA_FILE, "r") as f:
            return json.load(f)
    return {}
