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

## Available Commands and Modes

The Abai controller supports various commands and can operate in different modes, each leveraging specialized AI agents.

### Commands

*   `set mode to [mode_name]`: Changes the active operational mode of the AI. Replace `[mode_name]` with one of the available modes listed below.
*   `save project to [path]`: Saves the current Ableton Live project to the specified `[path]`.

### Detaillierte Funktionen der MCP-Agenten

Das MCP-System ist ein KI-gesteuertes Ableton Live-Kontrollsystem, das Benutzeranfragen versteht und an spezialisierte KI-Agenten weiterleitet. Jeder Agent ist für bestimmte Aufgabenbereiche zuständig und kann präzise JSON-Befehle an Ableton Live senden.

Hier ist eine Zusammenfassung der Funktionen, aufgeteilt nach den spezialisierten Agenten:

**1. Orchestrator AI (Zentrale Steuerung):**
*   Versteht Benutzeranfragen und leitet sie an den am besten geeigneten spezialisierten Agenten weiter.
*   Stellt sicher, dass die Ausgabe immer ein JSON-Objekt mit dem gewählten Agenten und der Nachricht für diesen Agenten ist.
*   Leitet Anfragen, die keinem spezifischen Agenten zugeordnet werden können, an den `general_session_info_agent` weiter.

**2. Arrangement Specialist AI:**
*   **Strukturierung:** Hilft bei der Strukturierung musikalischer Ideen, dem Erstellen von Sektionen und dem Management des Songflusses.
*   **Clip- und Szenenmanagement:** Kann Clips, Tracks und Szenen erstellen, duplizieren, löschen und anordnen.
*   **Befehle:** `get_session_info`, `get_track_info`, `create_midi_track`, `create_audio_track`, `set_track_name`, `create_clip`, `add_notes_to_clip`, `set_clip_name`, `fire_clip`, `stop_clip`, `start_playback`, `stop_playback`, `duplicate_clip`, `delete_clip`, `move_clip`, `set_clip_loop_attributes`.

**3. Cutter/Editor Specialist AI:**
*   **Präzise Bearbeitung:** Führt präzise Manipulationen von Clips (MIDI und Audio) und Noten innerhalb von MIDI-Clips aus.
*   **Clip-Erstellung:** Kann neue MIDI-Clips erstellen und diese mit Noten basierend auf Benutzerbeschreibungen (z.B. Melodie, Rhythmus, Skala) füllen.
*   **Granulare Kontrolle:** Versteht Parameter wie Start-/Endzeiten, Dauern, Velocities und Quantisierung.
*   **Befehle:** `get_session_info`, `get_track_info`, `create_clip`, `add_notes_to_clip`, `update_notes_in_clip`, `delete_notes_from_clip`, `set_clip_name`, `set_clip_loop_attributes`, `set_clip_start_end`, `duplicate_clip`, `delete_clip`, `move_clip`, `set_clip_quantization`.

**4. General Session Info Specialist AI:**
*   **Informationsbereitstellung:** Bietet allgemeine Informationen über den aktuellen Ableton Live-Session-Status.
*   **Systemfähigkeiten:** Beschreibt die Gesamtfunktionen und verfügbaren Befehle des KI-Systems.
*   **Befehle:** `get_session_info`, `get_track_info`.

**5. Mixing Specialist AI:**
*   **Pegel- und Pan-Steuerung:** Hilft beim Einstellen von Lautstärken, Panning und Konfigurieren von Sends/Returns.
*   **Signalfluss:** Kann Return-Tracks erstellen und Send-Pegel einstellen.
*   **Sidechaining-Anleitung:** Bietet Anleitungen für Mixing-Techniken wie Sidechain-Kompression (manuelle Schritte).
*   **Befehle:** `get_session_info`, `get_track_info`, `set_track_volume`, `set_track_pan`, `create_return_track`, `set_send_level`, `load_instrument_or_effect`.

**6. Rolling Bass Specialist AI:**
*   **Psytrance Rolling Bass:** Spezialisiert auf die Erstellung von "Rolling Bass"-Mustern, insbesondere für Psytrance.
*   **Track- und Instrumenten-Setup:** Kann MIDI-Tracks erstellen, Instrumente laden, Tempo einstellen und MIDI-Clips mit spezifischen Mustern erstellen.
*   **Automatisierung & Anleitung:** Führt automatisierbare Schritte aus und gibt detaillierte Anweisungen für manuelle Schritte (z.B. Sidechaining).
*   **Befehle:** `get_session_info`, `get_track_info`, `create_midi_track`, `set_track_name`, `create_clip`, `add_notes_to_clip`, `set_clip_name`, `set_tempo`, `fire_clip`, `stop_clip`, `start_playback`, `stop_playback`, `get_browser_tree`, `get_browser_items_at_path`, `load_instrument_or_effect`, `load_drum_kit`, `create_return_track`, `set_send_level`, `set_track_volume`.

**7. Sound Design Specialist AI:**
*   **Instrumente & Effekte:** Hilft beim Laden von Instrumenten und Effekten, Anwenden von Presets und Anpassen von Parametern zur Klanggestaltung.
*   **Kreative Vorschläge:** Kann Vorschläge für Sounddesign-Techniken machen.
*   **Befehle:** `get_browser_tree`, `get_browser_items_at_path`, `load_instrument_or_effect`, `load_drum_kit`, `set_device_parameter` (hypothetisch), `get_track_info`.

**8. Track Management Agent:**
*   **Track- und Clip-Verwaltung:** Verantwortlich für das Löschen von Tracks, das Erstellen von MIDI-/Audio-Tracks, das Benennen von Tracks und das Erstellen von Clips.
*   **Befehle:** `delete_track`, `create_midi_track`, `create_audio_track`, `set_track_name`, `create_clip`.

Zusammenfassend lässt sich sagen, dass das MCP-System eine umfassende Suite von KI-Agenten bietet, die in der Lage sind, eine Vielzahl von Aufgaben in Ableton Live zu automatisieren und zu unterstützen, von der grundlegenden Session-Verwaltung über detaillierte Bearbeitung und Sounddesign bis hin zur spezialisierten Generierung von musikalischen Elementen wie Rolling Basslines.

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
