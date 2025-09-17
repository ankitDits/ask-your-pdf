
# Backend

Python FastAPI API for PDF chatbot.


# Backend (FastAPI)

This is the backend for the PDF chatbot app. It provides authentication, PDF upload, chat, chat history, semantic search, and memory features.

## Features
- User registration, login, JWT auth
- PDF upload and text extraction
- PDF text is split into chunks and embedded (sentence-transformers)
- Chroma vector DB for semantic search and retrieval
- Chat with local LLM (Ollama/Mistral) using only relevant PDF chunks
- User memory: user-provided facts/statements are stored and included in LLM context for each PDF
- Chat history per user and PDF
- SQLite database

## Endpoints
- `/register` - Register new user
- `/login` - Login and get JWT
- `/upload_pdf` - Upload PDF and process
- `/chat` - Chat with LLM about PDF (semantic search + memory)
- `/history` - Get chat history
- `/logout` - (Frontend only)

## Setup
1. Create and activate a virtual environment:
	```powershell
	python -m venv venv
	.\venv\Scripts\activate
	pip install -r requirements.txt
	```
2. Start Ollama and pull the Mistral model:
	```powershell
	ollama pull mistral
	ollama serve
	```
3. Run the FastAPI server:
	```powershell
	uvicorn main:app --reload
	```

## Notes
- Chroma DB files are stored in `chroma_db/`
- Uploaded PDFs are stored in `uploaded_pdfs/`
- Change JWT secret key for production
