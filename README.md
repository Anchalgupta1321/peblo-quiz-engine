# Peblo AI Backend Engineer Challenge

This repository contains a prototype backend system for ingesting educational content from PDFs and generating quiz questions using an LLM, developed for the Peblo challenge.

## System Architecture

```
PDF
 │
 ▼
Content Ingestion Service
 │
 ▼
Chunked Content DB
 │
 ▼
LLM Quiz Generator
 │
 ▼
Quiz Questions DB
 │
 ▼
FastAPI Endpoints
 │
 ▼
Student Answers + Adaptive Difficulty
```

## Features

1. **Traceability**: Questions maintain a strict reference to the `source_chunk_id`.
2. **Clean Architecture**: Structured isolating `ingestion`, `llm`, `services`, and `api` modules.
3. **Adaptive Difficulty Logic**: Easy → correct → medium; Medium → correct → hard; Hard → wrong → medium.
4. **Duplicate Detection Framework**: Built defensively against LLM overlapping. 

## Setup Instructions

Ensure you have Python 3.8+ installed. 

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure environment variables
Copy the environment template:
```bash
cp .env.example .env
```
Edit `.env` and add your OpenAI API key for `LLM_API_KEY`. If no key is provided, the system falls back to generating mock queries so you can still test the flow locally without friction!

### 3. Run the backend
Start the FastAPI server via uvicorn:
```bash
uvicorn app.main:app --reload
```

## API Testing

FastAPI provides an interactive UI out of the box. Use:

[http://localhost:8000/docs](http://localhost:8000/docs)

(FastAPI Swagger)
