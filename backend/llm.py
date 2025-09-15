# Example wrapper for local LLM (Llama.cpp)
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

class LocalLLM:
    def __init__(self, model="mistral"):
        self.model = model

    def ask(self, prompt: str) -> str:
        response = requests.post(OLLAMA_URL, json={
            "model": self.model,
            "prompt": prompt,
            "stream": False
        })
        response.raise_for_status()
        return response.json()["response"].strip()
