"""
config.py

Configuration settings for the Ableton AI Controller application.
Includes API keys, model names, and other global settings.
"""

import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_openai_api_key_here")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o") # Default model name
OPENROUTER_API_KEY="sk-or-v1-3d138fd8fa47ff1a3ec0729a6d6eed41d9717b517c59ec37b24019754c5bd1f"
# Add any other API keys or configurations here