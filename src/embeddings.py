from langchain_huggingface import HuggingFaceEndpointEmbeddings
import os

def get_embedder(config_path="config.yaml"):
    """
    Get embeddings using HuggingFace Inference API (zero memory, API-based).
    
    Uses HUGGINGFACE_API_KEY from environment.
    Free tier: 1000 requests/day (much higher than Google's free tier)
    
    Memory usage: ~0 MB (API calls only, no model loading)
    
    Get free API key from: https://huggingface.co/settings/tokens
    """
    hf_token = os.getenv("HUGGINGFACE_API_KEY") or os.getenv("HF_TOKEN")
    
    if not hf_token:
        raise ValueError(
            "HUGGINGFACE_API_KEY not found in environment.\n"
            "Get free API key from https://huggingface.co/settings/tokens\n"
            "Add it to Render environment variables as HUGGINGFACE_API_KEY"
        )
    
    print(f"[INFO] Using HuggingFace Inference API embeddings (zero memory, free tier)")
    
    try:
        # Use sentence-transformers model via API (no local loading)
        embedder = HuggingFaceEndpointEmbeddings(
            model="sentence-transformers/all-MiniLM-L6-v2",
            huggingfacehub_api_token=hf_token
        )
        return embedder
    except Exception as e:
        print(f"[ERROR] Failed to initialize HuggingFace embeddings: {e}")
        print("[INFO] Make sure HUGGINGFACE_API_KEY is set in Render environment")
        raise

def cleanup_embeddings():
    """No cleanup needed for API-based embeddings."""
    pass