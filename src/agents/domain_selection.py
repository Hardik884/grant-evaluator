# src/agents/domain_classifier.py

from src.llm_wrapper import gemini_llm
from src.prompts import DOMAIN_CLASSIFIER_PROMPT
import re

def strip_response(text: str) -> str:
    """
    Clean LLM output to extract a simple string domain label.
    """
    text = text.strip()
    text = re.sub(r"```(?:.*)?```", "", text)  # remove accidental codeblocks
    return text.split("\n")[0].strip()  # only keep first non-empty line

def classify_domain(proposal_text: str) -> str:
    """
    Classify proposal into a domain using the LLM.
    Truncates input to avoid API errors with large documents.
    """
    # Limit to first 5000 characters (usually enough for classification)
    # This avoids 500 errors from sending too much data
    max_chars = 5000
    truncated_text = proposal_text[:max_chars]
    
    if len(proposal_text) > max_chars:
        truncated_text += "\n\n[... content truncated for classification ...]"
    
    prompt = DOMAIN_CLASSIFIER_PROMPT.format(context=truncated_text)
    
    try:
        response = gemini_llm(prompt)
    except Exception as e:
        print(f"[WARNING] Domain classification failed: {e}")
        print("[INFO] Defaulting to 'Social Sciences / Policy'")
        return "Social Sciences / Policy"

    domain = strip_response(response)

    # Optional: safety fallback if model outputs garbage
    allowed_domains = [
        "AI / Computer Science",
        "Biotechnology / Life Sciences",
        "Healthcare / Medicine",
        "Education / Learning Sciences",
        "Environment / Climate / Sustainability",
        "Social Sciences / Policy",
        "Engineering / Technology",
        "Physics / Materials Science",
        "Chemistry / Chemical Engineering",
        "Agriculture / Food Science",
        "Energy / Renewable Resources",
        "Economics / Business",
        "Arts / Humanities",
        "Psychology / Behavioral Sciences",
        "Urban Planning / Architecture",
        "Data Science / Statistics",
        "Cybersecurity / Information Security",
        "Public Health / Epidemiology",
        "Space Science / Astronomy",
        "Marine Biology / Oceanography",
        "Neuroscience / Cognitive Science"
    ]

    if domain not in allowed_domains:
        domain = "Social Sciences / Policy"  # default safest domain

    return domain


def get_all_domains() -> list:
    """
    Return list of all available domains for UI dropdown.
    """
    return [
        "AI / Computer Science",
        "Biotechnology / Life Sciences",
        "Healthcare / Medicine",
        "Education / Learning Sciences",
        "Environment / Climate / Sustainability",
        "Social Sciences / Policy",
        "Engineering / Technology",
        "Physics / Materials Science",
        "Chemistry / Chemical Engineering",
        "Agriculture / Food Science",
        "Energy / Renewable Resources",
        "Economics / Business",
        "Arts / Humanities",
        "Psychology / Behavioral Sciences",
        "Urban Planning / Architecture",
        "Data Science / Statistics",
        "Cybersecurity / Information Security",
        "Public Health / Epidemiology",
        "Space Science / Astronomy",
        "Marine Biology / Oceanography",
        "Neuroscience / Cognitive Science"
    ]
