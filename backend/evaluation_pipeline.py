"""
Grant Evaluation Pipeline
Orchestrates the full evaluation process from document loading to final decision.
"""

import sys
import os
from datetime import datetime
from typing import Any, Callable, Dict, Optional

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

StatusCallback = Optional[Callable[[Dict[str, Any]], None]]

PIPELINE_STAGES = [
    {"key": "document_ingest", "label": "Parsing document and detecting sections"},
    {"key": "domain_detection", "label": "Identifying research domain context"},
    {"key": "summarisation", "label": "Summarising narrative and metadata"},
    {"key": "scoring", "label": "Scoring against rubric benchmarks"},
    {"key": "critique", "label": "Reviewing critique and risk signals"},
    {"key": "budget", "label": "Auditing budget structure and anomalies"},
    {"key": "compliance", "label": "Validating compliance and plagiarism scan"},
    {"key": "finalisation", "label": "Compiling final recommendation package"},
]


def build_critique_domain_scores(critique: dict, scores: dict, domain: str) -> list:
    """
    Build critique domain scores from critique analysis.
    Uses a scoring model based on section scores, adjusted by issues and recommendations.
    
    Args:
        critique: The critique dictionary with domain-specific analysis
        scores: The section scores dictionary
        domain: The grant domain
    
    Returns:
        List of critique domain scores [{"domain": "Scientific", "score": 7.5}, ...]
    """
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
    
    # Calculate average section score as baseline
    section_scores_list = []
    for section_data in scores.get("scores", {}).values():
        if isinstance(section_data, dict):
            section_scores_list.append(section_data.get("score", 0))
    
    avg_section_score = sum(section_scores_list) / len(section_scores_list) if section_scores_list else 6.0
    
    for domain_key, display_name in critique_domain_map.items():
        domain_critique = critique.get(domain_key, {})
        
        if not domain_critique or not isinstance(domain_critique, dict):
            print(f"[WARNING] No critique data for {domain_key}")
            critique_domain_scores.append({
                "domain": display_name,
                "score": avg_section_score  # Use section avg as default
            })
            continue
        
        # Count issues and recommendations
        issues = domain_critique.get("issues", [])
        recs = domain_critique.get("recommendations", [])
        issue_count = len(issues) if isinstance(issues, list) else 0
        rec_count = len(recs) if isinstance(recs, list) else 0
        
        # Scoring model: Start from section average, penalize based on issues/recs
        # - Each issue reduces score by 0.5 points
        # - Each recommendation reduces score by 0.2 points
        # This reflects that critique identifies quality problems
        base_score = avg_section_score
        issue_penalty = issue_count * 0.5
        rec_penalty = rec_count * 0.2
        
        domain_score = max(0, min(10, base_score - issue_penalty - rec_penalty))
        
        critique_domain_scores.append({
            "domain": display_name,
            "score": round(domain_score, 1)
        })
    
    return critique_domain_scores


