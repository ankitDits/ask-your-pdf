from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import os
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter # type: ignore
from sentence_transformers import SentenceTransformer # type: ignore
import chromadb # type: ignore

app = FastAPI()

UPLOAD_DIR = "uploaded_pdfs2"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize Chroma client and collection
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection("pdf_chunks2")

# Load embedding model once
embedder = SentenceTransformer("all-MiniLM-L6-v2")

@app.get("/")
def read_root():
    return {"message": "Hello from backend2 FastAPI!"}


@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):
    # Save PDF to disk
    file_location = os.path.join(UPLOAD_DIR, file.filename) # type: ignore
    with open(file_location, "wb") as f:
        f.write(await file.read())

    # Load PDF and extract text
    reader = PdfReader(file_location)
    text = "\n".join(page.extract_text() or "" for page in reader.pages)

    # Split text into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(text)

    # Create embeddings
    embeddings = embedder.encode(chunks).tolist()

    # Store in Chroma vector DB
    ids = [f"{file.filename}_chunk_{i}" for i in range(len(chunks))]
    collection.add(documents=chunks, embeddings=embeddings, ids=ids, metadatas=[{"filename": file.filename}]*len(chunks))

    return JSONResponse({"message": "PDF uploaded, processed, and embedded successfully.", "chunks": len(chunks)})


# --- New endpoint for question answering ---
from pydantic import BaseModel
import requests

class AskRequest(BaseModel):
    filename: str
    question: str

@app.post("/ask_question")
def ask_question(data: AskRequest):
    # Embed the question
    question_embedding = embedder.encode([data.question]).tolist()[0]

    # Semantic search in Chroma for this PDF
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=5,
        where={"filename": data.filename}
    )
    # Get matched chunks
    matched_chunks = [doc for doc in results.get("documents", [[]])[0]]

    # Compose prompt for Mistral
    context = "\n".join(matched_chunks)
    prompt = f"Answer the following question based on the PDF context below.\n\nContext:\n{context}\n\nQuestion: {data.question}\nAnswer:"

    # Call local Mistral model via Ollama REST API
    ollama_url = "http://localhost:11434/api/generate"
    payload = {
        "model": "mistral",
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(ollama_url, json=payload, timeout=60)
        response.raise_for_status()
        answer = response.json().get("response", "No answer returned.")
    except Exception as e:
        answer = f"Error contacting LLM: {e}"

    return {"answer": answer, "matched_chunks": matched_chunks}
