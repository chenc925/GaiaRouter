"""
Basic Usage Example for GaiaRouter API

This example demonstrates how to make a simple chat completion request
to the GaiaRouter API.
"""

import os

import httpx

# Configuration
API_BASE_URL = "http://localhost:8000"
API_KEY = os.getenv("GAIAROUTER_API_KEY", "your-api-key-here")


def basic_chat_completion():
    """Make a basic chat completion request"""

    url = f"{API_BASE_URL}/v1/chat/completions"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

    payload = {
        "model": "openrouter/anthropic/claude-3.5-sonnet",
        "messages": [{"role": "user", "content": "What is the capital of France?"}],
        "temperature": 0.7,
        "max_tokens": 100,
    }

    response = httpx.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        result = response.json()
        print("Response:")
        print(result["choices"][0]["message"]["content"])
    else:
        print(f"Error: {response.status_code}")
        print(response.text)


if __name__ == "__main__":
    basic_chat_completion()
