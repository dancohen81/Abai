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
