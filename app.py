import uuid
import streamlit as st

from chatbot_engine import get_bot_response
from database import (
    create_tables,
    insert_default_faq,
    get_chat_sessions,
    get_messages_by_session,
    delete_chat_session
)

create_tables()
insert_default_faq()

st.set_page_config(
    page_title="EduGuide AI Chatbot",
    page_icon="🎓",
    layout="centered"
)

# ---------------- THEME ----------------
# ---------------- THEME ----------------
if "theme" not in st.session_state:
    st.session_state.theme = "light"

with st.sidebar:
    st.title("⚙️ Settings")

    dark_enabled = st.toggle(
        "Theme Mode",
        value=(st.session_state.theme == "dark")
    )

    if dark_enabled:
        st.session_state.theme = "dark"
        st.caption("Current: 🌙 Dark Mode")
    else:
        st.session_state.theme = "light"
        st.caption("Current: ☀️ Light Mode")

# ---------------- CSS UI ----------------
if st.session_state.theme == "dark":
    bg_color = "#050001"
    card = "#1e1e1e"
    sidebar = "#161b22"
    user_bubble = "#b8060e17"
    bot_bubble = "#312629"
    text_color = "#ffffff"
    muted_text = "#c9d1d9"
    button_bg = "#2b2f3a"
    button_text = "#ffffff"
    border_color = "rgba(255, 255, 255, 0.12)"
else:
    bg_color = "#eef3f8"
    card = "#ffffffff"
    sidebar = "#ffffff"
    user_bubble = "#d1fae5"
    bot_bubble = "#ffffff"
    text_color = "#000000D5"
    muted_text = "#E2E6EC"
    button_bg = "#e2e8f0"
    button_text = "#0d55fd"
    border_color = "rgba(15, 23, 42, 0.14)"
    chat_input = "#e2e8f0"

st.markdown(f"""
<style>
.stApp {{
    background-color: {bg_color};
}}

section[data-testid="stSidebar"] {{
    background-color: {sidebar};
    border-right: 1px solid {border_color};
}}

section[data-testid="stSidebar"] * {{
    color: {text_color} !important;
}}

.block-container {{
    background-color: {card};
    border-radius: 22px;
    padding: 2rem;
    max-width: 900px;
    margin-top: 2rem;
    box-shadow: 0 10px 30px rgba(15, 23, 42, 0.12);
}}

[data-testid="stChatMessage"] {{
    border-radius: 16px;
    padding: 14px;
    margin-bottom: 12px;
    font-size: 15px;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
}}

[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {{
    background-color: {user_bubble};
    color: #064e3b !important;
    margin-left: auto;
    max-width: 70%;
}}

[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) {{
    background-color: {bot_bubble};
    color: {text_color} !important;
    margin-right: auto;
    max-width: 70%;
    border: 1px solid {border_color};
}}

h1, h2, h3, h4, h5, h6 {{
    color: {text_color} !important;
    font-weight: 800;
}}

h1 {{
    text-align: center;
}}

p, span, div, label {{
    color: {text_color} !important;
}}

.stCaptionContainer, .stCaptionContainer * {{
    color: {muted_text} !important;
    text-align: center;
}}

.stMarkdown p {{
    color: {text_color} !important;
    opacity: 0.95;
}}

button {{
    background-color: {button_bg} !important;
    color: {button_text} !important;
    border: 1px solid {border_color} !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
}}

button:hover {{
    filter: brightness(0.96);
    border-color: #8b5cf6 !important;
}}

[data-testid="stCodeBlock"] {{
    background-color: {button_bg} !important;
     border: 1px solid {border_color} !important;
    border-radius: 10px;
}}

[data-testid="stChatInput"] textarea {{
    color: {text_color} !important;
}}


</style>
""", unsafe_allow_html=True)



# ---------------- SESSION ----------------
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- FUNCTIONS ----------------
def start_new_chat():
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = []

def load_old_chat(session_id):
    st.session_state.session_id = session_id
    st.session_state.messages = []

    old_messages = get_messages_by_session(session_id)

    for user_message, bot_response in old_messages:
        st.session_state.messages.append({
            "role": "user",
            "content": user_message
        })
        st.session_state.messages.append({
            "role": "assistant",
            "content": bot_response
        })

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("---")
    st.title("💬 Chats")

    if st.button("➕ New Chat", use_container_width=True):
        start_new_chat()
        st.rerun()

    st.markdown("---")
    st.subheader("Previous Chats")

    sessions = get_chat_sessions()

    if not sessions:
        st.caption("No previous chats yet.")
    else:
        for session_id, first_message, last_time in sessions:
            title = first_message[:30] + "..." if len(first_message) > 30 else first_message

            col1, col2 = st.columns([4, 1])

            with col1:
                if st.button(f"🕘 {title}", key=f"open_{session_id}", use_container_width=True):
                    load_old_chat(session_id)
                    st.rerun()

            with col2:
                if st.button("❌", key=f"delete_{session_id}"):
                    delete_chat_session(session_id)
                    st.rerun()

    st.markdown("---")
    st.subheader("Learning Format")
    st.subheader("teach: question = answer")

    st.write("In this format, you can teach the model by providing a question and its corresponding answer.")
    st.subheader("Sample Questions")
    st.write("- what courses do you offer")
    st.write("- what is cyber security")
    st.write("- explain machine learning simply")
    st.write("- suggest a course for coding")

# ---------------- MAIN UI ----------------
st.title("🎓 EduGuide AI Chatbot")
st.caption("Your Smart Education Assistant")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------------- INPUT ----------------
user_input = st.chat_input("Type your message here...")

if user_input:
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = get_bot_response(user_input, st.session_state.session_id)
            st.markdown(response)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })