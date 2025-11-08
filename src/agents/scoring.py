from src.llm_wrapper import gemini_llm
import json
from src.prompts import SCORING_PROMPT
import re

def strip_codeblock(text: str) -> str:
    """
    Remove Markdown-style code block wrappers (```json ... ```) if present.
    """
    return re.sub(r"^```(?:json)?\n|```$", "", text.strip(), flags=re.MULTILINE)


def repair_json(text: str) -> str:
    """
    Attempt to repair common JSON issues like unterminated strings.
    """
    # Try to find where the JSON actually ends
    # Look for the last complete object before truncation
    
    # If there's an unterminated string, try to close it
    if text.count('"') % 2 != 0:
        # Find the last quote and add a closing quote
        text = text + '"'
    
    # Count braces to see if we need to close them
    open_braces = text.count('{')
    close_braces = text.count('}')
    if open_braces > close_braces:
        text = text + ('}' * (open_braces - close_braces))
    
    # Count brackets
    open_brackets = text.count('[')
    close_brackets = text.count(']')
    if open_brackets > close_brackets:
        text = text + (']' * (open_brackets - close_brackets))
    
    return text


def run_grant_scoring(summary_json, domain: str):
    """
    Pass a structured grant summary JSON to Gemini LLM and get section-wise scores.
    NOTE: These scores are *raw* — adaptive weighting happens later in backend.
    """
    # Convert summary to JSON string for the prompt
    grant_json_str = json.dumps(summary_json, indent=2)

    # Prepare full prompt WITH DOMAIN CONTEXT
    prompt = SCORING_PROMPT.format(grant_json=grant_json_str, domain=domain)

    # Call Gemini LLM with increased token limit for complete JSON
    response = gemini_llm(prompt, max_output_tokens=8192)

    cleaned_response = strip_codeblock(response)

    # Parse JSON safely
    try:
        scores_json = json.loads(cleaned_response)
        
        # Validate expected structure
        if not isinstance(scores_json, dict):
            raise ValueError("Expected dict from scoring agent")
        
        # Check if "scores" key is missing - try to detect if it's a flat structure
        if "scores" not in scores_json:
            # Check if this looks like section scores directly (has section names)
            section_names = ["Objectives", "Methodology", "Budget", "Innovation", "Impact", 
                           "Feasibility", "Background", "Timeline", "Team", "Sustainability"]
            
            if any(section in scores_json for section in section_names):
                # Wrap flat structure into expected format
                scores_json = {
                    "scores": scores_json,
                    "overall_summary": scores_json.get("overall_summary", "")
                }
            else:
                # If neither "scores" key nor section names found, this is malformed
                raise ValueError("Response has neither 'scores' key nor section names")
            
    except (json.JSONDecodeError, ValueError) as e:
        # Try to repair the JSON
        try:
            repaired = repair_json(cleaned_response)
            scores_json = json.loads(repaired)
            
            # Validate repaired JSON also has proper structure
            if "scores" not in scores_json:
                section_names = ["Objectives", "Methodology", "Budget", "Innovation", "Impact"]
                if any(section in scores_json for section in section_names):
                    scores_json = {
                        "scores": scores_json,
                        "overall_summary": scores_json.get("overall_summary", "")
                    }
                else:
                    raise ValueError("Repaired JSON still malformed")
                    
        except Exception as repair_error:
            # Last resort: Return minimal valid structure to prevent crash
            # Initialize with default sections based on common grant structure
            scores_json = {
                "scores": {
                    "Objectives": {"score": 0.0, "feedback": "Error: Unable to parse LLM response"},
                    "Methodology": {"score": 0.0, "feedback": "Error: Unable to parse LLM response"},
                    "Budget": {"score": 0.0, "feedback": "Error: Unable to parse LLM response"},
                    "Impact": {"score": 0.0, "feedback": "Error: Unable to parse LLM response"},
                },
                "overall_summary": "Error: LLM returned invalid JSON - please retry evaluation",
                "raw_response": cleaned_response[:1000]  # Truncate to avoid huge error messages
            }

    return scores_json


from src.config.domain_weights import DOMAIN_WEIGHTS

def compute_weighted_score(section_scores: dict, domain: str) -> float:
    weights = DOMAIN_WEIGHTS.get(domain)
    if not weights:
        raise ValueError(f"No weight configuration found for domain: {domain}")

    score = 0
    for section, data in section_scores.items():
        if section in weights:
            score += data["score"] * weights[section]

    return round(score, 2)
