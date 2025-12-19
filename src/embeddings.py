from langchain_huggingface import HuggingFaceEmbeddings
import yaml
import os
import gc

_embeddings_cache = None

def get_embedder(config_path="config.yaml"):
    """
    Get embeddings model with memory-efficient lazy loading.
    Uses a lightweight model (all-MiniLM-L6-v2, ~80MB) and caches it to avoid reloading.
    """
    global _embeddings_cache
    
    # Return cached embeddings if available
    if _embeddings_cache is not None:
        return _embeddings_cache
    
    try:
        # Load config to check if custom model specified
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        model_name = config.get("embeddings", {}).get("model_name", "sentence-transformers/all-MiniLM-L6-v2")
    except:
        # Default to lightweight model (~80MB)
        model_name = "sentence-transformers/all-MiniLM-L6-v2"
    
    print(f"[INFO] Loading embeddings model: {model_name} (cached for session)")
    
    # Use lightweight model with minimal memory footprint
    embedder = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={'device': 'cpu'},  # Force CPU to avoid GPU memory
        encode_kwargs={'normalize_embeddings': True, 'batch_size': 32}
    )
    
    # Cache for reuse during session
    _embeddings_cache = embedder
    return embedder

def cleanup_embeddings():
    """Clean up embeddings cache to free memory after evaluation."""
    global _embeddings_cache
    if _embeddings_cache is not None:
        del _embeddings_cache
        _embeddings_cache = None
        gc.collect()
        print("[INFO] Embeddings cache cleaned up")