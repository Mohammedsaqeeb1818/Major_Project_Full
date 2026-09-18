
import requests
import json


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:1.5b"


def stream_qwen(prompt):

    try:

        response = requests.post(
            OLLAMA_URL,

            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": True,

                "options": {
                    "temperature": 0.2,
                    "num_predict": 150
                }
            },

            stream=True,
            timeout=180
        )

        response.raise_for_status()

        for line in response.iter_lines():

            if line:

                data = json.loads(line)

                chunk = data.get(
                    "response",
                    ""
                )

                if chunk:
                    yield chunk

                if data.get("done"):
                    break

    except requests.exceptions.RequestException as e:

        print("Qwen Error:", e)

        yield "\nAI explanation unavailable."