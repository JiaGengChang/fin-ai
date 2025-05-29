FROM python:3.13-slim

WORKDIR /app

COPY src .
COPY .env .
COPY requirements.txt .

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "server:app", "--host=0.0.0.0", "--reload"]