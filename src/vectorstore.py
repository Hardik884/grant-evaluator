from langchain_community.vectorstores import Chroma
import os
import shutil
import uuid
from langchain.schema import Document

def create_vectorstore(docs: list[Document], embeddings, persist_dir=None):
    """
    Create a Chroma vectorstore from Document objects with metadata.
    
    If persist_dir is None, creates an in-memory vectorstore (recommended for evaluation isolation).
    If persist_dir is provided, persists to that directory.
    
    ISOLATION: Each vectorstore gets a unique collection name to prevent contamination.
    """
    if persist_dir is None:
        # In-memory mode with unique collection name for complete isolation
        unique_collection_name = f"eval_{uuid.uuid4().hex[:16]}"
        
        db = Chroma.from_documents(
            documents=docs,
            embedding=embeddings,
            collection_name=unique_collection_name
        )
    else:
        # Persistent mode
        os.makedirs(persist_dir, exist_ok=True)
        
        unique_collection_name = f"eval_{uuid.uuid4().hex[:16]}"
        
        db = Chroma.from_documents(
            documents=docs,        # <-- preserve text + metadata
            embedding=embeddings,  
            persist_directory=persist_dir,
            collection_name=unique_collection_name
        )
    return db


def cleanup_vectorstore(persist_dir):
    """
    Delete a vectorstore directory to prevent contamination between evaluations.
    """
    if persist_dir and os.path.exists(persist_dir):
        try:
            shutil.rmtree(persist_dir)
        except Exception as e:
            print(f"[WARNING] Could not clean up vectorstore at {persist_dir}: {e}")


def load_vectorstore(embedding, persist_dir="data/vectorstore"):
    """
    Load an existing Chroma vectorstore from disk.
    """
    db = Chroma(
        embedding_function=embedding,  # LangChain embedding object
        persist_directory=persist_dir
    )
    return db