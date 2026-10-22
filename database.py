import sqlite3
from datetime import datetime

DB_NAME = "knowledge_base.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS faq (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            user_message TEXT NOT NULL,
            bot_response TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def insert_default_faq():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM faq")
    count = cursor.fetchone()[0]

    if count == 0:
        default_data = [
            ("hello", "Hello! I am EduGuide AI. How can I help you?"),
            ("hi", "Hi! Welcome to EduGuide AI."),
            ("what courses do you offer", "We offer IT, Business Management, Software Engineering, and Cyber Security courses."),
            ("what is software engineering", "Software Engineering is about designing, developing, testing, and maintaining software systems."),
            ("what is cyber security", "Cyber Security focuses on protecting computer systems, networks, and data from attacks."),
            ("thank you", "You are welcome!"),
            ("bye", "Goodbye! Have a nice day!")
        ]

        cursor.executemany(
            "INSERT INTO faq (question, answer) VALUES (?, ?)",
            default_data
        )

    conn.commit()
    conn.close()


def search_answer(user_question):
    conn = get_connection()
    cursor = conn.cursor()

    user_question = user_question.strip().lower()

    cursor.execute(
        "SELECT answer FROM faq WHERE LOWER(question) = ?",
        (user_question,)
    )
    exact = cursor.fetchone()

    if exact:
        conn.close()
        return exact[0]

    words = user_question.split()

    cursor.execute("SELECT question, answer FROM faq")
    rows = cursor.fetchall()

    for question, answer in rows:
        q_words = question.lower().split()

        if all(word in words for word in q_words):
            conn.close()
            return answer

    conn.close()
    return None


def learn_new_answer(question, answer):
    conn = get_connection()
    cursor = conn.cursor()

    question = question.strip().lower()
    answer = answer.strip()

    cursor.execute(
        "SELECT id FROM faq WHERE LOWER(question) = ?",
        (question,)
    )

    existing = cursor.fetchone()

    if existing:
        cursor.execute(
            "UPDATE faq SET answer = ? WHERE id = ?",
            (answer, existing[0])
        )
    else:
        cursor.execute(
            "INSERT INTO faq (question, answer) VALUES (?, ?)",
            (question, answer)
        )

    conn.commit()
    conn.close()


def save_chat(session_id, user_message, bot_response):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO chat_history (session_id, user_message, bot_response)
        VALUES (?, ?, ?)
        """,
        (session_id, user_message, bot_response)
    )

    conn.commit()
    conn.close()


def get_chat_sessions():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            session_id,
            MIN(user_message) AS first_message,
            MAX(created_at) AS last_time
        FROM chat_history
        GROUP BY session_id
        ORDER BY last_time DESC
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows


def get_messages_by_session(session_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_message, bot_response
        FROM chat_history
        WHERE session_id = ?
        ORDER BY created_at ASC
    """, (session_id,))

    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_chat_session(session_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM chat_history WHERE session_id = ?",
        (session_id,)
    )

    conn.commit()
    conn.close()    