def run_full_evaluation(
    file_path: str,
    max_budget: float = 50000,
    override_domain: str = None,
    check_plagiarism: bool = False,
    status_callback: StatusCallback = None,
):
    """
    Run complete adaptive grant evaluation pipeline.

    Args:
        file_path: Path to the grant proposal file (PDF/DOCX)
        max_budget: Maximum allowed requested budget
        override_domain: Optional domain override by user (bypasses auto-detection)
    check_plagiarism: Whether to run plagiarism detection
    status_callback: Optional callable receiving structured stage updates

    Returns:
        dict: structured evaluation result for frontend
    """
    import uuid
    
    # Generate unique session ID for this evaluation to track isolation
    session_id = uuid.uuid4().hex[:12]

    total_stages = len(PIPELINE_STAGES)

    def emit_stage(stage_index: int, status: str, message: Optional[str] = None, progress_override: Optional[int] = None) -> None:
        if status_callback is None:
            return

        try:
            stage_meta = PIPELINE_STAGES[stage_index]
            stage_key = stage_meta["key"]
            stage_label = stage_meta["label"]
        except IndexError:
            stage_key = f"stage-{stage_index}"
            stage_label = "Pipeline"

        if progress_override is None:
            if status == "started":
                progress_value = max(0, min(99, int((stage_index / total_stages) * 100)))
            else:
                progress_value = max(1, min(100, int(((stage_index + 1) / total_stages) * 100)))
        else:
            progress_value = max(0, min(100, progress_override))

        payload = {
            "event": "status",
            "stage_index": stage_index,
            "stage_key": stage_key,
            "label": stage_label,
            "status": status,
            "progress": progress_value,
            "message": message or stage_label,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        try:
            status_callback(payload)
        except Exception:
            # Callback errors should not break the evaluation pipeline
            pass

    # Make evaluation deterministic to remove LLM randomness
    try:
        set_deterministic_mode(True)
    except:
        pass

    # Step 1 — Extract text pages
    emit_stage(0, "started", "Extracting proposal pages")
    print(f"[INFO] Loading document: {file_path}")
    pages = input_agent(file_path)
    if not pages:
        raise ValueError("Document extraction failed.")
    print(f"[INFO] Loaded {len(pages)} pages")
    
    emit_stage(0, "completed", f"Loaded {len(pages)} pages")

    # Step 2 — Build vectorstore fresh each run (avoid cross-proposal contamination)
    emit_stage(1, "started", "Building semantic index and preparing domain detection")
    print("[INFO] Creating in-memory vectorstore...")
    # Get config path relative to the project root
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
    
    # Use persist_dir=None to create in-memory vectorstore for complete isolation
    vs = vectorstore_agent(pages, config_path=config_path, persist_dir=None)

    # Step 3 — Domain classification (or use override) - DO THIS FIRST
    if override_domain:
        print(f"[INFO] Using user-specified domain → {override_domain}")
        domain = override_domain
        emit_stage(1, "completed", f"Domain locked to {domain}")
    else:
        print("[INFO] Detecting academic / research domain...")
        domain = classify_domain(" ".join([p.page_content for p in pages]))
        print(f"[INFO] Domain Detected → {domain}")
        emit_stage(1, "completed", f"Detected domain: {domain}")

    # Step 4 — Structured summarization (section-wise) with domain context
    emit_stage(2, "started", "Generating structured summary")
    print("[INFO] Generating structured summary...")
    summary = run_summarizer_extended(vs["ask"], domain=domain)
    emit_stage(2, "completed", "Summary generated")

    # Step 5 — Scoring (raw, before weighting)
    emit_stage(3, "started", "Scoring proposal against rubric")
    print("[INFO] Running scoring agent...")
    scores = run_grant_scoring(summary, domain)
    
    emit_stage(3, "completed", "Section scores computed")

    # Step 6 — Critique (uses scoring to generate quality assessment)
    emit_stage(4, "started", "Generating critique and risk analysis")
    print("[INFO] Generating critique...")
    critique = run_grant_critique(
        scorer_json=scores,
        summaries_json=summary,
        domain=domain
    )
    emit_stage(4, "completed", "Critique ready")
    
    # Step 6.5 — Build critique domain scores for comprehensive evaluation
    print("[INFO] Building critique domain scores...")
    critique_domain_scores = build_critique_domain_scores(critique, scores, domain)
    print(f"[INFO] Generated {len(critique_domain_scores)} critique domain scores")
    
    # Step 7 — Compute COMPREHENSIVE final score (section scores + critique scores)
    print("[INFO] Computing comprehensive final score...")
    
    # Handle case where LLM returns unexpected structure
    if not isinstance(scores, dict):
        raise ValueError(f"Scoring agent returned non-dict type: {type(scores)}")
    
    if "scores" not in scores:
        # Try to recover if the LLM returned the section scores directly
        if any(key in scores for key in ["Objectives", "Methodology", "Budget"]):
            print("[WARNING] Scoring agent returned flat structure, wrapping it...")
            scores = {"scores": scores, "overall_summary": ""}
        else:
            raise KeyError(f"Scoring agent response missing 'scores' key. Keys found: {list(scores.keys())}")
    
    # Check if scores dict is empty (happens when JSON parsing completely failed)
    if not scores["scores"] or len(scores["scores"]) == 0:
        raise ValueError("Scoring agent returned empty scores dictionary. Please retry evaluation.")
    
    # NEW: Pass critique domains to get comprehensive score
    final_weighted_score = compute_weighted_score(
        scores["scores"], 
        domain, 
        critique_domains=critique_domain_scores
    )
    print(f"[INFO] Final Comprehensive Score = {final_weighted_score:.2f}/10")

    # Step 8 — Budget analysis (MULTI-STRATEGY EXTRACTION)
    emit_stage(5, "started", "Evaluating budget structure")
    print("[INFO] Evaluating budget...")
    
    # Strategy 1: Get budget from summarizer output
    budget_text = summary.get("Budget", {}).get("text", "")
    budget_notes = summary.get("Budget", {}).get("notes", [])
    budget_refs = summary.get("Budget", {}).get("references", [])
    
    # Strategy 2: Direct search in raw pages for budget keywords
    print("[INFO] Strategy 2 - Searching raw pages for budget content...")
    budget_keywords = ["budget", "cost", "$", "expense", "funding", "financial", "price", "total", "personnel", "equipment", "travel", "indirect"]
    budget_pages_content = []
    
    for page in pages:
        page_text = page.page_content.lower()
        # Check if page contains multiple budget keywords or dollar signs
        keyword_count = sum(1 for kw in budget_keywords if kw in page_text)
        dollar_count = page_text.count("$")
        
        if keyword_count >= 2 or dollar_count >= 3:
            budget_pages_content.append(page.page_content)
    
    # If we found budget pages, append to budget_text
    if budget_pages_content:
        raw_budget_text = "\n\n".join(budget_pages_content)
        
        # If summary budget is weak, replace with raw extraction
        if len(budget_text) < 100:
            print("[INFO] Summary budget weak, using raw page extraction")
            budget_text = raw_budget_text
        else:
            # Combine both for comprehensive coverage
            print("[INFO] Combining summary and raw budget extractions")
            budget_text = budget_text + "\n\n--- Additional Budget Details from Pages ---\n\n" + raw_budget_text
    
    # Strategy 3: Use vectorstore to retrieve budget-specific chunks
    print("[INFO] Strategy 3 - Vectorstore retrieval for budget...")
    budget_query_results = vs["ask"]("Extract all budget information, costs, expenses, line items, dollar amounts, and financial details")
    budget_chunks = [doc.get("text", "") for doc in budget_query_results if any(kw in doc.get("text", "").lower() for kw in ["$", "budget", "cost", "expense"])]
    
    if budget_chunks:
        vector_budget_text = "\n\n".join(budget_chunks[:10])  # Top 10 most relevant
        
        # Add to budget text if substantial
        if len(vector_budget_text) > 100:
            budget_text = budget_text + "\n\n--- Budget from Vectorstore ---\n\n" + vector_budget_text
    
    # Strategy 4: Search in other summary sections for budget mentions
    if len(budget_text) < 200:
        print("[INFO] Strategy 4 - Searching other summary sections...")
        for section_name, section_data in summary.items():
            if isinstance(section_data, dict) and section_name != "Budget":
                section_text = section_data.get("text", "")
                # Check if this section mentions budget/cost/funding
                if any(keyword in section_text.lower() for keyword in budget_keywords):
                    budget_text += f"\n\n--- From {section_name} Section ---\n{section_text}"
                    print(f"[INFO] Found budget mentions in {section_name} section")
    
    budget_input = {
        "text": budget_text,
        "notes": budget_notes,
        "references": budget_refs,
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
    
    budget_stage_message = "Budget analysis complete"

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
        budget_stage_message = "Budget information unavailable; issued warning"
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

        budget_stage_message = f"Budget analysis complete (total ${budget_evaluation['totalBudget']:.2f})"

    emit_stage(5, "completed", budget_stage_message)

    # Step 9 — Compliance and optional plagiarism check
    emit_stage(6, "started", "Running compliance checks")
    plagiarism_result = None
    compliance_message = "Compliance checks completed"
    if check_plagiarism:
        print("[INFO] Running plagiarism detection...")
        try:
            from src.plagiarism.plagiarism_detector import detect_plagiarism
            full_text = " ".join([p.page_content for p in pages])
            plagiarism_result = detect_plagiarism(full_text)
            risk_level = plagiarism_result.get("risk_level", "UNKNOWN")
            print(f"[INFO] Plagiarism Risk Level → {risk_level}")
            compliance_message = f"Plagiarism check completed (risk {risk_level})"
        except Exception as e:
            print(f"[WARNING] Plagiarism check failed: {str(e)}")
            plagiarism_result = {
                "error": str(e),
                "risk_level": "UNKNOWN"
            }
            compliance_message = "Plagiarism check encountered an error"
    else:
        compliance_message = "Plagiarism scan skipped (disabled)"

    emit_stage(6, "completed", compliance_message)

    # Step 10 — Final decision (uses weighted score, does NOT recalc score)
    emit_stage(7, "started", "Compiling final recommendation package")
    print("[INFO] Finalizing decision...")
    final_decision = run_final_decision_agent(
        summary_json=summary,
        scores_json=scores,
        critique_json=critique,
        budget_json=budget_evaluation,
        final_weighted_score=final_weighted_score,
        domain=domain
    )

    response = format_evaluation_response(
        summary, scores, critique, budget_evaluation, final_decision,
        final_weighted_score, domain, critique_domain_scores, plagiarism_result
    )

    emit_stage(7, "completed", f"Recommendation ready ({response.get('decision', 'UNKNOWN')})")

    # Cleanup: Explicitly delete vectorstore to ensure no contamination
    try:
        if vs and "vectorstore" in vs:
            del vs["vectorstore"]
            del vs
    except Exception:
        pass

    return response


def format_evaluation_response(summary, scores, critique, budget_eval, decision, final_weighted_score, domain, critique_domain_scores, plagiarism_result=None):
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
        raw_strengths = section_data.get("strengths")
        strengths = raw_strengths if isinstance(raw_strengths, list) and raw_strengths else [
            "No standout strengths recorded."
        ]
        raw_weaknesses = section_data.get("weaknesses")
        weaknesses = raw_weaknesses if isinstance(raw_weaknesses, list) and raw_weaknesses else [
            "No critical weaknesses identified."
        ]
        section_scores.append({
            "section": formatted_name,
            "score": section_data.get("score", 0)
        })
        score_details.append({
            "category": formatted_name,
            "score": section_data.get("score", 0),
            "maxScore": 10,
            "strengths": strengths,
            "weaknesses": weaknesses
        })

    # Transform critique structure to match FullCritique model
    overall_feedback = critique.get("overall_feedback") if isinstance(critique, dict) else None
    if not isinstance(overall_feedback, str) or not overall_feedback.strip():
        overall_feedback = "No executive summary was generated."
    formatted_critique = {
        "summary": overall_feedback,
        "issues": [],
        "recommendations": []
    }
    
    # Use the critique_domain_scores passed from pipeline (already calculated)
    # Just extract issues and recommendations for formatted output
    
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
    
    for domain_key, display_name in critique_domain_map.items():
        domain_critique = critique.get(domain_key, {})
        
        if not domain_critique or not isinstance(domain_critique, dict):
            continue
        
        # Extract issues and recommendations for formatted critique
        issues = domain_critique.get("issues", [])
        recs = domain_critique.get("recommendations", [])
        
        # Add issues and recommendations to formatted critique with domain tags
        for issue in issues:
            if isinstance(issue, str):
                formatted_critique["issues"].append({
                    "severity": "high",  # Default severity
                    "category": display_name,
                    "domain": display_name,  # Explicit domain tag for filtering
                    "description": issue
                })
        for rec in recs:
            if isinstance(rec, str):
                formatted_critique["recommendations"].append({
                    "priority": "medium",  # Default priority
                    "domain": display_name,  # Explicit domain tag for filtering
                    "recommendation": rec
                })
    
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
