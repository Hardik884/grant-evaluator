DOMAIN_WEIGHTS = {
    "AI / Computer Science": {
        "Objectives": 0.15,
        "Methodology": 0.25,
        "Innovation": 0.30,
        "Feasibility": 0.15,
        "Budget": 0.10,
        "Sustainability": 0.05
    },
    "Biotechnology / Life Sciences": {
        "Objectives": 0.10,
        "Methodology": 0.30,
        "Innovation": 0.20,
        "Feasibility": 0.25,
        "Budget": 0.10,
        "Sustainability": 0.05
    },
    "Healthcare / Medicine": {
        "Objectives": 0.15,
        "Methodology": 0.25,
        "Innovation": 0.15,
        "Feasibility": 0.30,
        "Budget": 0.10,
        "Sustainability": 0.05
    },
    "Education / Learning Sciences": {
        "Objectives": 0.25,
        "Methodology": 0.20,
        "Innovation": 0.10,
        "Feasibility": 0.25,
        "Budget": 0.10,
        "Sustainability": 0.10
    },
    "Environment / Climate / Sustainability": {
        "Objectives": 0.20,
        "Methodology": 0.20,
        "Innovation": 0.15,
        "Feasibility": 0.20,
        "Budget": 0.10,
        "Sustainability": 0.15
    },
    "Social Sciences / Policy": {
        "Objectives": 0.30,
        "Methodology": 0.20,
        "Innovation": 0.10,
        "Feasibility": 0.20,
        "Budget": 0.10,
        "Sustainability": 0.10
    },
    "Engineering / Technology": {
        "Objectives": 0.15,
        "Methodology": 0.25,
        "Innovation": 0.25,
        "Feasibility": 0.20,
        "Budget": 0.10,
        "Sustainability": 0.05
    },
    "Physics / Materials Science": {
        "Objectives": 0.10,
        "Methodology": 0.30,
        "Innovation": 0.25,
        "Feasibility": 0.20,
        "Budget": 0.10,
        "Sustainability": 0.05
    },
    "Chemistry / Chemical Engineering": {
        "Objectives": 0.10,
        "Methodology": 0.30,
        "Innovation": 0.20,
        "Feasibility": 0.25,
        "Budget": 0.10,
        "Sustainability": 0.05
    },
    "Agriculture / Food Science": {
        "Objectives": 0.15,
        "Methodology": 0.25,
        "Innovation": 0.15,
        "Feasibility": 0.25,
        "Budget": 0.10,
        "Sustainability": 0.10
    },
    "Energy / Renewable Resources": {
        "Objectives": 0.20,
        "Methodology": 0.20,
        "Innovation": 0.20,
        "Feasibility": 0.20,
        "Budget": 0.10,
        "Sustainability": 0.10
    },
    "Economics / Business": {
        "Objectives": 0.25,
        "Methodology": 0.20,
        "Innovation": 0.10,
        "Feasibility": 0.25,
        "Budget": 0.15,
        "Sustainability": 0.05
    },
    "Arts / Humanities": {
        "Objectives": 0.30,
        "Methodology": 0.15,
        "Innovation": 0.20,
        "Feasibility": 0.20,
        "Budget": 0.10,
        "Sustainability": 0.05
    },
    "Psychology / Behavioral Sciences": {
        "Objectives": 0.20,
        "Methodology": 0.30,
        "Innovation": 0.10,
        "Feasibility": 0.25,
        "Budget": 0.10,
        "Sustainability": 0.05
    },
    "Urban Planning / Architecture": {
        "Objectives": 0.20,
        "Methodology": 0.20,
        "Innovation": 0.15,
        "Feasibility": 0.25,
        "Budget": 0.10,
        "Sustainability": 0.10
    },
    "Data Science / Statistics": {
        "Objectives": 0.15,
        "Methodology": 0.30,
        "Innovation": 0.20,
        "Feasibility": 0.20,
        "Budget": 0.10,
        "Sustainability": 0.05
    },
    "Cybersecurity / Information Security": {
        "Objectives": 0.15,
        "Methodology": 0.25,
        "Innovation": 0.25,
        "Feasibility": 0.20,
        "Budget": 0.10,
        "Sustainability": 0.05
    },
    "Public Health / Epidemiology": {
        "Objectives": 0.20,
        "Methodology": 0.25,
        "Innovation": 0.10,
        "Feasibility": 0.30,
        "Budget": 0.10,
        "Sustainability": 0.05
    },
    "Space Science / Astronomy": {
        "Objectives": 0.15,
        "Methodology": 0.30,
        "Innovation": 0.25,
        "Feasibility": 0.15,
        "Budget": 0.10,
        "Sustainability": 0.05
    },
    "Marine Biology / Oceanography": {
        "Objectives": 0.15,
        "Methodology": 0.25,
        "Innovation": 0.15,
        "Feasibility": 0.25,
        "Budget": 0.10,
        "Sustainability": 0.10
    },
    "Neuroscience / Cognitive Science": {
        "Objectives": 0.10,
        "Methodology": 0.35,
        "Innovation": 0.20,
        "Feasibility": 0.20,
        "Budget": 0.10,
        "Sustainability": 0.05
    }
}


