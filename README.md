# PDF Chatbot Monorepo

This monorepo contains a fullstack application for chatting with PDFs using a local LLM.

## Structure
- `/backend`: Python API, PDF upload, chat, authentication
- `/frontend`: Next.js app, PDF upload, chat interface, authentication

## Features
- PDF upload and text extraction
- Chat with local LLM about PDF content
- User authentication (JWT)
- Chat history

## Setup

### Backend
1. Create and activate a Python virtual environment:
   ```powershell
   cd backend
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. Download a compatible Llama model and update the path in `llm.py`.
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
- Register and login via the frontend.
- Upload PDFs and chat about their content.
- All data is stored locally in SQLite.

## Notes
- Update the LLM model path in `backend/llm.py` as needed.
- For production, change the JWT secret key and use secure deployment practices.
