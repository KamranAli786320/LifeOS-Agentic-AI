
import sqlite3
from datetime import datetime

DB_NAME = "lifeos.db"


def init_db():
    connection = sqlite3.connect(DB_NAME)

    # Conversation history table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    # Personal memories table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS personal_memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            fact TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL
        )
    """)

    # Tasks table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL
        )
    """)

    # Agent execution logs table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS execution_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL,
            agent TEXT NOT NULL,
            action TEXT NOT NULL,
            status TEXT NOT NULL,
            response TEXT,
            duration_ms INTEGER,
            created_at TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


# Save conversation messages
def save_message(role, content):
    connection = sqlite3.connect(DB_NAME)

    connection.execute(
        """
        INSERT INTO conversations (role, content, timestamp)
        VALUES (?, ?, ?)
        """,
        (role, content, datetime.now().isoformat())
    )

    connection.commit()
    connection.close()


# Retrieve recent conversation history
def get_history(limit=10):
    connection = sqlite3.connect(DB_NAME)

    rows = connection.execute(
        """
        SELECT role, content
        FROM conversations
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,)
    ).fetchall()

    connection.close()

    return [
        {"role": role, "content": content}
        for role, content in reversed(rows)
    ]


# Save personal memory
def save_memory(category, fact):
    connection = sqlite3.connect(DB_NAME)

    connection.execute(
        """
        INSERT OR IGNORE INTO personal_memories
        (category, fact, created_at)
        VALUES (?, ?, ?)
        """,
        (category, fact, datetime.now().isoformat())
    )

    connection.commit()
    connection.close()


# Retrieve all personal memories
def get_memories():
    connection = sqlite3.connect(DB_NAME)

    rows = connection.execute(
        """
        SELECT category, fact
        FROM personal_memories
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()

    return [
        {"category": category, "fact": fact}
        for category, fact in rows
    ]


# Delete a personal memory
def delete_memory(fact):
    connection = sqlite3.connect(DB_NAME)

    cursor = connection.execute(
        """
        DELETE FROM personal_memories
        WHERE fact = ?
        """,
        (fact,)
    )

    deleted = cursor.rowcount

    connection.commit()
    connection.close()

    return deleted > 0


# Create a new task
def create_task(title):
    connection = sqlite3.connect(DB_NAME)

    cursor = connection.execute(
        """
        INSERT INTO tasks (title, status, created_at)
        VALUES (?, 'pending', ?)
        """,
        (title, datetime.now().isoformat())
    )

    task_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return task_id


# Retrieve all tasks
def get_tasks():
    connection = sqlite3.connect(DB_NAME)

    rows = connection.execute(
        """
        SELECT id, title, status, created_at
        FROM tasks
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()

    return [
        {
            "id": row[0],
            "title": row[1],
            "status": row[2],
            "created_at": row[3]
        }
        for row in rows
    ]


# Mark a task as completed
def complete_task(task_id):
    connection = sqlite3.connect(DB_NAME)

    cursor = connection.execute(
        """
        UPDATE tasks
        SET status = 'completed'
        WHERE id = ?
        """,
        (task_id,)
    )

    updated = cursor.rowcount

    connection.commit()
    connection.close()

    return updated > 0


# Delete a task
def delete_task(task_id):
    connection = sqlite3.connect(DB_NAME)

    cursor = connection.execute(
        """
        DELETE FROM tasks
        WHERE id = ?
        """,
        (task_id,)
    )

    deleted = cursor.rowcount

    connection.commit()
    connection.close()

    return deleted > 0


# Save agent execution log
def save_execution_log(
    message,
    agent,
    action,
    status,
    response=None,
    duration_ms=None
):
    connection = sqlite3.connect(DB_NAME)

    connection.execute(
        """
        INSERT INTO execution_logs
        (message, agent, action, status, response, duration_ms, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            message,
            agent,
            action,
            status,
            response,
            duration_ms,
            datetime.now().isoformat()
        )
    )

    connection.commit()
    connection.close()


# Retrieve recent execution logs
def get_execution_logs(limit=50):
    connection = sqlite3.connect(DB_NAME)

    rows = connection.execute(
        """
        SELECT id, message, agent, action, status,
               response, duration_ms, created_at
        FROM execution_logs
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,)
    ).fetchall()

    connection.close()

    return [
        {
            "id": row[0],
            "message": row[1],
            "agent": row[2],
            "action": row[3],
            "status": row[4],
            "response": row[5],
            "duration_ms": row[6],
            "created_at": row[7]
        }
        for row in rows
    ]
