import streamlit as st
import requests
import os

st.set_page_config(page_title="College Assistant Bot", page_icon="🎓", layout="centered")

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
# Initialize global session properties
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- AUTHENTICATION INTERFACE ---
if not st.session_state.authenticated:
    st.title("🎓 College Portal Access")
    tabs = st.tabs(["Login to System", "Create an Account"])
    
    with tabs[0]:
        st.subheader("Login Form")
        login_user = st.text_input("Username", key="login_user_input")
        login_pass = st.text_input("Password", type="password", key="login_pass_input")
        if st.button("Log In", use_container_width=True):
            try:
                res = requests.post(f"{BACKEND_URL}/api/login", json={"username": login_user, "password": login_pass})
                if res.status_code == 200:
                    st.session_state.authenticated = True
                    st.session_state.username = login_user
                    st.success("Authorized! Directing to assistant framework...")
                    st.rerun()
                else:
                    st.error(res.json().get("detail", "Authentication rejected."))
            except Exception:
                st.error("Could not connect to authentication services server backend.")

    with tabs[1]:
        st.subheader("Registration Form")
        reg_user = st.text_input("Preferred Username", key="reg_user_input")
        reg_pass = st.text_input("Secure Password", type="password", key="reg_pass_input")
        if st.button("Register Account", use_container_width=True):
            try:
                res = requests.post(f"{BACKEND_URL}/api/register", json={"username": reg_user, "password": reg_pass})
                if res.status_code == 200:
                    st.success("Account constructed successfully! Please switch tabs to login.")
                else:
                    st.error(res.json().get("detail", "Registration blocked."))
            except Exception:
                st.error("Backend offline or inaccessible during user setup processing.")

# --- CONVERSATIONAL ASSISTANT FRAMEWORK ---
else:
    st.sidebar.title(f"👤 Welcome, {st.session_state.username}!")
    if st.sidebar.button("Logout from Session"):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.session_state.chat_history = []
        st.rerun()

    st.title("🤖 Intelligent College Virtual Assistant")
    st.caption("Ask questions about fee structures, available seats, engineering branches, and core documentation details.")

    # Render ongoing conversations
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Monitor query submissions
    if user_prompt := st.chat_input("Ask a question regarding courses or fees..."):
        with st.chat_message("user"):
            st.markdown(user_prompt)
        st.session_state.chat_history.append({"role": "user", "content": user_prompt})

        # Process queries via the backend pipeline
        with st.chat_message("assistant"):
            try:
                # Use the unique username as the conversation thread_id to persist history across logins
                payload = {"question": user_prompt, "thread_id": f"session_{st.session_state.username}"}
                res = requests.post(f"{BACKEND_URL}/api/chat", json=payload)
                
                if res.status_code == 200:
                    bot_reply = res.json().get("response")
                    st.markdown(bot_reply)
                    st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
                else:
                    st.error("The assistant pipeline ran into issues resolving this request.")
            except Exception:
                st.error("Communication channel with intelligence backend has timed out.")
