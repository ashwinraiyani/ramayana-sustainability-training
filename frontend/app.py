"""
Ramayana Sustainability Training Platform - Main Streamlit Application
A modern web interface for sustainability learning inspired by Ramayana wisdom
"""

import streamlit as st
import requests
import os
from datetime import datetime
import json

# Configuration
API_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Page Configuration
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
        padding: 1.5rem;
        background: linear-gradient(135deg, #FFD54F 0%, #FFF9C4 50%, #C8E6C9 100%);
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .module-card {
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #4CAF50;
        margin: 1rem 0;
        background: linear-gradient(135deg, #F1F8E9 0%, #FFFFFF 100%);
        transition: transform 0.3s;
    }
    .module-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    .stat-box {
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
        border: 2px solid #4CAF50;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stat-box h2 {
        color: #2E7D32;
        margin: 0;
        font-size: 2.5rem;
    }
    .stat-box p {
        color: #558B2F;
        margin: 0.5rem 0 0 0;
        font-size: 1rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .user-message {
        background: #E3F2FD;
        margin-left: 2rem;
    }
    .assistant-message {
        background: #FFF9C4;
        margin-right: 2rem;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #E8F5E9 0%, #FFFFFF 100%);
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'token' not in st.session_state:
    st.session_state.token = None
if 'user' not in st.session_state:
    st.session_state.user = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'current_page' not in st.session_state:
    st.session_state.current_page = "dashboard"

# API Helper Functions
def api_request(endpoint, method="GET", data=None, auth=True):
    """Make API request with error handling"""
    headers = {}
    if auth and st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    
    try:
        if method == "GET":
            response = requests.get(f"{API_URL}{endpoint}", headers=headers)
        elif method == "POST":
            response = requests.post(f"{API_URL}{endpoint}", json=data, headers=headers)
        elif method == "PUT":
            response = requests.put(f"{API_URL}{endpoint}", json=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(f"{API_URL}{endpoint}", headers=headers)
        
        if response.status_code == 200 or response.status_code == 201:
            return response.json(), None
        else:
            return None, f"Error {response.status_code}: {response.text}"
    except Exception as e:
        return None, f"Connection error: {str(e)}"

def login(username, password):
    """Login user"""
    data = {"username": username, "password": password}
    result, error = api_request("/api/users/login", "POST", data, auth=False)
    
    if result:
        st.session_state.logged_in = True
        st.session_state.token = result.get('access_token')
        st.session_state.user = result.get('user')
        return True, "Login successful!"
    return False, error or "Login failed"

def register(username, email, password, full_name):
    """Register new user"""
    data = {
        "username": username,
        "email": email,
        "password": password,
        "full_name": full_name
    }
    result, error = api_request("/api/users/register", "POST", data, auth=False)
    
    if result:
        return True, "Registration successful! Please login."
    return False, error or "Registration failed"

def logout():
    """Logout user"""
    st.session_state.logged_in = False
    st.session_state.token = None
    st.session_state.user = None
    st.session_state.chat_history = []

def send_chat_message(message):
    """Send message to chatbot"""
    data = {"message": message}
    result, error = api_request("/api/chatbot/message", "POST", data)
    
    if result:
        return result.get('message'), None
    return None, error

# Page Components
def render_header():
    """Render main header"""
    st.markdown(
        '<div class="main-header">🌿 Ramayana Sustainability Training 🌿<br/>'
        '<small style="font-size: 1rem;">Ancient Wisdom for Modern Sustainability</small></div>',
        unsafe_allow_html=True
    )

def render_login_page():
    """Render login and registration page"""
    render_header()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
        
        with tab1:
            st.subheader("Welcome Back!")
            username = st.text_input("Username or Email", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("Login", type="primary", use_container_width=True):
                    if username and password:
                        success, message = login(username, password)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                    else:
                        st.warning("Please enter both username and password")
            
            with col_b:
                st.info("**Test Account:**\nUsername: admin\nPassword: password123")
        
        with tab2:
            st.subheader("Create New Account")
            new_username = st.text_input("Username", key="reg_username")
            new_email = st.text_input("Email", key="reg_email")
            new_fullname = st.text_input("Full Name", key="reg_fullname")
            new_password = st.text_input("Password (min 8 characters)", type="password", key="reg_password")
            
            if st.button("Register", type="primary", use_container_width=True):
                if all([new_username, new_email, new_fullname, new_password]):
                    if len(new_password) >= 8:
                        success, message = register(new_username, new_email, new_password, new_fullname)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
                    else:
                        st.warning("Password must be at least 8 characters")
                else:
                    st.warning("Please fill in all fields")

def render_sidebar():
    """Render sidebar navigation"""
    with st.sidebar:
        st.image("https://via.placeholder.com/150/4CAF50/FFFFFF?text=User", width=150)
        
        user = st.session_state.user or {}
        st.markdown(f"### 👤 {user.get('full_name', 'User')}")
        st.markdown(f"📧 {user.get('email', 'N/A')}")
        st.markdown(f"🎯 Role: {user.get('role', 'employee').title()}")
        
        st.divider()
        
        st.markdown("### 🧭 Navigation")
        
        if st.button("📊 Dashboard", use_container_width=True):
            st.session_state.current_page = "dashboard"
            st.rerun()
        
        if st.button("📚 Learning Modules", use_container_width=True):
            st.session_state.current_page = "modules"
            st.rerun()
        
        if st.button("💬 Chat with Hanuman", use_container_width=True):
            st.session_state.current_page = "chatbot"
            st.rerun()
        
        if st.button("🏆 Leaderboard", use_container_width=True):
            st.session_state.current_page = "leaderboard"
            st.rerun()
        
        if st.button("👤 My Profile", use_container_width=True):
            st.session_state.current_page = "profile"
            st.rerun()
        
        st.divider()
        
        if st.button("🚪 Logout", type="secondary", use_container_width=True):
            logout()
            st.rerun()

def render_dashboard():
    """Render main dashboard"""
    render_header()
    
    st.subheader("📊 Your Learning Dashboard")
    
    # Stats boxes
    col1, col2, col3, col4 = st.columns(4)
    
    user = st.session_state.user or {}
    
    with col1:
        st.markdown(
            f'<div class="stat-box"><h2>{user.get("modules_completed", 0)}</h2><p>Modules Completed</p></div>',
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f'<div class="stat-box"><h2>{user.get("total_points", 0)}</h2><p>Total Points</p></div>',
            unsafe_allow_html=True
        )
    
    with col3:
        progress = (user.get("modules_completed", 0) / 5 * 100) if user.get("modules_completed", 0) > 0 else 0
        st.markdown(
            f'<div class="stat-box"><h2>{progress:.0f}%</h2><p>Overall Progress</p></div>',
            unsafe_allow_html=True
        )
    
    with col4:
        st.markdown(
            '<div class="stat-box"><h2>0</h2><p>Badges Earned</p></div>',
            unsafe_allow_html=True
        )
    
    st.divider()
    
    # Recent Activity
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📈 Your Progress")
        st.info("🎯 Start your learning journey with our modules!")
        
    with col2:
        st.subheader("🎖️ Achievements")
        st.success("Complete modules to earn badges!")

def render_modules_page():
    """Render learning modules page"""
    render_header()
    
    st.subheader("📚 Available Learning Modules")
    
    modules = [
        {
            "title": "Dharma in Business",
            "description": "Learn ethics and righteousness in business practices, inspired by Lord Rama's unwavering integrity",
            "icon": "⚖️",
            "duration": "45 min",
            "points": 100
        },
        {
            "title": "Harmony with Nature",
            "description": "Understand environmental stewardship through lessons from the forest exile (Vanavasa)",
            "icon": "🌳",
            "duration": "60 min",
            "points": 150
        },
        {
            "title": "Collective Welfare",
            "description": "Master teamwork and collaboration, inspired by building the bridge to Lanka",
            "icon": "🤝",
            "duration": "50 min",
            "points": 120
        },
        {
            "title": "Resource Management",
            "description": "Efficient governance and resource optimization from Ayodhya's sustainable model",
            "icon": "📊",
            "duration": "55 min",
            "points": 130
        },
        {
            "title": "Humility and Service",
            "description": "Leadership principles through Hanuman's devotion and selfless service",
            "icon": "🙏",
            "duration": "40 min",
            "points": 110
        }
    ]
    
    for module in modules:
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"""
                <div class="module-card">
                    <h3>{module['icon']} {module['title']}</h3>
                    <p>{module['description']}</p>
                    <p><strong>⏱️ Duration:</strong> {module['duration']} | <strong>🎯 Points:</strong> {module['points']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Start Learning", key=f"start_{module['title']}", type="primary"):
                    st.success(f"Starting: {module['title']}")
                    st.info("Module content will load here!")

def render_chatbot_page():
    """Render chatbot page"""
    render_header()
    
    st.subheader("💬 Chat with Hanuman - Your AI Guide")
    st.markdown("Ask me anything about sustainability, Ramayana wisdom, or your learning journey!")
    
    # Chat history display
    chat_container = st.container()
    
    with chat_container:
        for msg in st.session_state.chat_history:
            if msg['role'] == 'user':
                st.markdown(
                    f'<div class="chat-message user-message"><strong>You:</strong> {msg["content"]}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="chat-message assistant-message"><strong>🙏 Hanuman:</strong> {msg["content"]}</div>',
                    unsafe_allow_html=True
                )
    
    # Input area
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_input("Your message:", key="chat_input", label_visibility="collapsed")
    
    with col2:
        send_button = st.button("Send", type="primary", use_container_width=True)
    
    if send_button and user_input:
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Get AI response
        response, error = send_chat_message(user_input)
        
        if response:
            st.session_state.chat_history.append({"role": "assistant", "content": response})
        else:
            # Fallback response if API fails
            fallback_response = "🙏 Namaste! I am here to guide you on your sustainability journey. How may I assist you today?"
            st.session_state.chat_history.append({"role": "assistant", "content": fallback_response})
        
        st.rerun()
    
    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()

def render_leaderboard_page():
    """Render leaderboard page"""
    render_header()
    
    st.subheader("🏆 Sustainability Champions")
    
    # Mock leaderboard data
    leaderboard_data = [
        {"rank": 1, "name": "Arjun Sharma", "points": 850, "modules": 5, "badge": "🏅"},
        {"rank": 2, "name": "Priya Patel", "points": 720, "modules": 4, "badge": "🥈"},
        {"rank": 3, "name": "Raj Kumar", "points": 650, "modules": 4, "badge": "🥉"},
        {"rank": 4, "name": "Maria Santos", "points": 580, "modules": 3, "badge": "⭐"},
        {"rank": 5, "name": "John Doe", "points": 420, "modules": 3, "badge": "⭐"},
    ]
    
    for entry in leaderboard_data:
        col1, col2, col3, col4, col5 = st.columns([1, 3, 2, 2, 1])
        with col1:
            st.markdown(f"### {entry['badge']}")
        with col2:
            st.markdown(f"**{entry['name']}**")
        with col3:
            st.markdown(f"🎯 {entry['points']} points")
        with col4:
            st.markdown(f"📚 {entry['modules']} modules")
        with col5:
            st.markdown(f"**#{entry['rank']}**")
        st.divider()

def render_profile_page():
    """Render user profile page"""
    render_header()
    
    st.subheader("👤 My Profile")
    
    user = st.session_state.user or {}
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image("https://via.placeholder.com/200/4CAF50/FFFFFF?text=Profile", width=200)
    
    with col2:
        st.markdown(f"### {user.get('full_name', 'User')}")
        st.markdown(f"**Email:** {user.get('email', 'N/A')}")
        st.markdown(f"**Username:** {user.get('username', 'N/A')}")
        st.markdown(f"**Role:** {user.get('role', 'employee').title()}")
        st.markdown(f"**Member Since:** {user.get('created_at', 'N/A')}")
    
    st.divider()
    
    st.subheader("📊 Learning Statistics")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Modules Completed", user.get('modules_completed', 0))
    with col2:
        st.metric("Total Points", user.get('total_points', 0))
    with col3:
        st.metric("Current Streak", "0 days")

# Main Application
def main():
    if not st.session_state.logged_in:
        render_login_page()
    else:
        render_sidebar()
        
        page = st.session_state.current_page
        
        if page == "dashboard":
            render_dashboard()
        elif page == "modules":
            render_modules_page()
        elif page == "chatbot":
            render_chatbot_page()
        elif page == "leaderboard":
            render_leaderboard_page()
        elif page == "profile":
            render_profile_page()

if __name__ == "__main__":
    main()