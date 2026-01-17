# 🚀 Complete Quick Start Guide - Ramayana Sustainability Training Platform

## 📋 What's Already Done

Your repository now has:
✅ Backend API (FastAPI) - Complete
✅ Database Schema (PostgreSQL)
✅ Authentication System
✅ All API Routes (users, modules, chatbot, analytics)
✅ Configuration files

## 🎯 What You Need to Do (Simple 5 Steps)

### Step 1: Install Prerequisites (One-time setup)

**Install these on your computer:**

1. **Python 3.9+** - Download from https://www.python.org/downloads/
2. **PostgreSQL** - Download from https://www.postgresql.org/download/
3. **Git** - Download from https://git-scm.com/downloads

### Step 2: Clone and Setup

```bash
# Clone your repository
git clone https://github.com/ashwinraiyani/ramayana-sustainability-training.git
cd ramayana-sustainability-training

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Database

```bash
# Copy environment template
cp .env.example .env

# Edit .env file and update these lines:
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ramayana_training
DB_USER=postgres
DB_PASSWORD=your_postgres_password

# Add your OpenAI key (get from https://platform.openai.com/api-keys)
OPENAI_API_KEY=sk-your-key-here
```

### Step 4: Initialize Database

```bash
# Create database and tables
psql -U postgres -c "CREATE DATABASE ramayana_training;"
psql -U postgres -d ramayana_training -f database/schema.sql
psql -U postgres -d ramayana_training -f database/seed_data.sql
```

### Step 5: Run the Application

```bash
# Terminal 1 - Start Backend API
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Start Frontend (create this file below)
streamlit run frontend/app.py
```

---

## 📁 Frontend Code (Create These Files)

### File 1: `frontend/app.py`

```python
"""
Main Streamlit Application
Ramayana Sustainability Training Platform
"""

