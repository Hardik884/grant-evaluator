# # src/agents/summarizer_agent.py
# from src.llm_wrapper import gemini_llm
# import json
# from src.prompts import SUMMARY_PROMPT

# def run_summarizer_extended(retriever_fn, query="Provide a structured summary of this grant proposal"):
#     """
#     Fetch chunks via retriever_fn and return structured summary JSON with:
#     - pages
#     - references
#     - notes
#     """

#     retrieved_docs = retriever_fn(query)

#     if not retrieved_docs:
#         return {}

#     # Combine text with page numbers for LLM
#     context_text = ""
#     for doc in retrieved_docs:
#         page_num = doc.get("page_number", "Unknown")
#         text = doc.get("text", "")
#         source = doc.get("source", "Unknown")
#         context_text += f"[Page {page_num} | Source: {source}]\n{text}\n\n"

#     # Prompt LLM
#     prompt = SUMMARY_PROMPT.format(context=context_text)
#     response = gemini_llm(prompt)

#     # Parse JSON safely
#     try:
#         summary_json = json.loads(response)
#     except json.JSONDecodeError:
#         # If LLM fails to give valid JSON, return raw response for inspection
#         summary_json = {"raw_response": response}

#     print("=== LLM Raw Response ===")
#     print(response)
#     return summary_json

# src/agents/summarizer_agent.py
from src.llm_wrapper import gemini_llm
import json
import re
from src.prompts import SUMMARY_PROMPT

# Define all key grant sections
GRANT_SECTIONS = [
    "CoverLetter",
    "Objectives",
    "Methodology",
    "EvaluationPlan",
    "ExpectedOutcomes",
    "Budget",
    "Feasibility",
    "Innovation",
    "Sustainability",
    "LettersOfSupport"
]

def strip_codeblock(text: str) -> str:
    """
    Remove Markdown-style code block wrappers (```json ... ```) if present.
    """
    return re.sub(r"^```(?:json)?\n|```$", "", text.strip(), flags=re.MULTILINE)

def run_summarizer_extended(retriever_fn, domain="General"):
    """
    Fetch chunks via retriever_fn for each grant section and return
    a complete structured summary JSON with:
    - text
    - pages
    - references
    - notes
    
    Args:
        retriever_fn: Function to retrieve relevant documents
        domain: The academic/research domain for context (default: "General")
    """
    # Strategy 1: Get a larger set of documents with one comprehensive query
    comprehensive_query = (
        "Retrieve all sections of this grant proposal including: "
        "cover letter, objectives, goals, aims, methodology, methods, approach, project description, "
        "evaluation plan, assessment, expected outcomes, results, impact, deliverables, "
        "budget, costs, financial plan, feasibility, sustainability, future funding, capacity, "
        "innovation, novel approach, unique features, and letters of support"
    )
    
    all_docs = retriever_fn(comprehensive_query)
    
    # Strategy 2: Add dedicated budget retrieval to ensure we capture dollar amounts
    budget_query = (
        "budget costs expenses funding financial dollars personnel equipment materials "
        "travel indirect costs line items budget breakdown total budget requested amount "
        "salaries stipends supplies overhead facilities administrative expenses"
    )
    budget_docs = retriever_fn(budget_query)
    
    # Strategy 3: Add numeric/table retrieval for budget tables
    numeric_query = "$ dollars table cost breakdown itemized line items total amount"
    numeric_docs = retriever_fn(numeric_query)
    
    # Strategy 4: Add outcomes and impact retrieval
    outcomes_query = (
        "expected outcomes results impact deliverables targets goals achievements "
        "reduce increase improve measure percent performance indicators success metrics"
    )
    outcomes_docs = retriever_fn(outcomes_query)
    
    # Strategy 5: Add innovation and feasibility retrieval
    innovation_query = (
        "innovation innovative novel unique new approach cutting-edge original "
        "feasibility sustainability future funding capacity resources organizational support"
    )
    innovation_docs = retriever_fn(innovation_query)
    
    # Merge documents, avoiding duplicates
    doc_ids = set()
    merged_docs = []
    
    for doc in all_docs + budget_docs + numeric_docs + outcomes_docs + innovation_docs:
        # Create unique ID based on content hash
        doc_id = hash(doc.get('text', '')[:100])
        if doc_id not in doc_ids:
            doc_ids.add(doc_id)
            merged_docs.append(doc)
    
    if not merged_docs:
        print("[WARNING] No documents retrieved from vectorstore")
        return {}
    
    print(f"[INFO] Retrieved {len(merged_docs)} total chunks across {5} retrieval strategies")
    
    # Sort by page number for coherent context
    try:
        docs_sorted = sorted(merged_docs, key=lambda d: int(d.get('page_number', 0)))
    except Exception:
        docs_sorted = merged_docs
    
    # Build context text with page markers
    context_text = ""
    for doc in docs_sorted:
        page_num = doc.get("page_number", "Unknown")
        text = doc.get("text", "")
        source = doc.get("source", "Unknown")
        context_text += f"[Page {page_num} | Source: {source}]\n{text}\n\n"
    
    print(f"[INFO] Total context length: {len(context_text)} characters")

    if not context_text:
        print("[WARNING] Context text is empty after building from docs")
        return {}

    # Prepare full prompt with domain context
    prompt = SUMMARY_PROMPT.format(context=context_text, domain=domain)

    # Call Gemini LLM
    response = gemini_llm(prompt)

    # Strip code block if present
    clean_response = strip_codeblock(response)

    # Parse JSON safely
    try:
        summary_json = json.loads(clean_response)
    except json.JSONDecodeError:
        summary_json = {"raw_response": response}

    return summary_json