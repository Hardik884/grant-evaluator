import json
import re
from src.llm_wrapper import gemini_llm  # your LLM wrapper
from src.prompts import BUDGET_PROMPT  # your prompt template


def strip_codeblock(text: str) -> str:
    """
    Remove Markdown-style code block wrappers (```json ... ```) if present.
    """
    return re.sub(r"^```(?:json)?\n|```$", "", text.strip(), flags=re.MULTILINE)


def run_budget_agent(budget_input, max_budget=None, domain="General"):
    """
    Evaluate the Budget section of a grant using LLM.

    Args:
        budget_input (dict): Combined Budget info from summarizer and scorer.
            Expected keys: text, notes, references, score, summary, strengths, weaknesses
        max_budget (float, optional): Maximum allowed budget to flag overages.
        domain (str, optional): The academic/research domain for context (default: "General")

    Returns:
        dict: LLM output with budget_score, budget_summary, flags, recommendations
    """
    # Convert input to JSON string
    budget_json_str = json.dumps(budget_input, indent=2)

    # Prepare prompt with domain context
    prompt = BUDGET_PROMPT.format(
        budget_json=budget_json_str, 
        max_budget=max_budget or "N/A",
        domain=domain
    )

    # Call LLM with higher token limit for detailed extraction
    response = gemini_llm(prompt, max_output_tokens=8192)

    cleaned_response = strip_codeblock(response)

    # Parse JSON safely
    try:
        budget_result = json.loads(cleaned_response)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Budget agent JSON parse error: {e}")
        budget_result = {"raw_response": cleaned_response, "totalBudget": 0.0, "breakdown": [], "flags": []}

    return budget_result
