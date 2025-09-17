from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from pydantic import BaseModel
from jose import jwt
import hashlib
import os
from PyPDF2 import PdfReader
from models import init_db, get_db
from llm import LocalLLM
from cors_middleware import add_cors # type: ignore
from vector_db import add_pdf_chunks, query_pdf_chunks

app = FastAPI()
add_cors(app)

# Initialize the database
init_db()

UPLOAD_DIR = "uploaded_pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

SECRET_KEY = "your-secret-key"  # Change this in production
ALGORITHM = "HS256"

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class ChatRequest(BaseModel):
    pdf_id: int
    question: str
    user_id: int

@app.get("/")
def read_root():
    return {"message": "PDF Chatbot Backend is running."}

@app.post("/upload_pdf")
def upload_pdf(user_id: int = Form(...), file: UploadFile = File(...)): # type: ignore
    if not file.filename or not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    # Extract text from PDF
    reader = PdfReader(file_path)
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    # Save PDF info to DB
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO pdfs (user_id, filename, filepath, extracted_text) VALUES (?, ?, ?, ?)",
        (user_id, file.filename, file_path, text)
    )
    conn.commit()
    pdf_id = cursor.lastrowid
    conn.close()
    # Add PDF chunks to Chroma vector DB
    add_pdf_chunks(pdf_id, text) # type: ignore
    return {"pdf_id": pdf_id, "filename": file.filename, "text_preview": text[:200]} # type: ignore

@app.post("/register")
def register(user: UserCreate):
    conn = get_db()
    cursor = conn.cursor()
    hashed_pw = hashlib.sha256(user.password.encode()).hexdigest()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (user.username, hashed_pw))
        conn.commit()
    except Exception:
        conn.close()
        raise HTTPException(status_code=400, detail="Username already exists.")
    conn.close()
    return {"message": "User registered successfully."}

@app.post("/login")
def login(user: UserLogin):
    conn = get_db()
    cursor = conn.cursor()
    hashed_pw = hashlib.sha256(user.password.encode()).hexdigest()
    cursor.execute("SELECT id FROM users WHERE username=? AND password=?", (user.username, hashed_pw))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    token = jwt.encode({"user_id": row["id"]}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

@app.get("/pdfs")
def list_pdfs(user_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, filename FROM pdfs WHERE user_id=?", (user_id,))
    pdfs = cursor.fetchall()
    conn.close()
    return [{"id": pdf["id"], "filename": pdf["filename"]} for pdf in pdfs]

@app.post("/chat")
def chat(request: ChatRequest):
    user_id = request.user_id
    pdf_id = request.pdf_id
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM pdfs WHERE id=? AND user_id=?", (pdf_id, user_id))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="PDF not found.")
    # Save any user statement as a fact
    cursor.execute(
        "INSERT INTO user_facts (user_id, pdf_id, fact) VALUES (?, ?, ?)",
        (user_id, pdf_id, request.question)
    )
    conn.commit()
    # Retrieve all facts for context
    cursor.execute(
        "SELECT fact FROM user_facts WHERE user_id=? AND pdf_id=?",
        (user_id, pdf_id)
    )
    facts = [row[0] for row in cursor.fetchall()]
    conn.close()
    # Semantic search for relevant chunks
    relevant_chunks = query_pdf_chunks(pdf_id, request.question, top_k=3)
    context = "\n\n".join(relevant_chunks)
    # Add facts to context
    if facts:
        context = "User Facts:\n" + "\n".join(facts) + "\n\n" + context
    llm = LocalLLM()
    prompt = f"{context}\n\nQuestion: {request.question}\nAnswer:"
    answer = llm.ask(prompt)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chats (user_id, pdf_id, question, answer) VALUES (?, ?, ?, ?)",
        (user_id, pdf_id, request.question, answer)
    )
    conn.commit()
    conn.close()
    return {"answer": answer}

@app.get("/chats")
def get_chats(user_id: int, pdf_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT question, answer, timestamp FROM chats WHERE user_id=? AND pdf_id=? ORDER BY timestamp DESC", (user_id, pdf_id))
    chats = cursor.fetchall()
    conn.close()
    return [{"question": chat["question"], "answer": chat["answer"], "timestamp": chat["timestamp"]} for chat in chats]
