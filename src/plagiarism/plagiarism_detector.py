import numpy as np
import gc
from .reference_loader import load_reference_corpus

def _get_plagiarism_model():
    """Lazy load plagiarism model only when needed (saves ~300MB memory)."""
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("all-MiniLM-L6-v2")

def detect_plagiarism(proposal_text: str):
    """
    Detect plagiarism by comparing proposal chunks against reference corpus.
    Uses chunk-based approach to find localized similarities rather than entire document comparison.
    """
    reference_texts = load_reference_corpus()
    
    # Split proposal into chunks (paragraphs or sentences)
    # This prevents entire document comparison which inflates similarity scores
    chunks = [chunk.strip() for chunk in proposal_text.split('\n\n') if len(chunk.strip()) > 50]
    
    if not chunks:
        # Fallback to sentence-level splitting if no paragraphs
        chunks = [sent.strip() for sent in proposal_text.split('.') if len(sent.strip()) > 30]
    
    if not chunks:
        return {
            "similarity_score": 0.0,
            "matched_reference_text": "No content to analyze",
            "risk_level": "LOW"
        }
    
    # Load model only when needed
    model = _get_plagiarism_model()
    
    try:
        # Encode chunks and references
        chunk_embs = model.encode(chunks, convert_to_numpy=True)
        ref_embs = model.encode(reference_texts, convert_to_numpy=True)
        
        # Find maximum similarity for each chunk
        max_similarities = []
        matched_chunks = []
        
        for i, chunk_emb in enumerate(chunk_embs):
            # Cosine similarity with all references
            sims = (chunk_emb @ ref_embs.T) / (
                np.linalg.norm(chunk_emb) * np.linalg.norm(ref_embs, axis=1)
            )
            max_sim = float(np.max(sims))
            max_similarities.append(max_sim)
            
            # Track highly similar chunks (potential plagiarism)
            if max_sim > 0.80:  # Only chunks with very high similarity
                best_match_idx = int(np.argmax(sims))
                matched_chunks.append({
                    "chunk": chunks[i][:100],  # First 100 chars
                    "similarity": max_sim,
                    "reference": reference_texts[best_match_idx][:100]
                })
        
        # Calculate overall similarity score
        # Use top 10% of chunks to avoid inflation from common phrases
        top_k = max(1, len(max_similarities) // 10)
        top_similarities = sorted(max_similarities, reverse=True)[:top_k]
        avg_top_similarity = np.mean(top_similarities)
        
        # More strict thresholds for risk levels
        # Only flag as HIGH if multiple chunks have very high similarity
        high_sim_count = sum(1 for sim in max_similarities if sim > 0.85)
        
        if high_sim_count >= 3 or avg_top_similarity > 0.90:
            risk_level = "HIGH"
        elif high_sim_count >= 1 or avg_top_similarity > 0.80:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        # Find the most similar chunk for reporting
        best_chunk_idx = int(np.argmax(max_similarities))
        best_score = max_similarities[best_chunk_idx]
        
        # Get the reference that matched best
        chunk_emb = chunk_embs[best_chunk_idx]
        sims = (chunk_emb @ ref_embs.T) / (
            np.linalg.norm(chunk_emb) * np.linalg.norm(ref_embs, axis=1)
        )
        best_ref_idx = int(np.argmax(sims))
        
        return {
            "similarity_score": round(avg_top_similarity, 3),
            "max_chunk_similarity": round(best_score, 3),
            "high_similarity_chunks": high_sim_count,
            "total_chunks_analyzed": len(chunks),
            "matched_reference_text": reference_texts[best_ref_idx][:200] + "...",
            "risk_level": risk_level
        }
    finally:
        # Free model memory immediately after use
        del model
        gc.collect()
