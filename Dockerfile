FROM python:3.13-slim

WORKDIR /app

COPY src/main.py .
COPY src/agent.py .
COPY src/prompt.txt .
COPY src/db_description.txt .
COPY src/static static
COPY requirements.txt .

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=8000"]