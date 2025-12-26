"""
Streaming Response Example for GaiaRouter API

This example demonstrates how to use Server-Sent Events (SSE)
to receive streaming responses from the GaiaRouter API.
"""

import json
import os

import httpx

# Configuration
API_BASE_URL = "http://localhost:8000"
API_KEY = os.getenv("GAIAROUTER_API_KEY", "your-api-key-here")


def streaming_chat_completion():
    """Make a streaming chat completion request"""

    url = f"{API_BASE_URL}/v1/chat/completions"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

    payload = {
        "model": "openrouter/anthropic/claude-3.5-sonnet",
        "messages": [{"role": "user", "content": "Write a short poem about AI."}],
        "stream": True,
        "temperature": 0.8,
    }

    print("Streaming response:")
    print("-" * 60)

    with httpx.stream("POST", url, json=payload, headers=headers, timeout=30.0) as response:
        if response.status_code == 200:
            for line in response.iter_lines():
                if line.startswith("data: "):
                    data = line[6:]  # Remove "data: " prefix

                    if data == "[DONE]":
                        break

                    try:
                        chunk = json.loads(data)
                        delta = chunk["choices"][0]["delta"]

                        if "content" in delta:
                            print(delta["content"], end="", flush=True)
                    except json.JSONDecodeError:
                        continue

            print("\n" + "-" * 60)
        else:
            print(f"Error: {response.status_code}")
            print(response.text)


if __name__ == "__main__":
    streaming_chat_completion()
