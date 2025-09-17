# Backend2 - Custom FastAPI PDF Chatbot

This backend implements a PDF chatbot using FastAPI, Chroma vector database, and a local Mistral LLM (via Ollama).

## Features
- Upload PDF files via `/upload_pdf` endpoint
- Extracts and splits PDF text into chunks
- Embeds chunks using Sentence Transformers
- Stores embeddings in Chroma vector database
- Ask questions about uploaded PDFs via `/ask_question` endpoint
- Performs semantic search over PDF chunks
- Uses Mistral LLM (Ollama) to generate answers from matched chunks

## Endpoints
- `POST /upload_pdf` — Upload a PDF, process, embed, and store in vector DB
- `POST /ask_question` — Ask a question about a specific PDF, get LLM answer

## Setup
1. Install dependencies:
   ```powershell
   cd backend2
   pip install -r requirements.txt
   ```
2. Start Ollama and pull the Mistral model:
   ```powershell
   ollama pull mistral
   ollama serve
   ```
3. Start the FastAPI server:
   ```powershell
   uvicorn main:app --reload
   ```

## Usage
- Upload a PDF using `/upload_pdf` (form-data, file field)
- Ask questions using `/ask_question` (JSON: `{ "filename": "your.pdf", "question": "..." }`)

## Notes
- PDF files are saved in `uploaded_pdfs2/`
- Chroma vector DB is used for semantic search
- Requires Ollama running with Mistral model for LLM answers
