
import os
import requests
from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434/api/chat"
)


def get_ai_response(history, memories):

    memory_text = "\n".join(
        [f"- {item['fact']}" for item in memories]
    )

    if not memory_text:
        memory_text = "No saved personal memories yet."

    # Keep only recent conversation messages
    history = history[-6:]

    system_prompt = f"""
You are LifeOS, a personal AI assistant.

PERSONAL MEMORY:
{memory_text}

IMPORTANT RULES:
- Never invent personal facts, work experience, projects, or achievements.
- A task marked completed only means that task's status is completed.
- Never assume a project was submitted, reviewed, or fully delivered.
- Never invent resume details, names, emails, phone numbers, or links.
- If information is missing, ask the user.
- Be friendly and concise.
- Use simple English.
"""

    messages = [
        {"role": "system", "content": system_prompt}
    ]

    messages.extend(history)

    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "keep_alive": "10m",
        "options": {
            "temperature": 0.2,
            "num_predict": 120,
            "num_ctx": 2048
        }
    }

    try:

        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=180
        )

        response.raise_for_status()

        return response.json()["message"]["content"]

    except requests.exceptions.Timeout:
        return (
            "Sorry, my local AI model is taking too long to respond. "
            "Please try again with a shorter message."
        )

    except requests.exceptions.RequestException as error:
        print("Ollama connection error:", error)
        return "My AI brain is temporarily unavailable. Please try again."

    except (KeyError, ValueError) as error:
        print("AI response parsing error:", error)
        return "I couldn't process that response. Please try again."
