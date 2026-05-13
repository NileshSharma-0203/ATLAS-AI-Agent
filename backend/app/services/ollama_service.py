import httpx


OLLAMA_URL = "http://localhost:11434/api/chat"


async def chat_completion(messages: list[dict]):
    payload = {
        "model": "phi3",
        "messages": messages,
        "stream": False,
    }

    async with httpx.AsyncClient(timeout=45.0) as client:
        response = await client.post(
            OLLAMA_URL,
            json=payload
        )

    response.raise_for_status()

    data = response.json()

    return data["message"]["content"]