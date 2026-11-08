
import time
from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from app.ai_brain import get_ai_response

from app.memory import (
    save_message,
    get_history,
    get_memories,
    save_memory,
    create_task,
    get_tasks,
    complete_task,
    delete_task,
    save_execution_log
)


class LifeOSState(TypedDict):
    message: str
    intent: str
    response: str
    action: str


# --------------------------------
# MESSAGE CLASSIFICATION
# --------------------------------

def detect_intent(message: str):
    message = message.strip().lower()

    if message.startswith((
        "add task:",
        "show my tasks",
        "show tasks",
        "my tasks",
        "complete task:",
        "delete task:"
    )):
        return "task"

    elif message.startswith((
        "remember:",
        "remember personal:",
        "remember career:",
        "remember preference:",
        "remember project:",
        "remember goal:"
    )):
        return "memory"

    return "chat"


# --------------------------------
# SUPERVISOR AGENT
# --------------------------------

def supervisor_agent(state: LifeOSState):

    intent = detect_intent(state["message"])

    print(f"Supervisor selected: {intent}")

    return {"intent": intent}


# --------------------------------
# TASK AGENT
# --------------------------------

def task_agent(state: LifeOSState):

    message = state["message"].strip()
    lower_message = message.lower()

    action = "unknown_task_action"

    if lower_message.startswith("add task:"):

        action = "create_task"

        title = message[len("add task:"):].strip()

        if not title:
            reply = "Please provide a task title."
        else:
            task_id = create_task(title)

            reply = (
                f"Task created successfully!\n"
                f"Task ID: {task_id}\n"
                f"Title: {title}\n"
                f"Status: Pending"
            )

    elif lower_message in ("show my tasks", "show tasks", "my tasks"):

        action = "list_tasks"

        tasks = get_tasks()

        if not tasks:
            reply = "You don't have any tasks yet."
        else:
            lines = ["Here are your tasks:\n"]

            for task in tasks:
                lines.append(
                    f"ID: {task['id']}\n"
                    f"Task: {task['title']}\n"
                    f"Status: {task['status']}\n"
                )

            reply = "\n".join(lines)

    elif lower_message.startswith("complete task:"):

        action = "complete_task"

        task_id_text = message[len("complete task:"):].strip()

        if not task_id_text.isdigit():
            reply = "Please provide a valid task ID."
        else:
            task_id = int(task_id_text)

            if complete_task(task_id):
                reply = f"Task {task_id} marked as completed!"
            else:
                reply = f"Task {task_id} was not found."

    elif lower_message.startswith("delete task:"):

        action = "delete_task"

        task_id_text = message[len("delete task:"):].strip()

        if not task_id_text.isdigit():
            reply = "Please provide a valid task ID."
        else:
            task_id = int(task_id_text)

            if delete_task(task_id):
                reply = f"Task {task_id} deleted successfully."
            else:
                reply = f"Task {task_id} was not found."

    else:
        reply = "I couldn't understand that task command."

    save_message("user", message)
    save_message("assistant", reply)

    print("Task Agent executed successfully.")

    return {
        "response": reply,
        "action": action
    }


# --------------------------------
# MEMORY AGENT
# --------------------------------

def memory_agent(state: LifeOSState):

    message = state["message"].strip()
    parts = message.split(":", 1)

    action = "save_memory"

    if len(parts) != 2:
        reply = "Please use Remember: your personal fact."
        action = "validate_memory"

    else:
        command = parts[0].strip().lower()
        fact = parts[1].strip()

        if command == "remember":
            category = "personal"
        else:
            category = command[len("remember "):].strip()

        allowed_categories = (
            "personal",
            "career",
            "preference",
            "project",
            "goal"
        )

        if category not in allowed_categories:
            reply = (
                "Invalid category. Use: personal, career, "
                "preference, project, or goal."
            )
            action = "validate_memory"

        elif not fact:
            reply = "Please tell me what you want me to remember."
            action = "validate_memory"

        else:
            save_memory(category, fact)
            reply = f"Saved successfully under {category}: {fact}"

    save_message("user", message)
    save_message("assistant", reply)

    print("Memory Agent executed successfully.")

    return {
        "response": reply,
        "action": action
    }


# --------------------------------
# CHAT AGENT
# --------------------------------

def chat_agent(state: LifeOSState):

    message = state["message"].strip()

    history = get_history(limit=6)

    history.append({
        "role": "user",
        "content": message
    })

    memories = get_memories()

    # Ollama is called only for normal AI conversations.
    reply = get_ai_response(history, memories)

    save_message("user", message)
    save_message("assistant", reply)

    print("Chat Agent executed successfully.")

    return {
        "response": reply,
        "action": "generate_ai_response"
    }


# --------------------------------
# ROUTING
# --------------------------------

def route_to_agent(state: LifeOSState):

    return state["intent"]


# --------------------------------
# BUILD LANGGRAPH WORKFLOW
# --------------------------------

def build_graph():

    workflow = StateGraph(LifeOSState)

    workflow.add_node("supervisor", supervisor_agent)
    workflow.add_node("task_agent", task_agent)
    workflow.add_node("memory_agent", memory_agent)
    workflow.add_node("chat_agent", chat_agent)

    workflow.add_edge(START, "supervisor")

    workflow.add_conditional_edges(
        "supervisor",
        route_to_agent,
        {
            "task": "task_agent",
            "memory": "memory_agent",
            "chat": "chat_agent"
        }
    )

    workflow.add_edge("task_agent", END)
    workflow.add_edge("memory_agent", END)
    workflow.add_edge("chat_agent", END)

    return workflow.compile()


lifeos_graph = build_graph()


# --------------------------------
# CENTRAL EXECUTION + LOGGING
# --------------------------------

def run_lifeos_graph(message: str):

    start_time = time.perf_counter()

    intent = detect_intent(message)

    agent_names = {
        "task": "task_agent",
        "memory": "memory_agent",
        "chat": "chat_agent"
    }

    agent = agent_names[intent]
    action = "process_message"

    try:

        result = lifeos_graph.invoke({
            "message": message,
            "intent": "",
            "response": "",
            "action": ""
        })

        response = result["response"]
        action = result.get("action", action)

        duration_ms = int(
            (time.perf_counter() - start_time) * 1000
        )

        save_execution_log(
            message=message,
            agent=agent,
            action=action,
            status="success",
            response=response,
            duration_ms=duration_ms
        )

        print("Execution log saved successfully.")

        return response

    except Exception as error:

        duration_ms = int(
            (time.perf_counter() - start_time) * 1000
        )

        try:
            save_execution_log(
                message=message,
                agent=agent,
                action=action,
                status="failed",
                response=str(error)[:1000],
                duration_ms=duration_ms
            )
            print("Failed execution log saved.")
        except Exception as log_error:
            print("Execution logging error:", log_error)

        raise


# Keep old classifier available without executing agents.
def classify_message(message: str):

    return detect_intent(message)
