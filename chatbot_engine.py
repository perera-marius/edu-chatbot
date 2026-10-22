import os
from dotenv import load_dotenv
from groq import Groq

from database import search_answer, learn_new_answer, save_chat

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("API key not found. Check your .env file")

client = Groq(api_key=api_key)


def ask_ai(prompt):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are EduGuide AI, an education counseling chatbot. "
                        "Answer clearly and simply. Focus on education, courses, "
                        "career guidance, and student support."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"ERROR: {str(e)}"


def get_bot_response(user_message, session_id):
    user_message = user_message.strip()

    if not user_message:
        return "Please type a question."

    if user_message.lower().startswith("teach:"):
        try:
            data = user_message[6:].strip()
            question, answer = data.split("=", 1)

            learn_new_answer(question.strip(), answer.strip())

            response = "Thank you! I learned a new answer."
            save_chat(session_id, user_message, response)
            return response

        except Exception:
            response = "Use this format: teach: question = answer"
            save_chat(session_id, user_message, response)
            return response

    answer = search_answer(user_message)

    if answer:
        save_chat(session_id, user_message, answer)
        return answer

    ai_response = ask_ai(user_message)

    save_chat(session_id, user_message, ai_response)
    return ai_response