import os
import chromadb # type: ignore
import google.generativeai as genai # type: ignore

CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "pdf_chunks"
EMBED_MODEL = "models/text-embedding-004"

client = chromadb.PersistentClient(path=CHROMA_DIR) # type: ignore

# Configure Gemini embeddings
_GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
if not _GOOGLE_API_KEY:
    raise RuntimeError("GOOGLE_API_KEY (or GEMINI_API_KEY) not set for embeddings.")
genai.configure(api_key=_GOOGLE_API_KEY)

def _embed_text(text: str):
    resp = genai.embed_content(model=EMBED_MODEL, content=text)
    # Response shape: { 'embedding': [..] }
    return resp["embedding"]

def get_collection(): # type: ignore
    try:
        return client.get_collection(COLLECTION_NAME) # type: ignore
    except Exception:
        return client.create_collection(COLLECTION_NAME) # type: ignore

def add_pdf_chunks(pdf_id: int, text: str):
    collection = get_collection() # type: ignore
    # Split text into chunks (e.g., 1000 chars)
    chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
    metadatas = [{"pdf_id": pdf_id, "chunk_idx": idx} for idx in range(len(chunks))]
    ids = [f"{pdf_id}_{idx}" for idx in range(len(chunks))]
    embeddings = [_embed_text(chunk) for chunk in chunks] # type: ignore
    collection.add(documents=chunks, metadatas=metadatas, ids=ids, embeddings=embeddings) # type: ignore

def query_pdf_chunks(pdf_id: int, question: str, top_k: int = 3): # type: ignore
    collection = get_collection()
    question_emb = _embed_text(question)
    results = collection.query(
        query_embeddings=[question_emb],
        n_results=top_k,
        where={"pdf_id": pdf_id}
    )
    return results["documents"][0] if results["documents"] else []
