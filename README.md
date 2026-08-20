# AshAI Server

AshAI Server is a FastAPI-based backend that provides AI inference through a REST API. It includes user authentication, API key management, rate limiting, usage logging, and support for multiple AI models.

## Features

- JWT Authentication
- API Key Management
- AI Chat Endpoint
- Multiple Model Support
- Usage Logging
- Rate Limiting
- SQLite Database with SQLAlchemy
- Interactive Swagger Documentation

## Tech Stack

- FastAPI
- SQLAlchemy
- SQLite
- LangChain
- Ollama
- Pydantic

## Installation

Clone the repository

```bash
git clone https://github.com/ashwin-naik18/ashai-server.git
cd ashai-server
```

Create a virtual environment

```bash
python -m venv venv
```

Activate the virtual environment

**Windows**

```bash
venv\Scripts\activate
```

**Linux / macOS**

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

## Running the Server

```bash
uvicorn main:app --reload
```

The server will start at

```
http://127.0.0.1:8000
```

Swagger API documentation

```
http://127.0.0.1:8000/docs
```

## Project Structure

```
ashai-server/
│── main.py
│── database.py
│── model.py
│── schema.py
│── security.py
│── requirements.txt
└── README.md
```

