import streamlit as st
import os
from datetime import datetime, timedelta
import uuid
from agent import BookingAgent

# Page config
st.set_page_config(
    page_title="AI Calendar Booking Assistant",
    page_icon="📅",
    layout="wide"
)

def initialize_session():
    """Initialize session state"""
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "booking_agent" not in st.session_state:
        st.session_state.booking_agent = BookingAgent()
    if "session_state" not in st.session_state:
        st.session_state.session_state = {
            'messages': [],
            'intent': None,
            'date_preference': None,
            'time_preference': None,
            'duration': 60,
            'available_slots': [],
            'selected_slot': None,
            'booking_confirmed': False,
            'user_name': None
        }

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
            st.session_state.session_state = {
                'messages': [],
                'intent': None,
                'date_preference': None,
                'time_preference': None,
                'duration': 60,
                'available_slots': [],
                'selected_slot': None,
                'booking_confirmed': False,
                'user_name': None
            }
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
        
        st.markdown("---")
        st.header("🔌 Status")
        st.success("✅ Ready to Book!")
    
    # Display chat messages
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
                try:
                    response, updated_state = st.session_state.booking_agent.process_message(
                        prompt, st.session_state.session_state
                    )
                    st.session_state.session_state = updated_state
                    st.write(response)
                except Exception as e:
                    response = f"I'm having trouble processing that. Could you try rephrasing? (Error: {str(e)})"
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