import streamlit as st
import requests
import os
from datetime import datetime

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Page config
st.set_page_config(
    page_title="Ramayana Sustainability Training",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E7D32;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #FFD54F 0%, #FFF9C4 100%);
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .module-card {
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #4CAF50;
        margin: 1rem 0;
        background: #F1F8E9;
    }
    .stat-box {
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        background: #E8F5E9;
        border: 1px solid #4CAF50;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'token' not in st.session_state:
    st.session_state.token = None
if 'user' not in st.session_state:
    st.session_state.user = None

def login(username, password):
    """Login function"""
    try:
        response = requests.post(
            f"{API_URL}/api/users/login",
            data={"username": username, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            st.session_state.logged_in = True
            st.session_state.token = data['access_token']
            st.session_state.user = data['user']
            return True
        return False
    except Exception as e:
        st.error(f"Login error: {e}")
        return False

def register(username, email, password, full_name):
    """Registration function"""
    try:
        response = requests.post(
            f"{API_URL}/api/users/register",
            json={
                "username": username,
                "email": email,
                "password": password,
                "full_name": full_name
            }
        )
        return response.status_code == 201
    except Exception as e:
        st.error(f"Registration error: {e}")
        return False

def logout():
    """Logout function"""
    st.session_state.logged_in = False
    st.session_state.token = None
    st.session_state.user = None

# Main App
def main():
    # Header
    st.markdown(
        '<div class="main-header">🌿 Ramayana Sustainability Training 🌿</div>',
        unsafe_allow_html=True
    )
    
    # Authentication
    if not st.session_state.logged_in:
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            st.subheader("🔐 Login")
            username = st.text_input("Username or Email", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            
            if st.button("Login", type="primary"):
                if login(username, password):
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")
        
        with tab2:
            st.subheader("📝 Register")
            new_username = st.text_input("Username", key="reg_username")
            new_email = st.text_input("Email", key="reg_email")
            new_fullname = st.text_input("Full Name", key="reg_fullname")
            new_password = st.text_input("Password", type="password", key="reg_password")
            
            if st.button("Register", type="primary"):
                if register(new_username, new_email, new_password, new_fullname):
                    st.success("✅ Registration successful! Please login.")
                else:
                    st.error("❌ Registration failed")
    
    else:
        # Sidebar
        with st.sidebar:
            st.image("https://via.placeholder.com/150", caption="Welcome!")
            st.write(f"**{st.session_state.user.get('full_name', 'User')}**")
            st.write(f"📧 {st.session_state.user.get('email', '')}")
            
            if st.button("Logout", type="secondary"):
                logout()
                st.rerun()
        
        # Main Dashboard
        st.subheader("📊 Your Learning Dashboard")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="stat-box"><h3>0</h3><p>Modules Completed</p></div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="stat-box"><h3>0</h3><p>Total Points</p></div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="stat-box"><h3>0%</h3><p>Progress</p></div>', unsafe_allow_html=True)
        with col4:
            st.markdown('<div class="stat-box"><h3>0</h3><p>Badges Earned</p></div>', unsafe_allow_html=True)
        
        # Available Modules
        st.subheader("📚 Available Modules")
        
        modules = [
            {"title": "Dharma in Business", "description": "Ethics and Righteousness"},
            {"title": "Harmony with Nature", "description": "Environmental Stewardship"},
            {"title": "Collective Welfare", "description": "Teamwork and Collaboration"},
            {"title": "Resource Management", "description": "Efficient Governance"},
            {"title": "Humility and Service", "description": "Leadership Principles"}
        ]
        
        for module in modules:
            with st.container():
                st.markdown(f"""
                <div class="module-card">
                    <h3>{module['title']}</h3>
                    <p>{module['description']}</p>
                </div>
                """, unsafe_allow_html=True)
                col1, col2 = st.columns([3, 1])
                with col2:
                    st.button("Start Module", key=f"start_{module['title']}")
        
        # Chatbot Section
        st.subheader("💬 Chat with Hanuman")
        
        user_message = st.text_input("Ask me anything about sustainability...")
        if st.button("Send"):
            if user_message:
                st.info(f"You: {user_message}")
                st.success("🙏 Hanuman: I'm here to guide you! This feature will be fully functional once the backend is connected.")

if __name__ == "__main__":
    main()
```

---

## 🔧 Additional Setup Scripts

### File 2: `scripts/init_database.py`

```python
#!/usr/bin/env python3
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def init_db():
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME', 'ramayana_training'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', '')
        )
        
        cursor = conn.cursor()
        
        # Read and execute schema
        with open('database/schema.sql', 'r') as f:
            cursor.execute(f.read())
        
        # Read and execute seed data
        with open('database/seed_data.sql', 'r') as f:
            cursor.execute(f.read())
        
        conn.commit()
        print("✅ Database initialized successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    init_db()
```

---

## 📖 Documentation Files

### File 3: `docs/DEPLOYMENT.md`

```markdown
# AWS Deployment Guide

## Option 1: Deploy to AWS EC2

1. Launch EC2 instance (t2.medium recommended)
2. Install dependencies
3. Clone repository
4. Setup PostgreSQL RDS
5. Configure environment variables
6. Run with systemd service

## Option 2: Deploy to Streamlit Cloud (Easiest)

1. Push code to GitHub
2. Go to https://streamlit.io/cloud
3. Connect your repository
4. Deploy with one click!

## Option 3: Deploy Backend to AWS Lambda

Use AWS SAM or Serverless framework for serverless deployment.

Complete guides coming soon!
```

---

## ✅ Testing Your Setup

### Test Backend API:
```bash
# Check if backend is running
curl http://localhost:8000/api/health

# Expected response:
# {"status":"healthy","message":"Ramayana Sustainability Training API is running","version":"1.0.0"}
```

### Test Frontend:
```bash
# Open browser to:
http://localhost:8501
```

---

## 🆘 Troubleshooting

### Problem: Database connection error
**Solution:** Check PostgreSQL is running and .env credentials are correct

### Problem: Module import errors
**Solution:** Ensure virtual environment is activated and dependencies installed

### Problem: Port already in use
**Solution:** Change port in command: `--port 8001`

---

## 📞 Support

For issues:
1. Check logs folder
2. Review .env configuration
3. Ensure all dependencies installed
4. Check database connection

---

## 🎉 You're Ready!

Your platform is now set up! 

**Login with:**
- Username: `admin`
- Password: `password123`

Start learning and building a sustainable future! 🌱
