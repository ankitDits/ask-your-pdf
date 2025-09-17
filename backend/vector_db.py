import chromadb # type: ignore
from sentence_transformers import SentenceTransformer # type: ignore

CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "pdf_chunks"
EMBED_MODEL = "all-MiniLM-L6-v2"

client = chromadb.PersistentClient(path=CHROMA_DIR) # type: ignore
model = SentenceTransformer(EMBED_MODEL) # type: ignore

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
    embeddings = model.encode(chunks).tolist() # type: ignore
    collection.add(documents=chunks, metadatas=metadatas, ids=ids, embeddings=embeddings) # type: ignore

def query_pdf_chunks(pdf_id: int, question: str, top_k: int = 3): # type: ignore
    collection = get_collection()
    question_emb = model.encode([question]).tolist()[0]
    results = collection.query(
        query_embeddings=[question_emb],
        n_results=top_k,
        where={"pdf_id": pdf_id}
    )
    return results["documents"][0] if results["documents"] else []
