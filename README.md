# 📅 AI Calendar Booking Assistant

A conversational AI agent that helps users book appointments on Google Calendar through natural language chat.

## 🚀 Features

- **Natural Language Processing**: Understands booking requests in plain English
- **Calendar Integration**: Connects with Google Calendar (with mock fallback)
- **Smart Scheduling**: Suggests available time slots based on preferences
- **Conversational Flow**: Guides users through the booking process
- **Real-time Chat**: Interactive Streamlit interface

## 🛠 Tech Stack

- **Backend**: FastAPI + Python
- **Agent Framework**: LangGraph
- **Frontend**: Streamlit
- **Calendar**: Google Calendar API
- **AI**: OpenAI GPT-3.5-turbo

## 📦 Installation

1. **Clone and navigate to the project**:
   ```bash
   cd "d:\Internshala\Tailor talk"
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   copy .env.example .env
   ```
   Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Optional - Google Calendar Setup**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing
   - Enable Google Calendar API
   - Create credentials (OAuth 2.0)
   - Download `credentials.json` to project root
   - *Note: App works with mock data if credentials not provided*

## 🏃‍♂️ Running the Application

### Option 1: Run Everything Together
```bash
python run.py
```

### Option 2: Run Separately
**Terminal 1 - API Server**:
```bash
python api.py
```

**Terminal 2 - Streamlit App**:
```bash
streamlit run streamlit_app.py
```

## 🌐 Access Points

- **Streamlit Chat Interface**: http://localhost:8501
- **FastAPI Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/health

## 💬 Example Conversations

Try these natural language requests:

- "Hey, I want to schedule a call for tomorrow afternoon"
- "Do you have any free time this Friday?"
- "Book a meeting between 3-5 PM next week"
- "What slots are available tomorrow morning?"
- "Schedule a 30-minute call for next Monday"

## 🔧 How It Works

1. **Intent Understanding**: Extracts booking intent from natural language
2. **Date/Time Parsing**: Identifies preferred dates and times
3. **Availability Check**: Queries calendar for free slots
4. **Slot Suggestion**: Presents available options to user
5. **Confirmation**: Confirms booking details
6. **Calendar Booking**: Creates the appointment

## 📁 Project Structure

```
d:\Internshala\Tailor talk\
├── agent.py              # LangGraph booking agent
├── api.py                # FastAPI backend
├── streamlit_app.py      # Streamlit frontend
├── calendar_service.py   # Google Calendar integration
├── config.py             # Configuration settings
├── run.py                # Application runner
├── requirements.txt      # Dependencies
├── .env.example          # Environment variables template
└── README.md             # This file
```

## 🔒 Security Notes

- API keys are loaded from environment variables
- Google OAuth tokens are stored locally
- Session data is managed in-memory
- No sensitive data is logged

## 🐛 Troubleshooting

**API Connection Issues**:
- Ensure FastAPI server is running on port 8000
- Check firewall settings
- Verify OpenAI API key is set

**Calendar Issues**:
- App works with mock data if Google credentials not provided
- Check Google Cloud Console for API quotas
- Ensure credentials.json is in project root

**Dependencies**:
- Use Python 3.8+
- Install all requirements: `pip install -r requirements.txt`

## 🎯 Demo Usage

The application includes mock calendar data, so you can test it immediately without Google Calendar setup. Just add your OpenAI API key and run!

---

**Built with ❤️ for Internshala Assignment**