from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from agent import BookingAgent
import uvicorn
from config import config

app = FastAPI(title="Calendar Booking Agent API")

# Global agent instance
booking_agent = BookingAgent()
user_sessions: Dict[str, Dict] = {}

class ChatMessage(BaseModel):
    message: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    response: str
    session_id: str

@app.post("/chat", response_model=ChatResponse)
async def chat(chat_message: ChatMessage):
    """Process chat message and return AI response"""
    try:
        # Get or create session state
        if chat_message.session_id not in user_sessions:
            user_sessions[chat_message.session_id] = {
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
        
        state = user_sessions[chat_message.session_id]
        
        # Process message
        response, updated_state = booking_agent.process_message(chat_message.message, state)
        
        # Update session state
        user_sessions[chat_message.session_id] = updated_state
        
        return ChatResponse(response=response, session_id=chat_message.session_id)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """Clear a specific session"""
    if session_id in user_sessions:
        del user_sessions[session_id]
        return {"message": f"Session {session_id} cleared"}
    return {"message": "Session not found"}

if __name__ == "__main__":
    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT)