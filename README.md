# 🤖 Finance AI — Chat App with Graph Support

A lightweight chat interface powered by an AI backend for answering finance-related questions. 

Automatically displays AI-generated responses and renders graphs when provided.

## 🎬 Demo

https://github.com/user-attachments/assets/b9f0d9b5-0ff5-4b82-8a4e-7ec30c7d74bb

## 📦 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/jiakai2002/fin-ai.git
```

### 2. Install requirements

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Database and keys
Modify the .env file as follows:

*  OPENAI_API_KEY: your own API key from OpenAI. **Mandatory**.

*  OPENAI_MODEL_NAME: *gpt-4o-mini* or better is recommended. Default: `gpt-4o-mini`

*  MYSQL_USER: of the MySQL server user. Default: `root`

*  MYSQL_PASSWORD: of the MySQL server user. Default: `password`

*  MYSQL_HOST: hostname of MySQL server. Default: `localhost`

*  MYSQL_PORT: port on which mySQL is running. Default: `3306`.

Start the MySQL server, then populate the database with: 
```bash
cd src
python data/load_data.py
```

### 4. Start backend server


```bash
uvicorn server:app --reload
```

### 5. Launch frontend

Navigate to http://localhost:8000
You can now start chatting with Finance AI!

## 🖼️ Examples

- Ask about Apple's revenue
- ![apple_revenue](https://github.com/user-attachments/assets/8a8db44b-9cde-41d0-82b2-254a333175d3)
- Compare an indicator across companies in a specific year
- ![tech_company_dividends](https://github.com/user-attachments/assets/4f95cc69-9fed-4ddd-af1f-d82c0f64458b)


