# 💬 Finance AI — Chat App with Graph Support

A lightweight chat interface powered by an AI backend for answering finance-related questions. Automatically displays AI-generated responses and renders graphs when provided.

## 🚀 Features

- Clean chat UI with smooth scroll and resizing
- Handles multiline messages and line breaks
- Sends user input to backend via REST API (`POST /ask`)
- Renders both text and graph responses
- Automatic response handling, loading indication (↑ / ◼)

## 📦 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/finance-ai.git
cd finance-ai/frontend
```

### 2. Install requirements

```bash
cd ../backend
pip install -r requirements.txt
```

### 3. Start backend server

```bash
uvicorn main:app --reload
```

Ensure it runs on http://localhost:8000

### 4. Launch frontend

```bash
# On macOS
open frontend/index.html

# On Windows
start frontend/index.html
```

You can now start chatting with the AI!
