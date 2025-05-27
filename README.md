# Abai: Ableton AI Controller

Abai is an AI-powered multi-agent system designed to control and assist with music production tasks within Ableton Live. It leverages large language models (LLMs) to understand natural language commands and orchestrate various specialized AI agents to interact with Ableton Live via its API.

## Features

*   **Natural Language Control**: Interact with Ableton Live using plain English commands.
*   **Multi-Agent Architecture**: Specialized AI agents for tasks such as:
    *   Arrangement
    *   Cutting and Editing
    *   Mixing
    *   Sound Design
    *   Track Management
    *   Rolling Bass (specific task)
*   **Ableton Live Integration**: Connects directly to Ableton Live via a custom API wrapper.
*   **RAG System**: Utilizes a Retrieval-Augmented Generation (RAG) system with ChromaDB for enhanced context and knowledge.
*   **Extensible**: Easily add new agents and functionalities.

## Setup

### Prerequisites

*   **Python**: Python 3.12 or 3.13 is recommended.
*   **Ableton Live**: Ensure Ableton Live is installed and running.
*   **Ableton API**: A custom Ableton API setup is required for communication. (Details on setting this up are assumed to be external to this project, or within `ableton_api_wrapper.py`).

### Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/dancohen81/Abai.git
    cd Abai
    ```

2.  **Create a virtual environment**:
    It is highly recommended to use a virtual environment to manage dependencies.

    ```bash
    python3 -m venv .venv
    ```

3.  **Activate the virtual environment**:

    *   **On Windows**:
        ```bash
        .\.venv\Scripts\activate
        ```
    *   **On macOS/Linux**:
        ```bash
        source .venv/bin/activate
        ```

4.  **Install dependencies**:
    Use `uv pip` (as per user's global rules) or `pip` to install the required packages.

    ```bash
    uv pip install -r requirements.txt
    # Or if uv is not available:
    # pip install -r requirements.txt
    ```

5.  **Environment Variables**:
    Create a `.env` file in the root directory of the project and add your OpenAI API key (or other LLM provider API key) and any other necessary environment variables.

    ```
    OPENROUTER_API_KEY="your_api_key_here"
    # Add any other API keys or configurations here
    ```
    *Note: The project currently uses `OPENROUTER_API_KEY` as seen in `llm_utils.py` errors during initial git add output. Adjust according to your LLM provider.*

## How to Run

1.  **Ensure Ableton Live is running** and the custom API is active and accessible.
2.  **Activate your virtual environment** (if not already active).
3.  **Run the main application**:
    ```bash
    python main.py
    ```

4.  **Interact with the AI Controller**:
    Once the application starts, you can type commands in the console.
    *   Type `exit` to quit the application.
    *   Type `set mode to [new_mode]` to change the AI's operational mode.
    *   Type `save project to [path]` to save the current Ableton project.

## Running the Web Interface

To use the web-based interface for the Ableton AI Controller, you need to start both the backend API and the frontend development server.

1.  **Start the Backend API**:
    Open a new terminal in the root directory of the project (`Abai/`) and run the following command:
    ```bash
    uvicorn backend.app:app --reload
    ```
    This will start the FastAPI backend, typically on `http://127.0.0.1:8000`.

2.  **Start the Frontend Development Server**:
    Open another new terminal and navigate to the `web_interface` directory:
    ```bash
    cd web_interface
    ```
    Then, install the frontend dependencies and start the development server:
    ```bash
    npm install
    npm run dev
    ```
    This will start the Vite development server, typically on `http://localhost:5173` or `http://localhost:5174`.

3.  **Access the Web Interface**:
    Open your web browser and navigate to the URL provided by the Vite development server (e.g., `http://localhost:5174/`).

## Available Commands and Modes

The Abai controller supports various commands and can operate in different modes, each leveraging specialized AI agents.

### Commands

*   `set mode to [mode_name]`: Changes the active operational mode of the AI. Replace `[mode_name]` with one of the available modes listed below.
*   `save project to [path]`: Saves the current Ableton Live project to the specified `[path]`.

### Detailed Functions of the MCP Agents

The MCP system is an AI-driven Ableton Live control system that understands user requests and routes them to specialized AI agents. Each agent is responsible for specific task areas and can send precise JSON commands to Ableton Live.

Here is a summary of the functions, broken down by specialized agents:

**1. Orchestrator AI (Central Control):**
*   Understands user requests and routes them to the most appropriate specialized agent.
*   Ensures that the output is always a JSON object with the chosen agent and the message for that agent.
*   Routes requests that cannot be assigned to a specific agent to the `general_session_info_agent`.

