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


def compute_weighted_score(scores: dict, domain: str) -> float:
    """
    Compute weighted score based on domain-specific weights.
    
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
            # score_data can be either a dict like {"score": 8, "summary": "..."} or just a number
            if isinstance(score_data, dict):
                score = score_data.get("score", 0)
            else:
                score = score_data
            
            weighted_sum += score * weights[criterion]
            total_weight += weights[criterion]
    
    # Normalize by total weight to handle missing criteria
    if total_weight > 0:
        return weighted_sum / total_weight
    else:
        # Fallback to simple average, handling dict structure
        score_values = []
        for score_data in scores.values():
            if isinstance(score_data, dict):
                score_values.append(score_data.get("score", 0))
            else:
                score_values.append(score_data)
        return sum(score_values) / len(score_values) if score_values else 0.0
