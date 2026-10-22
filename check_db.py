import sqlite3

conn = sqlite3.connect("knowledge_base.db")
cursor = conn.cursor()

print("FAQ DATA")
cursor.execute("SELECT id, question, answer FROM faq")
for row in cursor.fetchall():
    print(row)

print("\nCHAT HISTORY")
cursor.execute("SELECT id, user_message, bot_response, created_at FROM chat_history")
for row in cursor.fetchall():
    print(row)

conn.close()