def compute_section_weighted_score(scores: dict, domain: str) -> float:
    """
    Compute weighted score for SECTION scores only (content evaluation).
    
    Args:
        scores: Dictionary of criterion scores (e.g., {"Objectives": 8.5, "Methodology": 7.0, ...})
        domain: The domain/category of the grant proposal
    
    Returns:
        Weighted average score (0-10 scale)
    """
    if domain not in DOMAIN_WEIGHTS:
        # Default to equal weights if domain not found
        weights = {k: 1.0 / len(scores) for k in scores.keys()}
    else:
        weights = DOMAIN_WEIGHTS[domain]
    
    weighted_sum = 0.0
    total_weight = 0.0
    
    for criterion, score_data in scores.items():
        if criterion in weights:
            # Extract numeric score from dict structure
            if isinstance(score_data, dict):
                score = score_data.get("score", 0)
            else:
                score = score_data
            
            weight = weights[criterion]
            contribution = score * weight
            weighted_sum += contribution
            total_weight += weight
    
    # Normalize by total weight to handle missing criteria
    if total_weight > 0:
        section_score = weighted_sum / total_weight
        return section_score
    else:
        # Fallback to simple average
        score_values = []
        for score_data in scores.values():
            if isinstance(score_data, dict):
                score_values.append(score_data.get("score", 0))
            else:
                score_values.append(score_data)
        return sum(score_values) / len(score_values) if score_values else 0.0


def compute_critique_average(critique_domains: list) -> float:
    """
    Compute average of critique domain scores (quality evaluation).
    
    Args:
        critique_domains: List of critique domain scores [{"domain": "Scientific", "score": 7.5}, ...]
    
    Returns:
        Average critique score (0-10 scale)
    """
    if not critique_domains or not isinstance(critique_domains, list):
        return 0.0
    
    scores = [d.get("score", 0) for d in critique_domains if isinstance(d, dict) and "score" in d]
    
    avg_score = sum(scores) / len(scores) if scores else 0.0
    
    return avg_score


def compute_weighted_score(scores: dict, domain: str, critique_domains: list = None) -> float:
    """
    Compute comprehensive final score combining section scores and critique scores.
    
    SCORING FORMULA:
    Final Score = (Section Score × 0.60) + (Critique Score × 0.40)
    
    - Section Score (60%): Domain-weighted evaluation of proposal content
      (Objectives, Methodology, Innovation, Feasibility, Budget, etc.)
    
    - Critique Score (40%): Quality assessment across critique dimensions
      (Scientific Rigor, Practical Feasibility, Language, Context, etc.)
    
    This balanced approach ensures both WHAT is proposed (content) and 
    HOW WELL it's presented (quality) contribute to the final evaluation.
    
    Args:
        scores: Dictionary of section scores
        domain: The domain/category of the grant proposal
        critique_domains: List of critique domain scores (optional)
    
    Returns:
        Comprehensive final score (0-10 scale)
    """
    # Calculate section-weighted score (content evaluation)
    section_score = compute_section_weighted_score(scores, domain)
    
    # If no critique data, use section score only
    if not critique_domains:
        return section_score
    
    # Calculate critique average (quality evaluation)
    critique_score = compute_critique_average(critique_domains)
    
    # Combined formula: 60% content + 40% quality
    SECTION_WEIGHT = 0.60
    CRITIQUE_WEIGHT = 0.40
    
    final_score = (section_score * SECTION_WEIGHT) + (critique_score * CRITIQUE_WEIGHT)
    
    return final_score


# Backward compatibility alias
def compute_weighted_score_legacy(scores: dict, domain: str) -> float:
    """Legacy function for backward compatibility - uses section scores only"""
    return compute_section_weighted_score(scores, domain)