**2. Arrangement Specialist AI:**
*   **Structuring:** Helps with structuring musical ideas, creating sections, and managing the overall song flow.
*   **Clip and Scene Management:** Can create, duplicate, delete, and arrange clips, tracks, and scenes.
*   **Commands:** `get_session_info`, `get_track_info`, `create_midi_track`, `create_audio_track`, `set_track_name`, `create_clip`, `add_notes_to_clip`, `set_clip_name`, `fire_clip`, `stop_clip`, `start_playback`, `stop_playback`, `duplicate_clip`, `delete_clip`, `move_clip`, `set_clip_loop_attributes`.

**3. Cutter/Editor Specialist AI:**
*   **Precise Editing:** Performs precise manipulations of clips (MIDI and Audio) and notes within MIDI clips.
*   **Clip Creation:** Can create new MIDI clips and populate them with notes based on user descriptions (e.g., melody, rhythm, scale).
*   **Granular Control:** Understands parameters such as start/end times, durations, velocities, and quantization.
*   **Commands:** `get_session_info`, `get_track_info`, `create_clip`, `add_notes_to_clip`, `update_notes_in_clip`, `delete_notes_from_clip`, `set_clip_name`, `set_clip_loop_attributes`, `set_clip_start_end`, `duplicate_clip`, `delete_clip`, `move_clip`, `set_clip_quantization`.

**4. General Session Info Specialist AI:**
*   **Information Provision:** Provides general information about the current Ableton Live session status.
*   **System Capabilities:** Describes the overall functions and available commands of the AI system.
*   **Commands:** `get_session_info`, `get_track_info`.

**5. Mixing Specialist AI:**
*   **Level and Pan Control:** Helps with setting volumes, panning, and configuring sends/returns.
*   **Signal Flow:** Can create return tracks and set send levels.
*   **Sidechaining Guidance:** Provides guidance for mixing techniques such as sidechain compression (manual steps).
*   **Commands:** `get_session_info`, `get_track_info`, `set_track_volume`, `set_track_pan`, `create_return_track`, `set_send_level`, `load_instrument_or_effect`.

**6. Rolling Bass Specialist AI:**
*   **Psytrance Rolling Bass:** Specializes in creating "Rolling Bass" patterns, particularly for Psytrance.
*   **Track and Instrument Setup:** Can create MIDI tracks, load instruments, set tempo, and create MIDI clips with specific patterns.
*   **Automation & Guidance:** Performs automatable steps and provides detailed instructions for manual steps (e.g., sidechaining).
*   **Commands:** `get_session_info`, `get_track_info`, `create_midi_track`, `set_track_name`, `create_clip`, `add_notes_to_clip`, `set_clip_name`, `set_tempo`, `fire_clip`, `stop_clip`, `start_playback`, `stop_playback`, `get_browser_tree`, `get_browser_items_at_path`, `load_instrument_or_effect`, `load_drum_kit`, `create_return_track`, `set_send_level`, `set_track_volume`.

**7. Sound Design Specialist AI:**
*   **Instruments & Effects:** Helps with loading instruments and effects, applying presets, and adjusting parameters for sound shaping.
*   **Creative Suggestions:** Can make suggestions for sound design techniques.
*   **Commands:** `get_browser_tree`, `get_browser_items_at_path`, `load_instrument_or_effect`, `load_drum_kit`, `set_device_parameter` (hypothetical), `get_track_info`.

**8. Track Management Agent:**
*   **Track and Clip Management:** Responsible for deleting tracks, creating MIDI/audio tracks, naming tracks, and creating clips.
*   **Commands:** `delete_track`, `create_midi_track`, `create_audio_track`, `set_track_name`, `create_clip`.

In summary, the MCP system offers a comprehensive suite of AI agents capable of automating and supporting a variety of tasks in Ableton Live, from basic session management to detailed editing and sound design, and specialized generation of musical elements like rolling basslines.

## Project Structure

*   `main.py`: Main entry point for the application.
*   `agents/`: Contains specialized AI agents and their logic.
*   `prompts/`: Stores system prompts for each AI agent.
*   `ableton_api_wrapper.py`: Handles communication with Ableton Live.
*   `chroma_db/`: Directory for ChromaDB persistent storage.
*   `rag_system.py`: Implements the Retrieval-Augmented Generation system.
*   `llm_utils.py`: Utility functions for interacting with LLMs.
*   `config.py`: Configuration settings for the application.
*   `utils.py`: General utility functions.
*   `requirements.txt`: Lists Python dependencies.
*   `.env`: (Ignored by Git) Stores environment variables like API keys.
