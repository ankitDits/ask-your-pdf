from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from jose import jwt
import hashlib
import os
from PyPDF2 import PdfReader
from models import init_db, get_db
from llm import ask
from cors_middleware import add_cors # type: ignore
from vector_db import add_pdf_chunks, query_pdf_chunks
import logging

app = FastAPI()
add_cors(app)

# Initialize the database
init_db()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pdf_chatbot")

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
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        try:
            reader = PdfReader(file_path)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as e:
            logger.exception("Failed to read PDF: %s", e)
            raise HTTPException(status_code=400, detail="Failed to read the uploaded PDF.")
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO pdfs (user_id, filename, filepath, extracted_text) VALUES (?, ?, ?, ?)",
            (user_id, file.filename, file_path, text)
        )
        conn.commit()
        pdf_id = cursor.lastrowid
        conn.close()
        try:
            add_pdf_chunks(pdf_id, text) # type: ignore
        except Exception as e:
            logger.exception("Embedding add_pdf_chunks failed: %s", e)
            return {"pdf_id": pdf_id, "filename": file.filename, "text_preview": text[:200], "warning": "Failed to index PDF content for search."} # type: ignore
        return {"pdf_id": pdf_id, "filename": file.filename, "text_preview": text[:200]} # type: ignore
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Upload failed: %s", e)
        raise HTTPException(status_code=500, detail="Upload failed due to an internal error.")

@app.post("/register")
def register(user: UserCreate):
    conn = get_db()
    cursor = conn.cursor()
    hashed_pw = hashlib.sha256(user.password.encode()).hexdigest()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (user.username, hashed_pw))
        conn.commit()
        return {"message": "User registered successfully."}
    except Exception:
        raise HTTPException(status_code=400, detail="Username already exists.")
    finally:
        conn.close()

@app.post("/login")
def login(user: UserLogin):
    try:
        conn = get_db()
        cursor = conn.cursor()
        hashed_pw = hashlib.sha256(user.password.encode()).hexdigest()
        cursor.execute("SELECT id FROM users WHERE username=? AND password=?", (user.username, hashed_pw))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=401, detail="Invalid credentials.")
        token = jwt.encode({"user_id": row["id"]}, SECRET_KEY, algorithm=ALGORITHM)
        return {"access_token": token, "token_type": "bearer"}
    finally:
        conn.close()

@app.get("/pdfs")
def list_pdfs(user_id: int):
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, filename FROM pdfs WHERE user_id=?", (user_id,))
        pdfs = cursor.fetchall()
        return [{"id": pdf["id"], "filename": pdf["filename"]} for pdf in pdfs]
    finally:
        conn.close()

@app.post("/chat")
def chat(request: ChatRequest):
    try:
        print('abcd')
        user_id = request.user_id
        pdf_id = request.pdf_id
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM pdfs WHERE id=? AND user_id=?", (pdf_id, user_id))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="PDF not found.")
        cursor.execute(
            "INSERT INTO user_facts (user_id, pdf_id, fact) VALUES (?, ?, ?)",
            (user_id, pdf_id, request.question)
        )
        conn.commit()
        cursor.execute(
            "SELECT fact FROM user_facts WHERE user_id=? AND pdf_id=?",
            (user_id, pdf_id)
        )
        facts = [row[0] for row in cursor.fetchall()]
        conn.close()
        try:
            relevant_chunks = query_pdf_chunks(pdf_id, request.question, top_k=3)
        except Exception as e:
            logger.exception("Vector DB query failed: %s", e)
            relevant_chunks = []
        context = "\n\n".join(relevant_chunks)
        if facts:
            context = "User Facts:\n" + "\n".join(facts) + "\n\n" + context
        prompt = f"{context}\n\nQuestion: {request.question}\nAnswer:"
        answer = ask(system_prompt="You are a helpful assistant.", user_prompt=prompt)
        if answer.startswith("[Error]") or answer.startswith("[LLM error]"):
            raise HTTPException(status_code=502, detail="LLM failed to generate a response.")
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chats (user_id, pdf_id, question, answer) VALUES (?, ?, ?, ?)",
            (user_id, pdf_id, request.question, answer)
        )
        conn.commit()
        conn.close()
        return {"answer": answer}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Chat failed: %s", e)
        raise HTTPException(status_code=500, detail="Chat failed due to an internal error.")

@app.get("/chats")
def get_chats(user_id: int, pdf_id: int):
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT question, answer, timestamp FROM chats WHERE user_id=? AND pdf_id=? ORDER BY timestamp DESC", (user_id, pdf_id))
        chats = cursor.fetchall()
        return [{"question": chat["question"], "answer": chat["answer"], "timestamp": chat["timestamp"]} for chat in chats]
    finally:
        conn.close()

@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError): # type: ignore
    return JSONResponse(status_code=422, content={"detail": exc.errors()})

@app.exception_handler(Exception)
def unhandled_exception_handler(request: Request, exc: Exception): # type: ignore
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})
