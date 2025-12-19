import faiss
import numpy as np
import gc

def _get_embedding_model():
    """Lazy load embedding model only when needed (saves ~300MB memory)."""
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("all-MiniLM-L6-v2")

def build_index(text_chunks):
    model = _get_embedding_model()
    try:
        embeddings = model.encode(text_chunks, convert_to_numpy=True)
        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(embeddings)
        return index, embeddings
    finally:
        # Free model memory immediately after use
        del model
        gc.collect()

