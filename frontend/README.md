
# Frontend (Next.js)

Modern Next.js (React, TypeScript) UI for PDF chatbot.

## Features
- Register, login, logout
- Upload PDFs
- Chat with LLM about PDF content (semantic search, memory)
- View chat history per PDF
- Responsive, modern design
- Secure: users only see their own PDFs and chats

## Pages
- `/login` - Login page
- `/register` - Register page
- `/dashboard` - Upload/view PDFs
- `/chat/[pdf_id]` - Chat about a PDF (semantic search + memory)

## Setup
1. Install dependencies:
   ```powershell
   npm install
   ```
2. Run the development server:
   ```powershell
   npm run dev
   ```

## Usage
1. Register and login
2. Upload PDFs and chat about their content
3. View chat history for each PDF
4. Logout securely when done

## Notes
- Connects to FastAPI backend at `https://687c699d555b.ngrok-free.app`
- Requires backend and Ollama server running
- Update API URLs in `src/api/` if backend port changes
