import streamlit as st
import requests
from io import BytesIO
from st_audiorec import st_audiorec

# --- Configuration ---
st.set_page_config(page_title="AI Health Assistant", layout="wide")
BACKEND_URL = "http://127.0.0.1:8000/"

# --- State Management Initialization ---
if "token" not in st.session_state:
    st.session_state.token = None
if "username" not in st.session_state:
    st.session_state.username = None
if "page" not in st.session_state:
    st.session_state.page = "Login"
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- API Error Helper ---
def handle_api_error(e, context="request"):
    """Displays a user-friendly error message from the backend."""
    try:
        error_detail = e.response.json().get("detail", "No detail provided.")
        st.error(f"Error with {context}: {error_detail}")
    except (requests.exceptions.JSONDecodeError, AttributeError):
        st.error(f"An error occurred: {e.response.text}")

# --- UI Pages ---
def render_login_page():
    st.header("Login / Signup")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Login", use_container_width=True):
                try:
                    r = requests.post(f"{BACKEND_URL}auth/login", data={'username': username, 'password': password})
                    r.raise_for_status()
                    data = r.json()
                    st.session_state.token = data['access_token']
                    st.session_state.username = data['username']
                    st.session_state.page = "Chat"
                    st.rerun()
                except requests.exceptions.HTTPError as e:
                    handle_api_error(e, "login")
        with col2:
            if st.form_submit_button("Sign Up", use_container_width=True):
                try:
                    r = requests.post(f"{BACKEND_URL}auth/signup", json={"username": username, "password": password})
                    r.raise_for_status()
                    data = r.json()
                    st.session_state.token = data['access_token']
                    st.session_state.username = data['username']
                    st.session_state.page = "Chat"
                    st.rerun()
                except requests.exceptions.HTTPError as e:
                    handle_api_error(e, "signup")

def render_chat_page():
    st.title(f"Welcome, {st.session_state.username}!")
    headers = {"Authorization": f"Bearer {st.session_state.token}"}

    # Display existing chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    st.markdown("---")
    st.subheader("Compose Your Query")
    with st.form("query_form", clear_on_submit=True):
        st.write("You can record voice, type text, and upload an image.")
        
        recorded_audio_bytes = st_audiorec()
        text_input = st.text_area("Type additional symptoms or questions here:")
        uploaded_image = st.file_uploader("Optionally, upload an image of your concern:")
        
        submitted = st.form_submit_button("Submit Query")

        if submitted:
            if not recorded_audio_bytes and not text_input and not uploaded_image:
                st.warning("Please provide an input before submitting.")
                st.stop()

            try:
            
                if recorded_audio_bytes:
                    user_summary_placeholder = "🎤 Sending voice and text query..."
                    st.session_state.messages.append({"role": "user", "content": user_summary_placeholder})
                    
                    with st.spinner("Processing your query..."):
                        data = {"text_context": text_input}
                        files = {'file': ("recorded_audio.wav", BytesIO(recorded_audio_bytes), "audio/wav")}
                        
                        r = requests.post(f"{BACKEND_URL}query/voice", data=data, files=files, headers=headers)
                        r.raise_for_status()
                        response_data = r.json()
                        
                        user_summary = [f"🎤: {response_data['transcribed_text']}"]
                        if text_input: user_summary.append(f"📝: {text_input}")
                
                        st.session_state.messages[-1] = {"role": "user", "content": "\n\n".join(user_summary)}
                        st.session_state.messages.append({"role": "assistant", "content": response_data['text_response']})
                elif uploaded_image:
                    prompt = text_input if text_input else "User uploaded an image for analysis."
                    st.session_state.messages.append({"role": "user", "content": f"🖼️: Image uploaded\n\n📝: {prompt}"})

                    with st.spinner("Analyzing image..."):
                        files = {'file': (uploaded_image.name, uploaded_image.getvalue(), uploaded_image.type)}
                        r = requests.post(f"{BACKEND_URL}query/image", data={'query': prompt}, files=files, headers=headers)
                        r.raise_for_status()
                        response_text = r.json().get('response')
                        st.session_state.messages.append({"role": "assistant", "content": response_text})

                elif text_input:
                    st.session_state.messages.append({"role": "user", "content": text_input})
                    
                    with st.spinner("Thinking..."):
                        r = requests.post(f"{BACKEND_URL}query/text", json={"text": text_input}, headers=headers)
                        r.raise_for_status()
                        response_text = r.json().get('response')
                        st.session_state.messages.append({"role": "assistant", "content": response_text})
                
                st.rerun()

            except requests.exceptions.HTTPError as e:
                st.session_state.messages.append({"role": "assistant", "content": "Sorry, an error occurred while processing your request."})
                handle_api_error(e, "query submission")
                st.rerun()
            except Exception as e:
                st.error(f"An unexpected client-side error occurred: {e}")
                st.rerun()

def render_dashboard_page():
    st.title("Your Health Dashboard")
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        r = requests.get(f"{BACKEND_URL}dashboard/history", headers=headers)
        r.raise_for_status()
        history = r.json()
        if not history: 
            st.info("No conversation history yet.")
        for item in reversed(history):
            role = "You" if item['role'] == 'user' else "Assistant"
            content = item.get("content", "")
            timestamp_str = item.get("timestamp", "").split(".")[0].replace("T", " ")
            st.markdown(f"**{role}** (_{timestamp_str}_): {content}")
            st.markdown("---")
    except requests.exceptions.HTTPError as e:
        handle_api_error(e, "dashboard")

# --- Main App Logic ---
st.sidebar.title("Navigation")
if st.session_state.get("token"):
    st.sidebar.write(f"Logged in as: **{st.session_state.username}**")
    page = st.sidebar.radio("Navigate", ["Chat", "Dashboard", "Logout"])
    if page == "Chat":
        render_chat_page()
    elif page == "Dashboard":
        render_dashboard_page()
    elif page == "Logout":
        st.session_state.clear()
        st.session_state.page = "Login"
        st.rerun()
else:
    render_login_page()

