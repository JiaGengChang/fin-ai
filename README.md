# 🤖 Finance AI — Chat App with Graph Support

A lightweight chat interface powered by an AI backend for answering finance-related questions. 

Automatically displays AI-generated responses and renders graphs when provided.

## 🎬 Demo

https://github.com/user-attachments/assets/b9f0d9b5-0ff5-4b82-8a4e-7ec30c7d74bb

## 📦 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/finance-ai.git
```

### 2. Install requirements

```bash
pip install -r requirements.txt
```

### 3. Database and keys
Modify the .env file as follows:

*  OPENAI_API_KEY: your own API key from OpenAI.

*  MYSQL_[USER|PASSWORD]: of the MySQL server user e.g. root

*  MYSQL_HOST: hostname of MySQL server e.g localhost

*  DB_URI - format is `mysql+mysqlconnector://<user>:<password>@<address>:<port>/<db-name>`

```bash
cd backend
python data/load_data.py
```


### 4. Start backend server

(Start the MySQL server if you haven't done so already)

```bash
uvicorn server:app --reload
```

Ensure it runs on http://localhost:8000

### 5. Launch frontend

```bash
# On macOS
open frontend/index.html

# On Windows
start frontend/index.html
```

You can now start chatting with the AI!

## 🖼️ Examples

- Ask about Apple's revenue
- ![apple_revenue](https://github.com/user-attachments/assets/8a8db44b-9cde-41d0-82b2-254a333175d3)
- Compare an indicator across companies in a specific year
- ![tech_company_dividends](https://github.com/user-attachments/assets/4f95cc69-9fed-4ddd-af1f-d82c0f64458b)


