import os
import json
import logging
import asyncio
import httpx
import re
from typing import Dict, Any, List, Union
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logger = logging.getLogger("LLMUtils")

async def get_llm_response(messages: List[Dict[str, str]]) -> str:
    """Get a response from the LLM using OpenRouter."""
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    if not OPENROUTER_API_KEY:
        logger.error("OPENROUTER_API_KEY environment variable not set.")
        raise ValueError("OPENROUTER_API_KEY environment variable not set.")
    else:
        logger.info("OPENROUTER_API_KEY successfully loaded.") # Debug print

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Using Gemini Flash 2.5 as requested
    model_name = "google/gemini-flash-1.5"
    
    # Add a critical system message to reinforce execution mode
    execution_reminder = {
        "role": "system",
        "content": "CRITICAL: You are in EXECUTION MODE. Generate JSON commands that will be executed, not instructions for humans."
    }
    
    # Prepend this to messages
    messages_with_reminder = [execution_reminder] + messages
    
    payload = {
        "model": model_name,
        "messages": messages_with_reminder
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60.0 # Increased timeout for LLM response
            )
            response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
            
            response_data = response.json()
            return response_data["choices"][0]["message"]["content"]
    except httpx.RequestError as e:
        logger.error(f"An error occurred while requesting {e.request.url!r}: {e}")
        raise Exception(f"LLM request failed: {e}")
    except httpx.HTTPStatusError as e:
        logger.error(f"Error response {e.response.status_code} while requesting {e.request.url!r}: {e}")
        raise Exception(f"LLM returned an error: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during LLM interaction: {e}")
        raise Exception(f"Unexpected LLM error: {e}")
