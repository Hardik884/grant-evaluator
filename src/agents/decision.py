from src.llm_wrapper import gemini_llm
import json
import re
from src.prompts import FINAL_DECISION_PROMPT

def strip_codeblock(text: str) -> str:
    return re.sub(r"^```(?:json)?\n|```$", "", text.strip(), flags=re.MULTILINE)

def run_final_decision_agent(scores_json, critique_json, budget_json, summary_json, final_weighted_score=None, domain="General"):
    """
    Combines outputs from scoring, critique, and budget agents with summary for final decision.
    
    Args:
        scores_json: Scoring results
        critique_json: Critique analysis
        budget_json: Budget evaluation
        summary_json: Structured summary
        final_weighted_score: Pre-calculated weighted score (optional)
        domain: The academic/research domain for context (default: "General")
    """
    full_input = {
        "scores": scores_json,
        "critique": critique_json,
        "budget": budget_json,
        "summary": summary_json,
        "final_weighted_score": final_weighted_score
    }

    prompt = FINAL_DECISION_PROMPT.format(
        data=json.dumps(full_input, indent=2),
        domain=domain,
        final_weighted_score=final_weighted_score if final_weighted_score is not None else "N/A"
    )

    response = gemini_llm(prompt)
    cleaned = strip_codeblock(response)

    try:
        decision_json = json.loads(cleaned)
    except json.JSONDecodeError:
        decision_json = {"raw_response": cleaned}

    return decision_json
