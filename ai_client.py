
import httpx
import json

MODEL = "qwen2.5:3b"
OLLAMA_URL = "http://localhost:11434/api/generate"


# Existing function for CLI - keep it working
def generate_response(prompt):
    data = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }

    response = httpx.post(
        OLLAMA_URL,
        json=data,
        timeout=120.0
    )

    response.raise_for_status()

    result = response.json()
    return result["response"]


# New function for Web - streaming response
def stream_response(prompt):
    data = {
        "model": MODEL,
        "prompt": prompt,
        "stream": True
    }

    with httpx.stream(
        "POST",
        OLLAMA_URL,
        json=data,
        timeout=120.0
    ) as response:

        response.raise_for_status()

        for line in response.iter_lines():
            if not line:
                continue

            result = json.loads(line)

            if "error" in result:
                raise RuntimeError(result["error"])

            if "response" in result:
                yield result["response"]

            if result.get("done"):
                break
