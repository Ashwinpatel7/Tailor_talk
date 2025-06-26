import streamlit as st
import requests
import json
from datetime import datetime
import uuid

# Page config
st.set_page_config(
    page_title="AI Calendar Booking Assistant",
    page_icon="📅",
    layout="wide"
)

# API endpoint
API_URL = "http://127.0.0.1:8000"

def initialize_session():
    """Initialize session state"""
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "api_available" not in st.session_state:
        st.session_state.api_available = check_api_health()

def check_api_health():
    """Check if API is available"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def send_message(message: str):
    """Send message to API and get response"""
    try:
        payload = {
            "message": message,
            "session_id": st.session_state.session_id
        }
        response = requests.post(f"{API_URL}/chat", json=payload, timeout=30)
        
        if response.status_code == 200:
            return response.json()["response"]
        else:
            return f"Error: {response.status_code} - {response.text}"
    except requests.exceptions.RequestException as e:
        return f"Connection error: {str(e)}"

def main():
    initialize_session()
    
    # Header
    st.title("📅 AI Calendar Booking Assistant")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Controls")
        
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            try:
                requests.delete(f"{API_URL}/session/{st.session_state.session_id}")
            except:
                pass
            st.rerun()
        
        st.markdown("---")
        st.header("ℹ️ Instructions")
        st.markdown("""
        **Try these examples:**
        - "I want to schedule a call for tomorrow afternoon"
        - "Do you have any free time this Friday?"
        - "Book a meeting between 3-5 PM next week"
        - "What slots are available tomorrow?"
        """)
        
        # API Status
        st.markdown("---")
        st.header("🔌 Status")
        if st.session_state.api_available:
            st.success("✅ API Connected")
        else:
            st.error("❌ API Disconnected")
            if st.button("🔄 Retry Connection"):
                st.session_state.api_available = check_api_health()
                st.rerun()
    
    # Main chat interface
    if not st.session_state.api_available:
        st.error("🚫 **API Server Not Available**")
        st.markdown("""
        Please make sure the FastAPI server is running:
        ```bash
        python api.py
        ```
        """)
        return
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.write(message["content"])
            else:
                with st.chat_message("assistant"):
                    st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = send_message(prompt)
            st.write(response)
        
        # Add AI response to chat
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Welcome message for new users
    if not st.session_state.messages:
        with st.chat_message("assistant"):
            welcome_msg = """
            👋 **Welcome to your AI Calendar Booking Assistant!**
            
            I can help you:
            - 📅 Check your calendar availability
            - ⏰ Schedule appointments and meetings
            - 🔍 Find suitable time slots
            - ✅ Confirm bookings
            
            Just tell me what you'd like to schedule and when!
            """
            st.markdown(welcome_msg)
            st.session_state.messages.append({"role": "assistant", "content": welcome_msg})

if __name__ == "__main__":
    main()