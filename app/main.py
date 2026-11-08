
import os
import hmac
import requests

from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Query
from fastapi.responses import PlainTextResponse, FileResponse
from pydantic import BaseModel

from app.agent_graph import run_lifeos_graph

from app.memory import (
    init_db,
    get_memories,
    delete_memory,
    get_tasks,
    get_execution_logs
)

load_dotenv()

app = FastAPI(
    title="LifeOS",
    description="Your Personal Agentic AI Assistant",
    version="1.5.0"
)

init_db()

BASE_DIR = Path(__file__).resolve().parent

WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")
WHATSAPP_API_VERSION = os.getenv("WHATSAPP_API_VERSION", "v25.0")


class ChatRequest(BaseModel):
    message: str


class MemoryDeleteRequest(BaseModel):
    fact: str


# --------------------------------
# MESSAGE PROCESSING
# --------------------------------

def process_message(message: str):

    message = message.strip()

    if not message:
        return "Please send a message."

    reply = run_lifeos_graph(message)

    print("LifeOS graph execution completed.")

    return reply


# --------------------------------
# HOME
# --------------------------------

@app.get("/")
def home():

    return {
        "status": "online",
        "assistant": "LifeOS",
        "version": "1.5.0"
    }


# --------------------------------
# DASHBOARD
# --------------------------------

@app.get("/dashboard")
def dashboard():

    dashboard_file = BASE_DIR / "dashboard.html"

    if not dashboard_file.exists():
        return {
            "error": "Dashboard file not found."
        }

    return FileResponse(
        dashboard_file,
        media_type="text/html"
    )


# --------------------------------
# CHAT API
# --------------------------------

@app.post("/chat")
def chat(request: ChatRequest):

    reply = process_message(request.message)

    return {"reply": reply}


# --------------------------------
# MEMORY APIs
# --------------------------------

@app.get("/memories")
def view_memories():

    memories = get_memories()

    return {
        "total": len(memories),
        "memories": memories
    }


@app.delete("/memories")
def remove_memory(request: MemoryDeleteRequest):

    fact = request.fact.strip()

    if not fact:
        return {
            "success": False,
            "message": "Memory fact cannot be empty."
        }

    deleted = delete_memory(fact)

    if deleted:
        return {
            "success": True,
            "message": "Memory deleted successfully.",
            "deleted_fact": fact
        }

    return {
        "success": False,
        "message": "Memory not found."
    }


# --------------------------------
# TASK API
# --------------------------------

@app.get("/tasks")
def view_tasks():

    tasks = get_tasks()

    return {
        "total": len(tasks),
        "tasks": tasks
    }


# --------------------------------
# EXECUTION LOG API
# --------------------------------

@app.get("/logs")
def view_execution_logs(
    limit: int = Query(default=50, ge=1, le=200)
):

    logs = get_execution_logs(limit)

    return {
        "total": len(logs),
        "logs": logs
    }


# --------------------------------
# WHATSAPP WEBHOOK VERIFICATION
# --------------------------------

@app.get("/webhook")
def verify_webhook(
    mode: str = Query(default="", alias="hub.mode"),
    token: str = Query(default="", alias="hub.verify_token"),
    challenge: str = Query(default="", alias="hub.challenge")
):

    if (
        mode == "subscribe"
        and WHATSAPP_VERIFY_TOKEN
        and hmac.compare_digest(token, WHATSAPP_VERIFY_TOKEN)
    ):
        return PlainTextResponse(content=challenge)

    return PlainTextResponse(
        content="Verification failed",
        status_code=403
    )


# --------------------------------
# SEND WHATSAPP MESSAGE
# --------------------------------

def send_whatsapp_message(to, message):

    if not WHATSAPP_ACCESS_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
        print("WhatsApp credentials are missing in .env")
        return False

    url = (
        f"https://graph.facebook.com/"
        f"{WHATSAPP_API_VERSION}/"
        f"{WHATSAPP_PHONE_NUMBER_ID}/messages"
    )

    headers = {
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }

    try:

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )

        response.raise_for_status()

        print("WhatsApp reply sent successfully.")

        return True

    except requests.exceptions.RequestException as error:

        print("WhatsApp sending error:", error)

        if error.response is not None:
            print("Meta API error details:", error.response.text)

        return False


# --------------------------------
# RECEIVE WHATSAPP MESSAGES
# --------------------------------

@app.post("/webhook")
def receive_whatsapp_message(payload: dict):

    for entry in payload.get("entry", []):

        for change in entry.get("changes", []):

            value = change.get("value", {})
            messages = value.get("messages", [])

            for message in messages:

                sender = message.get("from")

                if not sender:
                    continue

                if message.get("type") != "text":

                    reply = (
                        "For now, I can understand text messages. "
                        "Voice support is coming soon."
                    )

                else:

                    incoming_text = message.get(
                        "text", {}
                    ).get("body", "")

                    if not incoming_text.strip():
                        continue

                    print(
                        "Incoming WhatsApp message:",
                        incoming_text
                    )

                    try:

                        reply = process_message(incoming_text)

                    except Exception as error:

                        print("LifeOS processing error:", error)

                        reply = (
                            "Sorry, something went wrong while "
                            "processing your request. Please try again."
                        )

                send_whatsapp_message(sender, reply)

    return {"status": "EVENT_RECEIVED"}
