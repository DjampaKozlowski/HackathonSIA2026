import requests
import base64

def query_lm_studio_with_text(prompt: str) -> str:
    """
    Envoie un prompt texte seul au LLM (sans image).
    
    Args:
        prompt: Le prompt textuel à envoyer
        
    Returns:
        La réponse du LLM en texte brut
    """
    url = "http://localhost:1234/v1/chat/completions"
    
    payload = {
        "model": "google/gemma-3-12b",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.1,
        "max_tokens": 2000
    }
    
    response = requests.post(url, json=payload)
    response.raise_for_status()
    
    result = response.json()
    return result["choices"][0]["message"]["content"]