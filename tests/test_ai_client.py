from ai_client import MODEL, OLLAMA_URL


def test_model_configuration():
    assert MODEL == "qwen2.5:3b"


def test_ollama_url():
    assert OLLAMA_URL == "http://localhost:11434/api/generate"
