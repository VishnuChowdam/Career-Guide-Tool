# 🚀 CareerGuide - AI-Powered Career Assistant

[![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-lightgrey?logo=flask)](https://flask.palletsprojects.com/)
[![LangChain](https://img.shields.io/badge/LangChain-0.1.0-yellow)](https://python.langchain.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A smart career guidance application that leverages AI to provide personalized career recommendations based on your skills, education, and interests. Built with Flask and powered by LLaMA 3.3.

## ✨ Features

- 🎯 **Personalized Recommendations**: Get career suggestions tailored to your profile
- 📊 **Skill Analysis**: Understand how your skills match different career paths
- 🏢 **Company Insights**: Discover top companies in your field of interest
- 📚 **Learning Roadmap**: Step-by-step guide to achieve your career goals
- 🔍 **Role Details**: In-depth information about each recommended role

## 🚀 Deployment on Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/yourusername/career-guide)

### Manual Deployment Steps:

1. **Create a new Web Service** on Render
2. **Connect your GitHub repository** or use the deploy button above
3. Configure your deployment:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Environment Variables**:
     ```
     SECRET_KEY=your-secret-key
     GROQ_API_KEY=your-groq-api-key
     PYTHON_VERSION=3.8.0
     ```
4. Click **Deploy**

## 🛠️ Local Development

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- Groq API key (for LLaMA 3.3)

### Installation

1. **Clone the repository**
   ```bash
   git clone [https://github.com/yourusername/career-guide.git](https://github.com/yourusername/career-guide.git)
   cd career-guide
