# 🚀 Deployment Instructions

## Option 1: Streamlit Cloud (Recommended)
1. Push code to GitHub
2. Go to https://share.streamlit.io/
3. Connect GitHub repo
4. Set main file: `streamlit_standalone.py`
5. Add secrets: `OPENAI_API_KEY = your_key`
6. Deploy!

## Option 2: Heroku
```bash
# Install Heroku CLI
heroku create your-app-name
heroku config:set OPENAI_API_KEY=your_key
git push heroku main
```

## Option 3: Railway
1. Go to https://railway.app/
2. Connect GitHub repo
3. Add environment variable: `OPENAI_API_KEY`
4. Deploy automatically

## Option 4: Render
1. Go to https://render.com/
2. Connect GitHub repo
3. Add environment variable
4. Deploy

## Quick GitHub Setup:
```bash
git init
git add .
git commit -m "AI Calendar Booking Assistant"
git remote add origin https://github.com/yourusername/booking-agent
git push -u origin main
```

**Note**: For full functionality, deploy both API and Streamlit. Streamlit Cloud is easiest for demo.