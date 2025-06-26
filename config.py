import os
from typing import Optional

class Config:
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    GOOGLE_CALENDAR_CREDENTIALS_FILE: str = "credentials.json"
    GOOGLE_CALENDAR_TOKEN_FILE: str = "token.json"
    CALENDAR_ID: str = "primary"
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    # FastAPI settings
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    
    # Streamlit settings
    STREAMLIT_HOST: str = "127.0.0.1"
    STREAMLIT_PORT: int = 8501

config = Config()