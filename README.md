# LifeOS — WhatsApp-Powered Agentic AI Assistant

LifeOS is a WhatsApp-powered Agentic AI assistant designed to manage tasks, remember important personal information, and handle conversational requests through a structured agent workflow.

It combines LangGraph, Python, FastAPI, SQLite, and a locally running LLM through Ollama to create a practical AI assistant with an execution-monitoring dashboard.

## Key Features

- **WhatsApp Integration:** Send messages to LifeOS through the WhatsApp Cloud API.
- **Agent Routing:** A Supervisor routes incoming requests to the appropriate agent based on detected intent.
- **Task Management:** Create, view, complete, and delete tasks through WhatsApp.
- **Personal Memory:** Save and retrieve useful personal information.
- **AI Conversations:** Use a locally hosted LLM for general conversational requests.
- **Execution Monitoring:** Track agent activity, execution status, responses, and execution time.
- **Dashboard:** View execution statistics, recent activity, and task information.

## Architecture

LifeOS uses a LangGraph-based workflow to organize request handling.

```text
WhatsApp Message
       |
       v
  FastAPI Webhook
       |
       v
 Supervisor / Intent Router
       |
       +-------------------+
       |         |         |
       v         v         v
   Task Agent  Memory    Chat Agent
               Agent        |
       |         |           v
       |         |         Ollama
       |         |           |
       +---------+-----------+
                 |
                 v
          SQLite Database
                 |
                 v
          Execution Logs
                 |
                 v
         LifeOS Dashboard
```

The current Supervisor uses deterministic intent detection to route requests. The Chat Agent uses Ollama when a conversational response is needed.

## Technology Stack

| Component | Technology |
|---|---|
| Backend | Python, FastAPI |
| Agent Workflow | LangGraph |
| Local LLM | Ollama |
| Model | Llama 3.2 (1B) |
| Database | SQLite |
| Messaging | WhatsApp Cloud API |
| Dashboard | HTML, CSS, JavaScript |
| Tunneling | Cloudflare Tunnel |

## Project Structure

```text
LifeOS/
│
├── app/
│   ├── __init__.py
│   ├── ai_brain.py
│   ├── agent_graph.py
│   ├── main.py
│   ├── memory.py
│   └── dashboard.html
│
├── .gitignore
└── README.md
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/KamranAli786320/LifeOS-Agentic-AI.git
cd LifeOS-Agentic-AI
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install fastapi uvicorn requests python-dotenv langgraph
```

### 4. Install and configure Ollama

Install Ollama from:

https://ollama.com/

Pull the model:

```bash
ollama pull llama3.2:1b
```

Make sure Ollama is running locally.

### 5. Configure environment variables

Create a `.env` file in the project root:

```env
OLLAMA_MODEL=llama3.2:1b
OLLAMA_URL=http://localhost:11434/api/chat

WHATSAPP_ACCESS_TOKEN=your_access_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_VERIFY_TOKEN=your_verify_token
```

Replace the placeholder values with your own WhatsApp Cloud API credentials.

**Important:** Never upload your `.env` file, access tokens, or private credentials to GitHub.

### 6. Run the application

```bash
uvicorn app.main:app --reload
```

Open the API documentation:

http://127.0.0.1:8000/docs

Open the dashboard:

http://127.0.0.1:8000/dashboard

### 7. Configure WhatsApp Webhooks

For local development, expose your FastAPI server using a tunneling service such as Cloudflare Tunnel.

Configure the public webhook URL in your Meta Developer dashboard:

```text
https://YOUR-TUNNEL-URL/webhook
```

Subscribe to the WhatsApp `messages` webhook field.

## Example WhatsApp Commands

Create a task:

```text
Add task: Prepare my AI Engineer portfolio
```

View tasks:

```text
Show my tasks
```

Save personal information:

```text
Remember career: I am an AI Engineer specializing in Generative AI and Agentic AI.
```

Start a conversation:

```text
Explain what LifeOS does in simple words.
```

## Monitoring Dashboard
![LifeOS Dashboard](monitor%20agent.png)

The LifeOS dashboard provides visibility into:

- Total executions
- Successful and failed executions
- Average execution time
- Agent activity
- Recent execution logs
- Task overview

## Current Project Status

LifeOS is an actively developed portfolio project and working prototype.

The current implementation includes WhatsApp messaging, deterministic agent routing, task management, personal memory, local LLM conversations, SQLite execution logging, and a monitoring dashboard.

Production deployment, scalability, advanced agent orchestration, and additional reliability improvements remain future development areas.

## Future Improvements

- Human approval for sensitive actions
- More specialized agents and tools
- Improved error handling and retry mechanisms
- Enhanced monitoring and analytics
- Production-ready deployment
- Improved conversation and long-term memory capabilities

## Author

**Kamran Ali**

AI Engineer | Generative AI | Agentic AI | Machine Learning

- GitHub: https://github.com/KamranAli786320
- Portfolio: https://kamranali786320.github.io/KamranPortfolio/

---

*Built to explore practical applications of Agentic AI and intelligent automation.*
