import requests
import base64

def query_lm_studio_with_image(image_bytes, prompt):
    """
    Envoie une image et un prompt au modèle gemma3:12b via l'API locale de LM Studio.
    """
    base64_image = base64.b64encode(image_bytes).decode("utf-8")
    
    payload = {
        "model": "google/gemma-3-12b",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {
                        "url": f"data:image/png;base64,{base64_image}"
                    }}
                ]
            }
        ],
        "temperature": 0.1
    }
    
    response = requests.post("http://localhost:1234/v1/chat/completions", json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]