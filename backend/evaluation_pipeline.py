"""
Grant Evaluation Pipeline
Orchestrates the full evaluation process from document loading to final decision.
"""

import sys
import os

# Allow `src/...` imports when executed as script
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.agents.input_agent import input_agent
from src.agents.vectorstore_agent import vectorstore_agent
from src.agents.summarizer import run_summarizer_extended
from src.agents.domain_selection import classify_domain
from src.agents.scoring import run_grant_scoring
from src.config.domain_weights import compute_weighted_score
from src.agents.critique import run_grant_critique
from src.agents.budget_agent import run_budget_agent
from src.agents.decision import run_final_decision_agent
from src.llm_wrapper import set_deterministic_mode


def run_full_evaluation(file_path: str, max_budget: float = 50000, override_domain: str = None, check_plagiarism: bool = False):
    """
    Run complete adaptive grant evaluation pipeline.

    Args:
        file_path: Path to the grant proposal file (PDF/DOCX)
        max_budget: Maximum allowed requested budget
        override_domain: Optional domain override by user (bypasses auto-detection)
        check_plagiarism: Whether to run plagiarism detection

    Returns:
        dict: structured evaluation result for frontend
    """

    # Make evaluation deterministic to remove LLM randomness
    try:
        set_deterministic_mode(True)
    except:
        pass

    # Step 1 — Extract text pages
    print(f"[INFO] Loading document: {file_path}")
    pages = input_agent(file_path)
    if not pages:
        raise ValueError("Document extraction failed.")
    print(f"[INFO] Loaded {len(pages)} pages")

    # Step 2 — Build vectorstore fresh each run (avoid cross-proposal contamination)
    print("[INFO] Creating in-memory vectorstore...")
    # Get config path relative to the project root
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
    vs = vectorstore_agent(pages, config_path=config_path, persist_dir=None)

    # Step 3 — Domain classification (or use override) - DO THIS FIRST
    if override_domain:
        print(f"[INFO] Using user-specified domain → {override_domain}")
        domain = override_domain
    else:
        print("[INFO] Detecting academic / research domain...")
        domain = classify_domain(" ".join([p.page_content for p in pages]))
        print(f"[INFO] Domain Detected → {domain}")

    # Step 4 — Structured summarization (section-wise) with domain context
    print("[INFO] Generating structured summary...")
    summary = run_summarizer_extended(vs["ask"], domain=domain)

    # Step 5 — Scoring (raw, before weighting)
    print("[INFO] Running scoring agent...")
    scores = run_grant_scoring(summary, domain)

    # Step 6 — Apply adaptive weighting model
    print("[INFO] Computing weighted score...")
    final_weighted_score = compute_weighted_score(scores["scores"], domain)
    print(f"[INFO] Weighted Score = {final_weighted_score}")

    # Step 7 — Critique (uses scoring, does NOT modify score)
    print("[INFO] Generating critique...")
    critique = run_grant_critique(
        scorer_json=scores,
        summaries_json=summary,
        domain=domain
    )

    # Step 8 — Budget analysis
    print("[INFO] Evaluating budget...")
    
    # Try to extract budget more aggressively
    budget_text = summary.get("Budget", {}).get("text", "")
    budget_notes = summary.get("Budget", {}).get("notes", [])
    
    # If budget text is empty or too short, try alternative extraction
    if len(budget_text) < 20:
        print("[INFO] Budget section short, attempting alternative extraction...")
        # Look for budget in other sections that might contain it
        for section_name, section_data in summary.items():
            if isinstance(section_data, dict):
                section_text = section_data.get("text", "")
                # Check if this section mentions budget/cost/funding
                if any(keyword in section_text.lower() for keyword in ["budget", "cost", "funding", "financial", "$", "expense"]):
                    if len(section_text) > len(budget_text):
                        budget_text = section_text
                        budget_notes = section_data.get("notes", [])
                        print(f"[INFO] Found budget info in {section_name} section")
                        break
    
    budget_input = {
        "text": budget_text,
        "notes": budget_notes,
        "references": summary.get("Budget", {}).get("references", []),
        "score": scores.get("scores", {}).get("Budget", {}).get("score", 5),
        "summary": scores.get("scores", {}).get("Budget", {}).get("summary", "Budget not analyzed"),
        "strengths": scores.get("scores", {}).get("Budget", {}).get("strengths", []),
        "weaknesses": scores.get("scores", {}).get("Budget", {}).get("weaknesses", [])
    }
    
    # Check if budget info exists
    has_budget_info = len(budget_text) > 50 and any(
        keyword in budget_text.lower() 
        for keyword in ["budget", "cost", "$", "expense", "funding", "financial"]
    )
    
    if not has_budget_info:
        print("[WARNING] No substantial budget information found in proposal")
        budget_evaluation = {
            "totalBudget": 0.0,
            "breakdown": [],
            "flags": [{
                "type": "warning",
                "message": "No detailed budget information found in the proposal document."
            }],
            "summary": "The proposal does not contain a detailed budget section. Budget information may be missing or in a separate document."
        }
    else:
        budget_evaluation = run_budget_agent(
            budget_input,
            max_budget=max_budget,
            domain=domain
        )
        
        # Validate and clean budget_evaluation
        if not isinstance(budget_evaluation, dict):
            budget_evaluation = {"totalBudget": 0.0, "breakdown": [], "flags": [], "summary": "Budget analysis failed"}
        
        # Ensure required fields exist with defaults
        budget_evaluation.setdefault("totalBudget", 0.0)
        budget_evaluation.setdefault("breakdown", [])
        budget_evaluation.setdefault("flags", [])
        budget_evaluation.setdefault("summary", "No budget summary available")
        
        # Clean breakdown items - ensure no None values and convert strings to numbers
        if isinstance(budget_evaluation.get("breakdown"), list):
            cleaned_breakdown = []
            for item in budget_evaluation["breakdown"]:
                if isinstance(item, dict):
                    # Convert amount to float, handle strings like "Unclear", None, etc.
                    amount = item.get("amount", 0.0)
                    if isinstance(amount, str):
                        try:
                            amount = float(amount.replace(",", "").replace("$", ""))
                        except (ValueError, AttributeError):
                            amount = 0.0
                    elif amount is None:
                        amount = 0.0
                    
                    # Convert percentage to float
                    percentage = item.get("percentage", 0.0)
                    if isinstance(percentage, str):
                        try:
                            percentage = float(percentage.replace("%", "").replace(",", ""))
                        except (ValueError, AttributeError):
                            percentage = 0.0
                    elif percentage is None:
                        percentage = 0.0
                    
                    # Only include if category exists
                    category = item.get("category", "Unspecified")
                    if category and category != "Unclear":
                        cleaned_breakdown.append({
                            "category": category,
                            "amount": float(amount),
                            "percentage": float(percentage)
                        })
            
            budget_evaluation["breakdown"] = cleaned_breakdown
        
        # Ensure totalBudget is a float
        if isinstance(budget_evaluation.get("totalBudget"), str):
            try:
                budget_evaluation["totalBudget"] = float(
                    budget_evaluation["totalBudget"].replace(",", "").replace("$", "")
                )
            except (ValueError, AttributeError):
                budget_evaluation["totalBudget"] = 0.0
        elif budget_evaluation.get("totalBudget") is None:
            budget_evaluation["totalBudget"] = 0.0

    # Step 9 — Final decision (uses weighted score, does NOT recalc score)
    print("[INFO] Finalizing decision...")
    final_decision = run_final_decision_agent(
        summary_json=summary,
        scores_json=scores,
        critique_json=critique,
        budget_json=budget_evaluation,
        final_weighted_score=final_weighted_score,
        domain=domain
    )

    # Step 10 — Plagiarism check (optional)
    plagiarism_result = None
    if check_plagiarism:
        print("[INFO] Running plagiarism detection...")
        try:
            from src.plagiarism.plagiarism_detector import detect_plagiarism
            full_text = " ".join([p.page_content for p in pages])
            plagiarism_result = detect_plagiarism(full_text)
            print(f"[INFO] Plagiarism Risk Level → {plagiarism_result.get('risk_level', 'UNKNOWN')}")
        except Exception as e:
            print(f"[WARNING] Plagiarism check failed: {str(e)}")
            plagiarism_result = {
                "error": str(e),
                "risk_level": "UNKNOWN"
            }

    # Done — format into frontend-ready shape
    return format_evaluation_response(
        summary, scores, critique, budget_evaluation, final_decision, 
        final_weighted_score, domain, plagiarism_result
    )


