from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from calendar_service import CalendarService
import re
from dateutil import parser
from config import config
from typing_extensions import TypedDict
from smart_features import SmartFeatures

class BookingState(TypedDict):
    messages: List
    intent: Optional[str]
    date_preference: Optional[str]
    time_preference: Optional[str]
    duration: int
    available_slots: List[Dict]
    selected_slot: Optional[Dict]
    booking_confirmed: bool
    user_name: Optional[str]

class BookingAgent:
    def __init__(self):
        self.calendar_service = CalendarService()
        self.llm = ChatOpenAI(
            api_key=config.OPENAI_API_KEY,
            model="gpt-3.5-turbo",
            temperature=0.8
        ) if config.OPENAI_API_KEY else None
        self.graph = self._build_graph()
        self.user_preferences = {}  # Store user preferences
        self.conversation_context = {}  # Track conversation flow
    
    def _build_graph(self):
        workflow = StateGraph(BookingState)
        
        workflow.add_node("understand_intent", self._understand_intent)
        workflow.add_node("check_availability", self._check_availability)
        workflow.add_node("suggest_slots", self._suggest_slots)
        workflow.add_node("confirm_booking", self._confirm_booking)
        workflow.add_node("book_appointment", self._book_appointment)
        
        workflow.set_entry_point("understand_intent")
        
        workflow.add_conditional_edges(
            "understand_intent",
            self._route_after_intent,
            {
                "check_availability": "check_availability",
                "confirm": "confirm_booking",
                "end": END
            }
        )
        
        workflow.add_edge("check_availability", "suggest_slots")
        workflow.add_edge("suggest_slots", END)
        workflow.add_edge("confirm_booking", "book_appointment")
        workflow.add_edge("book_appointment", END)
        
        return workflow.compile()
    
    def _understand_intent(self, state: Dict) -> Dict:
        """Advanced intent understanding with context awareness"""
        if not state.get('messages', []):
            return state
        
        last_message = state['messages'][-1]
        user_input = last_message.content
        
        # Extract user name if mentioned
        if 'my name is' in user_input.lower() or 'i\'m ' in user_input.lower():
            import re
            name_match = re.search(r'(?:my name is|i\'m|call me)\s+([a-zA-Z]+)', user_input.lower())
            if name_match:
                state['user_name'] = name_match.group(1).title()
        
        if self.llm:
            # Enhanced prompt with context
            conversation_history = "\n".join([f"User: {msg.content}" if hasattr(msg, 'content') and not isinstance(msg, AIMessage) else f"Assistant: {msg.content}" for msg in state.get('messages', [])[-3:]])
            
            prompt = f"""You are an AI scheduling assistant. Analyze this conversation:

{conversation_history}

Latest message: "{user_input}"

Extract:
1. Intent: book/check_availability/confirm/select_slot/casual_chat/reschedule
2. Date preference (specific date, relative like 'tomorrow', or none)
3. Time preference (specific time, relative like 'afternoon', or none)
4. Meeting type (call, meeting, appointment, or none)
5. Duration preference (if mentioned)
6. Urgency level (urgent, flexible, or normal)

Format: intent|date|time|type|duration|urgency
Example: book|next friday|2pm|call|30min|normal"""
            
            try:
                response = self.llm.invoke(prompt).content.strip()
                parts = response.split('|')
                state['intent'] = parts[0] if len(parts) > 0 else 'book'
                state['date_preference'] = parts[1] if len(parts) > 1 and parts[1] not in ['none', ''] else None
                state['time_preference'] = parts[2] if len(parts) > 2 and parts[2] not in ['none', ''] else None
                state['meeting_type'] = parts[3] if len(parts) > 3 and parts[3] not in ['none', ''] else 'meeting'
                state['duration'] = self._parse_duration(parts[4]) if len(parts) > 4 and parts[4] not in ['none', ''] else 60
                state['urgency'] = parts[5] if len(parts) > 5 and parts[5] not in ['none', ''] else 'normal'
            except:
                self._basic_intent_extraction(state, user_input.lower())
        else:
            self._basic_intent_extraction(state, user_input.lower())
        
        return state
    
    def _parse_duration(self, duration_str: str) -> int:
        """Parse duration string to minutes"""
        if not duration_str:
            return 60
        import re
        if 'hour' in duration_str:
            hours = re.findall(r'(\d+)', duration_str)
            return int(hours[0]) * 60 if hours else 60
        elif 'min' in duration_str:
            mins = re.findall(r'(\d+)', duration_str)
            return int(mins[0]) if mins else 60
        return 60
    
    def _basic_intent_extraction(self, state: Dict, user_input: str):
        """Fallback intent extraction"""
        if any(word in user_input for word in ['book', 'schedule', 'appointment', 'meeting', 'call']):
            state['intent'] = 'book'
        elif any(word in user_input for word in ['available', 'free', 'slots', 'time']):
            state['intent'] = 'check_availability'
        elif any(word in user_input for word in ['yes', 'confirm', 'ok', 'sure', 'book it']):
            state['intent'] = 'confirm'
        else:
            state['intent'] = 'book'
        
        state['date_preference'] = self._extract_date_info(user_input)
        state['time_preference'] = self._extract_time_info(user_input)
    
    def _extract_date_info(self, text: str) -> Optional[str]:
        """Extract date information from text"""
        date_patterns = [
            r'tomorrow',
            r'today',
            r'next week',
            r'this week',
            r'monday|tuesday|wednesday|thursday|friday|saturday|sunday',
            r'\d{1,2}[/-]\d{1,2}',
            r'next \w+day'
        ]
        
        for pattern in date_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return re.search(pattern, text, re.IGNORECASE).group()
        return None
    
    def _extract_time_info(self, text: str) -> Optional[str]:
        """Extract time information from text"""
        time_patterns = [
            r'\d{1,2}:\d{2}\s*(am|pm)?',
            r'\d{1,2}\s*(am|pm)',
            r'morning|afternoon|evening',
            r'between\s+\d+.*\d+',
            r'\d+-\d+\s*pm'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group()
        return None
    
    def _route_after_intent(self, state: Dict) -> str:
        """Route based on understood intent"""
        # If we have available slots and user is selecting, go to confirm
        if state.get('available_slots') and not state.get('selected_slot'):
            messages = state.get('messages', [])
            if messages:
                last_msg = messages[-1].content.lower()
                # Check if user is selecting a slot
                if any(word in last_msg for word in ['1', '2', '3', '4', '5', 'pm', 'am', 'first', 'second']):
                    return "confirm"
        
        if state.get('intent') == 'confirm' and state.get('selected_slot'):
            return "confirm"
        elif state.get('intent') in ['book', 'check_availability']:
            return "check_availability"
        else:
            return "end"
    
    def _check_availability(self, state: Dict) -> Dict:
        """Check calendar availability"""
        start_date, end_date = self._parse_date_range(state.get('date_preference'))
        state['available_slots'] = self.calendar_service.get_free_slots(start_date, end_date, state.get('duration', 60))
        return state
    
    def _parse_date_range(self, date_pref: Optional[str]) -> tuple:
        """Parse date preference into start and end datetime"""
        now = datetime.now()
        
        if not date_pref:
            start_date = now + timedelta(days=1)
            end_date = start_date + timedelta(days=7)
        elif 'tomorrow' in date_pref.lower():
            start_date = now + timedelta(days=1)
            end_date = start_date + timedelta(days=1)
        elif 'today' in date_pref.lower():
            start_date = now
            end_date = start_date + timedelta(days=1)
        elif 'next week' in date_pref.lower():
            start_date = now + timedelta(days=7)
            end_date = start_date + timedelta(days=7)
        else:
            start_date = now + timedelta(days=1)
            end_date = start_date + timedelta(days=7)
        
        return start_date, end_date
    
    def _suggest_slots(self, state: Dict) -> Dict:
        """Smart slot suggestions with personalization"""
        if not state.get('available_slots', []):
            user_name = state.get('user_name', '')
            name_part = f"{user_name}, " if user_name else ""
            response = f"Sorry {name_part}I don't see any available slots for that time. How about we try a different day? What works better for your schedule?"
        else:
            # Smart filtering based on preferences
            slots = state['available_slots'][:5]
            urgency = state.get('urgency', 'normal')
            meeting_type = state.get('meeting_type', 'meeting')
            duration = state.get('duration', 60)
            
            # Add time zone awareness
            import datetime
            now = datetime.datetime.now()
            
            slots_text = []
            for i, slot in enumerate(slots, 1):
                start_time = slot['start']
                time_str = start_time.strftime("%A, %B %d at %I:%M %p")
                
                # Add helpful context
                if start_time.date() == now.date():
                    time_str += " (Today)"
                elif start_time.date() == (now + datetime.timedelta(days=1)).date():
                    time_str += " (Tomorrow)"
                
                # Add duration info
                if duration != 60:
                    time_str += f" ({duration} min)"
                
                slots_text.append(f"{i}. {time_str}")
            
            # Personalized response based on context
            user_name = state.get('user_name', '')
            name_part = f"{user_name}, " if user_name else ""
            time_pref = str(state.get('time_preference', '')).lower()
            
            if urgency == 'urgent':
                response = f"{name_part}I understand this is urgent! Here are the earliest available slots:\n\n" + "\n".join(slots_text)
            elif 'afternoon' in time_pref:
                response = f"Perfect {name_part}! I found some great afternoon slots for your {meeting_type}:\n\n" + "\n".join(slots_text)
            elif 'morning' in time_pref:
                response = f"Excellent {name_part}! Here are the morning options for your {meeting_type}:\n\n" + "\n".join(slots_text)
            else:
                response = f"Great {name_part}! I found these available times for your {meeting_type}:\n\n" + "\n".join(slots_text)
            
            # Smart follow-up questions
            if len(slots) == 1:
                response += "\n\nThis looks like the perfect time - shall I book it for you?"
            elif urgency == 'urgent':
                response += "\n\nWhich one works for your urgent needs?"
            else:
                response += "\n\nWhich one fits best with your schedule? Just let me know!"
        
        if 'messages' not in state:
            state['messages'] = []
        state['messages'].append(AIMessage(content=response))
        return state
    
    def _confirm_booking(self, state: Dict) -> Dict:
        """Confirm booking with natural selection"""
        messages = state.get('messages', [])
        last_message = messages[-1] if messages else None
        
        if last_message and hasattr(last_message, 'content'):
            user_input = last_message.content
            available_slots = state.get('available_slots', [])
            
            if self.llm and available_slots:
                # Use OpenAI to understand slot selection
                slots_info = "\n".join([f"{i+1}. {slot['start'].strftime('%A, %B %d at %I:%M %p')}" for i, slot in enumerate(available_slots)])
                prompt = f"""User said: "{user_input}"

Available slots:
{slots_info}

Which slot number (1-{len(available_slots)}) did they select? Respond with just the number, or 0 if unclear."""
                
                try:
                    response = self.llm.invoke(prompt).content.strip()
                    slot_num = int(response)
                    if 1 <= slot_num <= len(available_slots):
                        state['selected_slot'] = available_slots[slot_num - 1]
                except:
                    # Fallback to basic extraction
                    self._basic_slot_extraction(state, user_input, available_slots)
            else:
                self._basic_slot_extraction(state, user_input, available_slots)
        
        selected_slot = state.get('selected_slot')
        if selected_slot:
            start_time = selected_slot['start'].strftime("%A, %B %d at %I:%M %p")
            response = f"Excellent! I've got you down for {start_time}. Should I go ahead and book this for you?"
        else:
            response = "I'm not sure which time you prefer. Could you tell me the number or say something like 'the 2 PM slot'?"
        
        if 'messages' not in state:
            state['messages'] = []
        state['messages'].append(AIMessage(content=response))
        return state
    
    def _basic_slot_extraction(self, state: Dict, user_input: str, available_slots: List):
        """Fallback slot extraction"""
        user_lower = user_input.lower()
        
        # Number selection
        slot_num = self._extract_slot_number(user_lower)
        if slot_num and 1 <= slot_num <= len(available_slots):
            state['selected_slot'] = available_slots[slot_num - 1]
            return
        
        # Time-based selection
        for slot in available_slots:
            slot_time = slot['start'].strftime("%I:%M %p").lower()
            if slot_time in user_lower or slot_time.replace(':00', '') in user_lower:
                state['selected_slot'] = slot
                break
    
    def _extract_slot_number(self, text: str) -> Optional[int]:
        """Extract slot number from user input"""
        numbers = re.findall(r'\d+', text)
        return int(numbers[0]) if numbers else None
    
    def _book_appointment(self, state: Dict) -> Dict:
        """Premium booking experience with follow-up"""
        selected_slot = state.get('selected_slot')
        if selected_slot:
            meeting_type = state.get('meeting_type', 'meeting')
            duration = state.get('duration', 60)
            user_name = state.get('user_name', '')
            
            success = self.calendar_service.book_appointment(
                selected_slot['start'],
                selected_slot['end'],
                f"{meeting_type.title()} - {user_name}" if user_name else f"Scheduled {meeting_type.title()}",
                f"{duration}-minute {meeting_type} booked via AI assistant"
            )
            
            if success:
                start_time = selected_slot['start'].strftime("%A, %B %d at %I:%M %p")
                day_name = selected_slot['start'].strftime("%A")
                time_only = selected_slot['start'].strftime("%I:%M %p")
                
                # Personalized confirmation with helpful details
                name_part = f"{user_name}, " if user_name else ""
                
                # Calculate time until meeting
                import datetime
                now = datetime.datetime.now()
                time_diff = selected_slot['start'] - now
                
                if time_diff.days == 0:
                    time_context = "today"
                elif time_diff.days == 1:
                    time_context = "tomorrow"
                else:
                    time_context = f"in {time_diff.days} days"
                
                responses = [
                    f"🎉 Fantastic {name_part}! Your {duration}-minute {meeting_type} is confirmed for {start_time}. That's {time_context} - I've added it to your calendar!",
                    f"✅ All set {name_part}! Your {meeting_type} on {day_name} at {time_only} is booked. You'll receive a calendar invitation with all the details.",
                    f"🚀 Perfect {name_part}! See you {time_context} at {time_only} for our {meeting_type}. Looking forward to it!"
                ]
                
                import random
                response = random.choice(responses)
                
                # Add smart features
                meeting_id = SmartFeatures.generate_meeting_id()
                time_msg = SmartFeatures.get_time_zone_friendly_message(selected_slot['start'])
                prep_tip = SmartFeatures.suggest_meeting_prep(meeting_type, duration)
                
                response += f"\n\n{time_msg}\n{prep_tip}\n\n🆔 Meeting ID: {meeting_id}"
                
                if time_diff.days > 0:
                    weather = SmartFeatures.get_weather_context(selected_slot['start'])
                    response += f"\n🌤️ {weather}"
                
                # Add helpful follow-up
                if duration > 60:
                    response += f"\n\n💡 Since this is a {duration}-minute session, I recommend preparing any materials in advance."
                elif state.get('urgency') == 'urgent':
                    response += "\n\n⚡ I know this was urgent - glad we could get you scheduled quickly!"
                else:
                    response += "\n\n📅 Need to reschedule or have questions? Just let me know anytime!"
                
                state['booking_confirmed'] = True
                
                # Store user preference for future
                self.user_preferences[user_name or 'user'] = {
                    'preferred_duration': duration,
                    'preferred_meeting_type': meeting_type,
                    'last_booking': selected_slot['start'].isoformat()
                }
                
            else:
                response = f"Oops {name_part}! Something went wrong while booking your {meeting_type}. Let me try that again, or would you prefer a different time?"
        else:
            response = "Hmm, I don't have a time slot selected. Let's start fresh - when would you like to meet?"
        
        if 'messages' not in state:
            state['messages'] = []
        state['messages'].append(AIMessage(content=response))
        return state
    
    def process_message(self, message: str, state: Dict) -> tuple:
        """Process user message and return response"""
        if 'messages' not in state:
            state['messages'] = []
        
        state['messages'].append(HumanMessage(content=message))
        
        # Run the graph
        result = self.graph.invoke(state)
        
        # Get the last AI message
        ai_messages = [msg for msg in result['messages'] if isinstance(msg, AIMessage)]
        response = ai_messages[-1].content if ai_messages else "I'm here to help you book an appointment. What would you like to schedule?"
        
        return response, result