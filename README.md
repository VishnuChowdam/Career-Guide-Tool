# 🚀 CareerGuide - AI-Powered Career Assistant

[![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-lightgrey?logo=flask)](https://flask.palletsprojects.com/)
[![LangChain](https://img.shields.io/badge/LangChain-0.1.0-yellow)](https://python.langchain.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A smart career guidance application that leverages AI to provide personalized career recommendations based on your skills, education, and interests. Built with Flask and powered by LLaMA 3.3.

## 🛠️ Tech Stack

- **Backend:** Flask (Python)
- **AI/LLM:** LLaMA 3.3 (via Groq API)
- **Orchestration:** LangChain
- **Frontend:** HTML5,TailwindCSS
- **Deployment:** Render / Gunicorn

## ✨ Features

- 🎯 **Personalized Recommendations**: Get career suggestions tailored to your profile
- 📊 **Skill Analysis**: Understand how your skills match different career paths
- 🏢 **Company Insights**: Discover top companies in your field of interest
- 📚 **Learning Roadmap**: Step-by-step guide to achieve your career goals
- 🔍 **Role Details**: In-depth information about each recommended role


## 🚀 Deployment on Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/yourusername/career-guide)

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- [Groq API key](https://console.groq.com/) (for LLaMA 3.3)

### 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone [https://github.com/yourusername/career-guide.git](https://github.com/yourusername/career-guide.git)
   cd career-guide
2. **Set up virtual environment**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
4. **Configure environment variabless**
   ```bash
   # Groq API Configuration
   GROQ_API_KEY="your-groq-api-key-here"
5. **Run the development server**
   ```bash
   python app.py
6. **Access the application**
   ```bash
   http://localhost:5000

## 📂 Project Structure

```text
career-guide/
├── app.py                 # Main Flask application
├── rag.py                 # AI recommendation engine
├── requirements.txt       # Python dependencies
├── Procfile               # Deployment commands for Render
├── .gitignore             # Files to exclude from Git
├── .env                   # Environment variables (Not on GitHub)
├── static/                # Static files (CSS, JS, images)
│   └── ...
└── templates/             # HTML templates
    ├── base.html          # Base template
    ├── index.html         # Home page
    ├── dashboard.html     # Recommendations
    └── role_details.html  # Role information
   