def format_evaluation_response(summary, scores, critique, budget_eval, decision, final_weighted_score, domain, plagiarism_result=None):
    """
    Convert internal evaluation results to a frontend-compatible output format.
    """
    
    def format_section_name(name):
        """Add spaces to camelCase section names"""
        import re
        # Insert space before capital letters
        spaced = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
        return spaced

    section_scores = []
    score_details = []

    for section_name, section_data in scores.get("scores", {}).items():
        formatted_name = format_section_name(section_name)
        section_scores.append({
            "section": formatted_name,
            "score": section_data.get("score", 0)
        })
        score_details.append({
            "category": formatted_name,
            "score": section_data.get("score", 0),
            "maxScore": 10,
            "strengths": section_data.get("strengths", []),
            "weaknesses": section_data.get("weaknesses", [])
        })

    # Transform critique structure to match FullCritique model
    formatted_critique = {
        "summary": critique.get("overall_feedback", "No overall feedback provided."),
        "issues": [],
        "recommendations": []
    }
    
    # Build critique_domains list for frontend
    # Use a smarter scoring based on severity and count of issues vs recommendations
    critique_domain_scores = []
    
    # Mapping critique domains to their display names
    critique_domain_map = {
        "scientific_critique": "Scientific",
        "practical_critique": "Practical",
        "language_critique": "Language",
        "context_critique": "Context",
        "persuasiveness_critique": "Persuasiveness",
        "ethical_critique": "Ethical",
        "innovation_critique": "Innovation"
    }
    
    print(f"[DEBUG] Critique keys: {list(critique.keys())}")
    
    for domain_key, display_name in critique_domain_map.items():
        domain_critique = critique.get(domain_key, {})
        
        if not domain_critique or not isinstance(domain_critique, dict):
            print(f"[WARNING] No data for {domain_key}")
            # Default score when no data
            critique_domain_scores.append({
                "domain": display_name,
                "score": 6.0  # Slightly above average default
            })
            continue
        
        # Count issues and recommendations
        issues = domain_critique.get("issues", [])
        recs = domain_critique.get("recommendations", [])
        issue_count = len(issues) if isinstance(issues, list) else 0
        rec_count = len(recs) if isinstance(recs, list) else 0
        
        # More reasonable scoring aligned with overall score:
        # - Start from final_weighted_score as baseline (proposals are already scored)
        # - Each issue reduces score by 0.3-0.5 points (not 1.2!)
        # - Each recommendation reduces score by 0.1 (minor adjustment)
        # - Add domain-specific variation (-0.5 to +0.5)
        base_score = final_weighted_score  # Use actual overall score as baseline
        issue_penalty = issue_count * 0.4  # Much gentler penalty
        rec_penalty = rec_count * 0.1
        
        # Add slight variation based on domain importance
        domain_index = list(critique_domain_map.keys()).index(domain_key)
        variation = (domain_index * 0.15) - 0.5  # Creates -0.5 to +0.5 range
        
        domain_score = max(0, min(10, base_score - issue_penalty - rec_penalty + variation))
        
        print(f"[DEBUG] {display_name}: {issue_count} issues, {rec_count} recs, base: {base_score:.1f}, score: {domain_score:.1f}")
        
        critique_domain_scores.append({
            "domain": display_name,
            "score": round(domain_score, 1)
        })
        
        # Add issues and recommendations to formatted critique with domain tags
        for issue in issues:
            if isinstance(issue, str):
                formatted_critique["issues"].append({
                    "severity": "high",  # Default severity
                    "category": display_name,
                    "domain": display_name,  # Explicit domain tag for filtering
                    "description": issue
                })
                print(f"[DEBUG] Added issue for domain '{display_name}': {issue[:50]}...")
        for rec in recs:
            if isinstance(rec, str):
                formatted_critique["recommendations"].append({
                    "priority": "medium",  # Default priority
                    "domain": display_name,  # Explicit domain tag for filtering
                    "recommendation": rec
                })
                print(f"[DEBUG] Added recommendation for domain '{display_name}': {rec[:50]}...")
    
    print(f"[DEBUG] Total critique domains: {len(critique_domain_scores)}")
    print(f"[DEBUG] Total issues added: {len(formatted_critique['issues'])}")
    print(f"[DEBUG] Total recommendations added: {len(formatted_critique['recommendations'])}")

    response = {
        "decision": decision.get("decision", "CONDITIONALLY ACCEPT"),
        "overall_score": final_weighted_score,
        "domain": domain,
        "scores": score_details,
        "critique_domains": critique_domain_scores,
        "full_critique": formatted_critique,
        "budget_analysis": budget_eval,
        "section_scores": section_scores,
        "summary": summary
    }

    if plagiarism_result:
        response["plagiarism_check"] = plagiarism_result

    return response
