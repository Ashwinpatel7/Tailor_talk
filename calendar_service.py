import os
import pickle
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from config import config

class CalendarService:
    def __init__(self):
        self.service = None
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with Google Calendar API"""
        creds = None
        if os.path.exists(config.GOOGLE_CALENDAR_TOKEN_FILE):
            with open(config.GOOGLE_CALENDAR_TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if os.path.exists(config.GOOGLE_CALENDAR_CREDENTIALS_FILE):
                    flow = InstalledAppFlow.from_client_secrets_file(
                        config.GOOGLE_CALENDAR_CREDENTIALS_FILE, config.SCOPES)
                    creds = flow.run_local_server(port=0)
                else:
                    # Mock credentials for demo
                    return self._setup_mock_service()
            
            with open(config.GOOGLE_CALENDAR_TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('calendar', 'v3', credentials=creds)
    
    def _setup_mock_service(self):
        """Setup mock service for demo purposes"""
        self.service = None
        print("Using mock calendar service - Google credentials not found")
    
    def get_free_slots(self, start_date: datetime, end_date: datetime, duration_minutes: int = 60) -> List[Dict]:
        """Get available time slots between start_date and end_date"""
        if not self.service:
            return self._get_mock_free_slots(start_date, end_date, duration_minutes)
        
        try:
            events_result = self.service.events().list(
                calendarId=config.CALENDAR_ID,
                timeMin=start_date.isoformat() + 'Z',
                timeMax=end_date.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            return self._calculate_free_slots(events, start_date, end_date, duration_minutes)
        except Exception as e:
            print(f"Error fetching calendar events: {e}")
            return self._get_mock_free_slots(start_date, end_date, duration_minutes)
    
    def _get_mock_free_slots(self, start_date: datetime, end_date: datetime, duration_minutes: int) -> List[Dict]:
        """Generate mock free slots for demo"""
        slots = []
        current = start_date.replace(hour=9, minute=0, second=0, microsecond=0)
        
        while current < end_date:
            if current.weekday() < 5 and 9 <= current.hour < 17:  # Weekdays 9-5
                slots.append({
                    'start': current,
                    'end': current + timedelta(minutes=duration_minutes),
                    'title': f'Available slot'
                })
            current += timedelta(hours=1)
        
        return slots[:10]  # Return first 10 slots
    
    def _calculate_free_slots(self, events: List, start_date: datetime, end_date: datetime, duration_minutes: int) -> List[Dict]:
        """Calculate free slots based on existing events"""
        busy_times = []
        for event in events:
            start = datetime.fromisoformat(event['start'].get('dateTime', event['start'].get('date')).replace('Z', '+00:00'))
            end = datetime.fromisoformat(event['end'].get('dateTime', event['end'].get('date')).replace('Z', '+00:00'))
            busy_times.append((start, end))
        
        free_slots = []
        current = start_date.replace(hour=9, minute=0, second=0, microsecond=0)
        
        while current < end_date:
            if current.weekday() < 5 and 9 <= current.hour < 17:
                slot_end = current + timedelta(minutes=duration_minutes)
                is_free = True
                
                for busy_start, busy_end in busy_times:
                    if (current < busy_end and slot_end > busy_start):
                        is_free = False
                        break
                
                if is_free:
                    free_slots.append({
                        'start': current,
                        'end': slot_end,
                        'title': 'Available slot'
                    })
            
            current += timedelta(minutes=30)
        
        return free_slots
    
    def book_appointment(self, start_time: datetime, end_time: datetime, title: str, description: str = "") -> bool:
        """Book an appointment"""
        if not self.service:
            print(f"Mock booking: {title} from {start_time} to {end_time}")
            return True
        
        try:
            event = {
                'summary': title,
                'description': description,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC',
                },
            }
            
            self.service.events().insert(calendarId=config.CALENDAR_ID, body=event).execute()
            return True
        except Exception as e:
            print(f"Error booking appointment: {e}")
            return False