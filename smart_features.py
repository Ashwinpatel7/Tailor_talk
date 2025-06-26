"""
Advanced features for the booking agent
"""
import datetime
from typing import Dict, List
import random

class SmartFeatures:
    @staticmethod
    def get_weather_context(date: datetime.datetime) -> str:
        """Mock weather context for meetings"""
        weather_options = [
            "Perfect weather expected",
            "Might be rainy - good day for indoor meetings",
            "Beautiful sunny day ahead",
            "Cloudy but comfortable"
        ]
        return random.choice(weather_options)
    
    @staticmethod
    def suggest_meeting_prep(meeting_type: str, duration: int) -> str:
        """Suggest meeting preparation"""
        if meeting_type == 'call':
            if duration <= 30:
                return "💡 Quick tip: Have your key points ready for this focused call!"
            else:
                return "💡 Pro tip: Consider preparing an agenda for this longer call."
        elif meeting_type == 'meeting':
            return "💡 Suggestion: Bring any relevant documents or notes."
        return "💡 Tip: A few minutes of prep can make all the difference!"
    
    @staticmethod
    def get_time_zone_friendly_message(slot_time: datetime.datetime) -> str:
        """Generate time zone friendly messages"""
        hour = slot_time.hour
        if 6 <= hour < 12:
            return "🌅 Perfect morning time!"
        elif 12 <= hour < 17:
            return "☀️ Great afternoon slot!"
        elif 17 <= hour < 20:
            return "🌆 Nice evening time!"
        else:
            return "🌙 Late evening - hope that works for you!"
    
    @staticmethod
    def generate_meeting_id() -> str:
        """Generate a friendly meeting ID"""
        adjectives = ['swift', 'bright', 'smart', 'quick', 'smooth']
        nouns = ['chat', 'sync', 'meet', 'talk', 'call']
        numbers = random.randint(100, 999)
        return f"{random.choice(adjectives)}-{random.choice(nouns)}-{numbers}"
    
    @staticmethod
    def get_follow_up_suggestions(meeting_type: str) -> List[str]:
        """Get follow-up action suggestions"""
        if meeting_type == 'call':
            return [
                "Set up a follow-up call",
                "Schedule a longer deep-dive session",
                "Book a quick check-in next week"
            ]
        else:
            return [
                "Schedule a follow-up meeting",
                "Book time for next steps discussion",
                "Set up a progress review"
            ]