# 🌿 Ramayana-Inspired Sustainability Training Platform

An AI-powered corporate training platform that teaches sustainability principles through the timeless wisdom of the Ramayana epic.

## 🎯 Overview

This platform combines ancient Indian wisdom from the Ramayana with modern sustainability practices to create an engaging, culturally-rooted learning experience for organizations.

## ✨ Key Features

- **AI Chatbot (Hanuman)** - Personalized learning assistant powered by AI
- **Adaptive Learning Paths** - Customized journey based on role and assessment
- **Interactive Modules** - Engaging content with quizzes and simulations
- **Team Simulations** - Collaborative sustainability challenges
- **Analytics Dashboard** - Real-time insights for HR teams
- **Gamification** - Points, badges, and leaderboards
- **Micro-Learning** - Bite-sized daily lessons
- **Progress Tracking** - Individual and organizational metrics

## 🛠️ Technology Stack

- **Frontend:** Streamlit (Python-based web framework)
- **Backend:** FastAPI (Python REST API)
- **Database:** PostgreSQL on AWS RDS
- **AI:** OpenAI API / AWS Bedrock
- **Storage:** AWS S3
- **Authentication:** AWS Cognito
- **Deployment:** AWS EC2 / Streamlit Cloud

## 📋 Prerequisites

- Python 3.9 or higher
- AWS Account (free tier works)
- OpenAI API key (or AWS Bedrock access)
- Git installed

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/ashwinraiyani/ramayana-sustainability-training.git
cd ramayana-sustainability-training
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env with your credentials
```

### 4. Initialize Database
```bash
python scripts/init_database.py
```

### 5. Run the Application
```bash
# Start backend API
uvicorn backend.main:app --reload

# In another terminal, start frontend
streamlit run frontend/app.py
```

## 📁 Project Structure

```
ramayana-sustainability-training/
├── backend/              # FastAPI backend
├── frontend/             # Streamlit frontend
├── database/             # Database schemas and migrations
├── aws/                  # AWS deployment configuration
├── docs/                 # Documentation
├── tests/                # Test files
└── scripts/              # Utility scripts
```

## 📚 Documentation

- [User Guide](docs/USER_GUIDE.md) - For employees using the platform
- [Admin Guide](docs/ADMIN_GUIDE.md) - For HR administrators
- [Deployment Guide](docs/DEPLOYMENT.md) - AWS deployment instructions
- [API Documentation](docs/API_DOCS.md) - Backend API reference

## 🌐 Deployment

Detailed AWS deployment instructions are available in [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

### Quick Deploy to AWS
```bash
cd aws
./scripts/deploy.sh
```

## 🧪 Testing

```bash
pytest tests/
```

## 📊 Sample Data

The platform comes with pre-loaded sample data:
- 5 learning modules
- 20+ quiz questions
- Sample user accounts
- Department analytics

## 🤝 Contributing

This is a private project. For questions or suggestions, contact the maintainer.

## 📄 License

MIT License - See LICENSE file for details

## 🆘 Support

For issues or questions:
1. Check [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
2. Create an issue in this repository
3. Contact: ashwinraiyani@github

## 🙏 Acknowledgments

Inspired by the timeless wisdom of the Ramayana and modern sustainability practices.

---

**Built with ❤️ for a sustainable future**