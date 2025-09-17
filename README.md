

# PDF Chatbot Monorepo

This monorepo contains a fullstack PDF chatbot application with:
- Modern Next.js frontend (React, TypeScript)
- FastAPI backend (Python)
- Local LLM integration (Ollama/Mistral)
- SQLite database
- Chroma vector database for semantic search

## Features
- User registration, login, and JWT authentication
- PDF upload and text extraction
- PDF text is split into chunks, embedded (sentence-transformers), and stored in Chroma vector DB
- Chat with local LLM about PDF content using semantic search (retrieves only relevant chunks)
- User memory: chatbot remembers user-provided facts/statements for each PDF
- Chat history per user and PDF
- Beautiful, production-grade UI
- Secure: users only see their own PDFs and chats
- Logout functionality

## Project Structure
- `/backend`: FastAPI app, database, PDF/LLM/vector logic
- `/frontend`: Next.js app, authentication, chat UI

## Setup

### Backend
1. Create and activate a Python virtual environment:
   ```powershell
   cd backend
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

### Frontend
1. Install Node.js dependencies:
   ```powershell
   cd frontend
   npm install
   ```
2. Run the development server:
   ```powershell
   npm run dev
   ```

## Usage
1. Register and login via the frontend.
2. Upload PDFs and chat about their content.
3. View chat history for each PDF.
4. Logout securely when done.

## Notes
- Update the LLM model endpoint in `backend/llm.py` if needed.
- For production, change the JWT secret key and use secure deployment practices.
- All data is stored locally in SQLite, Chroma vector DB, and `uploaded_pdfs/`.
