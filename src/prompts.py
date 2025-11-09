from langchain.prompts import PromptTemplate

# src/prompts.py

# src/prompts.py

# SUMMARY_PROMPT = """
# You are an expert grant reviewer. Summarize the following grant proposal strictly in JSON.
# Include the following sections: Objectives, Methodology, ExpectedOutcomes, Innovation, Feasibility.

# Each section should contain:
# - "text": concise summary of that section
# - "pages": list of page numbers where the information appears
# - "references": include page numbers and sources for cited information
# - "notes": brief commentary or confidence about the information

# The input text has page numbers and sources in this format: [Page X | Source: filename.pdf]

# Context:
# {context}

# Return **only valid JSON**, no extra text.
# """

SUMMARY_PROMPT = """
You are an expert grant reviewer specializing in the field of **{domain}**.

Your task is to summarize the following grant proposal into a structured JSON format.
The summary must capture the meaning, intent, and emphasis of the proposal accurately,
using terminology appropriate for the **{domain}** research area.

### CRITICAL RULES:
- **IMPORTANT: Some proposals may not have explicitly labeled sections. Extract the CONTENT even if section headers are different or missing.**
- **Look for concepts, not just section titles.** For example:
  - "Expected Outcomes" may be in "Objectives", "Goals", "Impact", or "Results" sections
  - "Innovation" may be described in "Project Description", "Approach", or "Methodology"
  - "Feasibility" may be in "Sustainability", "Future Funding", "Resources", or "Capacity"
- **FALLBACK EXTRACTION STRATEGY:** If you cannot find a dedicated section:
  1. **Search the entire proposal** for relevant content about that concept
  2. **Infer and extract** information scattered across multiple sections
  3. **Synthesize** a coherent summary from what you find
  4. **For Innovation specifically:** Look for novel approaches, unique methods, new technologies, creative solutions, or what makes this project different from existing work
  5. **For Feasibility:** Look for organizational capacity, past success, resources, partnerships, timeline realism, or continuation plans
  6. **For Expected Outcomes:** Look for quantifiable goals, measurable targets, success metrics, or anticipated results
- **Only if information is completely absent** (not just unlabeled), state:
  - "text": "Not provided"
  - "pages": []
  - "references": []
  - "notes": "Section missing or insufficiently described."
- You must base the summary **on the provided text**, but you may **infer and synthesize** when content is present but not explicitly labeled.

Include all of the following sections (even if the original document uses different names):
- **CoverLetter** (may be labeled: "Cover Letter", "Introduction", opening letter)
- **Objectives** (may be labeled: "Goals", "Purpose", "Aims", "Project Objectives")
- **Methodology** (may be labeled: "Methods", "Approach", "Project Description", "Activities", "Implementation Plan")
- **EvaluationPlan** (may be labeled: "Evaluation", "Assessment", "Monitoring", "Success Metrics")
- **ExpectedOutcomes** (may be labeled: "Outcomes", "Expected Results", "Impact", "Deliverables" - often embedded in Objectives section)
- **Budget** (may be labeled: "Budget", "Budget Narrative", "Costs", "Financial Plan")
- **Feasibility** (may be labeled: "Sustainability", "Future Funding", "Organizational Capacity", "Resources", "Long-term Plans")
- **Innovation** (may be labeled: "Innovative Approach", "Novel Aspects", "Unique Features" - often embedded in Methodology or Project Description)
- **Sustainability** (may be labeled: "Future Plans", "Long-term Sustainability", "Continuation Plan")
- **LettersOfSupport** (may be labeled: "Letters of Support", "Endorsements", "Partner Letters")

### For each section, include:
- "text": A clear, detailed summary capturing specific actions, strategies, stakeholders, or workflows.
- "pages": List of page numbers where relevant information appears.
- "references": Exact short quotes or key phrases from the proposal to support the summary. **Format each reference as: "[Page X] Quote text" or "[Page X, approx. line Y] Quote text" when possible.**
- "notes": Expert commentary on completeness, clarity, relevance, or missing details.

### SPECIAL EXTRACTION GUIDELINES:

**For ExpectedOutcomes:**
- **PRIMARY SEARCH:** Look for sections labeled "Expected Outcomes", "Outcomes", "Expected Results", "Impact", "Deliverables"
- **SECONDARY SEARCH:** If no dedicated outcomes section, extract from:
  - Objectives section (often contains outcome statements)
  - Goals section (quantifiable targets)
  - Evaluation Plan (success metrics and indicators)
  - Project Description (anticipated results)
- **LOOK FOR:**
  - Quantifiable targets (e.g., "reduce by 20%", "increase by X", "serve Y people")
  - Measurable outcomes and success indicators
  - Specific deliverables or products
  - Timeline-bound achievements
  - Before/after comparisons
- **INFERENCE ALLOWED:** Extract outcome-focused statements even if not explicitly labeled as "outcomes"
- May overlap with Objectives - that's OK, extract the outcome-focused content

**For Innovation:**
- **PRIMARY SEARCH:** Look for sections labeled "Innovation", "Innovative Approach", "Novel Aspects", "Unique Features"
- **SECONDARY SEARCH:** If no dedicated innovation section exists, search throughout the proposal for:
  - Novel or unique methodologies, approaches, or techniques
  - New technologies, tools, or equipment being introduced
  - Creative solutions to existing problems
  - What makes this project different from similar existing programs
  - Cutting-edge or state-of-the-art elements
  - First-time implementations or pilot programs
  - Improvements over traditional methods
- **EXTRACTION LOCATIONS:** Check Project Description, Methodology, Approach, Objectives, and Summary sections
- **INFERENCE ALLOWED:** If innovation is implied but not explicitly stated, infer it from:
  - Descriptions of new equipment or facilities (e.g., "first fitness center for police department")
  - Novel combinations of existing approaches
  - Unique target populations or contexts
  - New partnerships or collaborations
- **IF NO INNOVATION FOUND:** Only after thoroughly searching the entire proposal, if truly no innovative elements exist, state:
  - "text": "No explicit innovative elements identified. Project appears to use established methods and approaches."
  - Include this in "notes" rather than leaving it as "Not provided"

**For Feasibility:**
- **PRIMARY SEARCH:** Look for sections labeled "Feasibility", "Sustainability", "Future Funding", "Organizational Capacity", "Resources"
- **SECONDARY SEARCH:** If no dedicated feasibility section, extract from:
  - Sustainability or continuation plans
  - Future funding commitments
  - Organizational capacity descriptions
  - Resource availability statements
  - Past success or track record
  - Partnership agreements or letters of support
  - Timeline and project management plans
- **LOOK FOR:**
  - Evidence of capability to execute (staff qualifications, experience, facilities)
  - Long-term sustainability plans and maintenance commitments
  - Institutional or partner support
  - Resource availability (funding, equipment, personnel)
  - Realistic timelines and milestones
  - Risk mitigation strategies
- **INFERENCE ALLOWED:** Synthesize feasibility assessment from scattered evidence throughout the proposal
- Include any commitments from stakeholders or funding bodies for continuation

**For CoverLetter:**
- **PRIMARY SEARCH:** Look for sections labeled "Cover Letter", "Introduction", "Letter of Intent"
- **SECONDARY SEARCH:** If no dedicated cover letter, look for:
  - Opening statement or introduction
  - Initial paragraphs that introduce the organization and project
  - Executive summary or opening remarks
- **LOOK FOR:**
  - Introduction of the applicant organization
  - Brief project overview
  - Funding amount requested
  - Contact information
- **INFERENCE ALLOWED:** Extract introductory content even if not formally labeled as cover letter

**For Objectives:**
- **PRIMARY SEARCH:** Look for sections labeled "Objectives", "Goals", "Aims", "Project Objectives", "Purpose"
- **SECONDARY SEARCH:** If no dedicated objectives section, extract from:
  - Summary or introduction (often states main goals)
  - Problem statement (goals are often stated as solutions)
  - Project description (embedded objectives)
- **LOOK FOR:**
  - Specific, measurable goals
  - What the project aims to achieve
  - Target populations or beneficiaries
  - Timeframes for objectives
- **INFERENCE ALLOWED:** Extract goal statements from throughout the proposal

**For Methodology:**
- **PRIMARY SEARCH:** Look for sections labeled "Methodology", "Methods", "Approach", "Project Description", "Activities", "Implementation Plan"
- **SECONDARY SEARCH:** If no dedicated methodology section, extract from:
  - Project description or narrative
  - Work plan or timeline sections
  - Activity descriptions
- **LOOK FOR:**
  - Specific activities and interventions
  - Step-by-step implementation plan
  - Resources and tools to be used
  - Roles and responsibilities
  - Timeline and phases
- **INFERENCE ALLOWED:** Synthesize methodology from scattered activity descriptions

**For EvaluationPlan:**
- **PRIMARY SEARCH:** Look for sections labeled "Evaluation", "Evaluation Plan", "Assessment", "Monitoring", "Success Metrics"
- **SECONDARY SEARCH:** If no dedicated evaluation section, look for:
  - Measurement strategies mentioned in objectives
  - Success indicators or metrics
  - Data collection plans
  - Quality assurance descriptions
- **LOOK FOR:**
  - How success will be measured
  - Data collection methods
  - Evaluation timeline
  - Performance indicators
  - Who will conduct the evaluation
- **INFERENCE ALLOWED:** Extract evaluation-related content from objectives, methodology, or outcomes sections

**For Sustainability:**
- **PRIMARY SEARCH:** Look for sections labeled "Sustainability", "Future Plans", "Long-term Sustainability", "Continuation Plan"
- **SECONDARY SEARCH:** If no dedicated sustainability section, extract from:
  - Future funding section
  - Organizational capacity descriptions
  - Long-term goals or vision statements
- **LOOK FOR:**
  - Plans for continuing the project after funding ends
  - Future funding sources identified
  - Institutional commitments
  - Long-term impact plans
- **INFERENCE ALLOWED:** Synthesize sustainability from future funding and capacity statements

**For LettersOfSupport:**
- **PRIMARY SEARCH:** Look for sections labeled "Letters of Support", "Endorsements", "Partner Letters", "Appendices"
- **SECONDARY SEARCH:** If no dedicated letters section, look for:
  - Partnership descriptions
  - Stakeholder commitments
  - References to supporting organizations
- **LOOK FOR:**
  - Letters from partners or stakeholders
  - Formal endorsements
  - Memoranda of understanding (MOUs)
  - Commitment statements
- **INFERENCE ALLOWED:** Note mentions of partner support even if formal letters aren't included

### SPECIAL INSTRUCTIONS FOR BUDGET SECTION:
- **PRIMARY SEARCH:** Look for sections labeled "Budget", "Budget Narrative", "Costs", "Financial Plan"
- **SECONDARY SEARCH:** If no dedicated budget section, search for:
  - Dollar amounts and cost figures anywhere in the proposal
  - Resource requirements
  - Personnel costs in staffing sections
  - Equipment lists with prices
- **EXTRACT ALL DOLLAR AMOUNTS, LINE ITEMS, AND COST CATEGORIES** from the proposal
- Include budget tables, personnel costs, equipment, materials, travel expenses, indirect costs
- Copy exact dollar figures (e.g., "$50,000 for personnel", "$10,000 for equipment")
- List ALL budget categories mentioned with their specific amounts
- In the "text" field, provide a detailed itemized breakdown with actual numbers
- In "references", include direct quotes with dollar amounts **formatted as: "[Page X] Quote with dollar amount"**
- **INFERENCE ALLOWED:** Compile budget information from scattered cost mentions throughout the proposal

If the proposal does not contain enough information for a section, explicitly state:
- text: "Not provided"
- pages: []
- references: []
- notes: "Section missing or insufficiently described."

The input text includes page markers in the format:
[Page X | Source: filename.pdf]

**IMPORTANT:** When creating references, extract the page number from these markers and format your references as:
- "[Page X] Direct quote from the proposal"
- This helps reviewers quickly locate and verify the quoted content

### Input Proposal Text:
{context}

### Output:
Return **only valid JSON**, with no explanation or surrounding text.
"""


# Scoring prompt template
SCORING_PROMPT = """
You are an expert grant evaluator specializing in the field of **{domain}**.
You are given a structured summary of a grant proposal in JSON format.

Your task is to evaluate the quality of each section objectively and produce **strictly structured JSON output** suitable for automated scoring.

### CRITICAL RULES:
- **Do NOT invent or assume any information that is not clearly present in the summary.**
- **Do NOT adjust or compute the final overall weighted score.** The scoring engine handles weighting.
- Return **only valid JSON** exactly in the requested structure.
- **IMPORTANT: You MUST complete the entire JSON response. Do not truncate strings or leave objects incomplete.**
- Keep strengths and weaknesses concise (under 100 characters each) to ensure completion.

### SPECIAL NOTE ON SECTION EVALUATION:
- **Some proposals may have content in non-standard sections.** For example:
  - Expected Outcomes may be embedded in Objectives
  - Innovation may be described in Methodology or Project Description
  - Feasibility may be discussed in Sustainability or Future Funding
- **Score based on the CONTENT provided, even if it came from a different section of the original document.**
- If a section shows "Not provided" or similar, give it a low score (0-2) with appropriate feedback.
- If a section contains substantive content (regardless of origin), score it based on that content's quality.

### SCORING INSTRUCTIONS
1. **Rate each section from 0 to 10**
   - 0 = Missing or irrelevant
   - 5 = Acceptable but incomplete or vague
   - 10 = Exceptional, clear, and well-supported

2. **Be strict but fair.**
   - Penalize missing data, weak justification, vague language, or lack of evidence.
   - Reward specificity, measurable goals, methodological rigor, innovation appropriate to the **{domain}** field, and clear alignment between goals and execution plan.

3. **Provide concise reasoning in each section’s fields:**
   - `summary`: One clear sentence describing the section's effectiveness.
   - `strengths`: 1–3 bullet points.
   - `weaknesses`: 1–3 bullet points.
   - `score`: Integer 0–10 (no decimals).

4. **Do NOT compute an overall weighted score here.**
   - The final weighted score is computed separately by the evaluation engine.
   - You must still provide `overall_summary` (1 short paragraph) describing general quality and coherence across sections.

### INPUT
Input JSON (the structured proposal summary):
{grant_json}

### OUTPUT FORMAT (STRICTLY JSON)
{{
  "scores": {{
    "CoverLetter": {{
      "score": int,
      "summary": str,
      "strengths": [str, ...],
      "weaknesses": [str, ...]
    }},
    "Objectives": {{
      "score": int,
      "summary": str,
      "strengths": [str, ...],
      "weaknesses": [str, ...]
    }},
    "Methodology": {{
      "score": int,
      "summary": str,
      "strengths": [str, ...],
      "weaknesses": [str, ...]
    }},
    "EvaluationPlan": {{
      "score": int,
      "summary": str,
      "strengths": [str, ...],
      "weaknesses": [str, ...]
    }},
    "ExpectedOutcomes": {{
      "score": int,
      "summary": str,
      "strengths": [str, ...],
      "weaknesses": [str, ...]
    }},
    "Budget": {{
      "score": int,
      "summary": str,
      "strengths": [str, ...],
      "weaknesses": [str, ...]
    }},
    "Feasibility": {{
      "score": int,
      "summary": str,
      "strengths": [str, ...],
      "weaknesses": [str, ...]
    }},
    "Innovation": {{
      "score": int,
      "summary": str,
      "strengths": [str, ...],
      "weaknesses": [str, ...]
    }},
    "Sustainability": {{
      "score": int,
      "summary": str,
      "strengths": [str, ...],
      "weaknesses": [str, ...]
    }},
    "LettersOfSupport": {{
      "score": int,
      "summary": str,
      "strengths": [str, ...],
      "weaknesses": [str, ...]
    }}
  }},
  "overall_summary": str
}}

Scoring Guidance:
- 10 = Exceptional and field-appropriate excellence (no major weaknesses)
- 8–9 = Strong but with minor refinements needed
- 6–7 = Adequate but lacks clarity or justification
- 4–5 = Weak with substantial missing details
- 0–3 = Critically flawed, incomplete, or non-compliant

"""
MASTER_CRITIQUE_PROMPT = """
You are a master-level grant reviewer specializing in the field of **{domain}**.

You are provided with:
1. The structured summaries of each proposal section (optional, may be None).
2. The section-level evaluation results from the Scoring Agent (scores, strengths, and weaknesses).

Your role is to produce a clear, objective critique that contextualizes the evaluation **according to the standards and expectations of the {domain} field**.

### Review Domains (analyze each):
1. **Scientific Rigor** – methodological soundness, research grounding, field-specific validity.
2. **Practical Feasibility** – resource realism, operational clarity, timeline viability.
3. **Language & Clarity** – coherence, academic tone, precision, logical flow.
4. **Context & Alignment** – alignment between goals, execution strategy, and expected outcomes.
5. **Persuasiveness** – justification strength, credibility, compelling rationale.
6. **Ethics & Inclusivity** – transparency, fairness, participant considerations, responsible conduct.
7. **Innovation & Impact** – originality, transformative potential, significance in the **{domain}** context.

### Important Instructions:
- Do **NOT** re-score or modify any scores.
- Do **NOT** contradict the scoring agent; instead, **expand on the reasoning**.
- Be constructive: every identified issue should have a corresponding recommendation.
- Language should be professional, direct, and free of filler or speculation.

For each review domain, produce:
- 2–5 **issues** — specific shortcomings or concerns
- 2–5 **recommendations** — realistic, actionable improvements
- Be factual, professional, concise.

End with:
- `priority_focus`: The **three most important** areas to improve first.
- `overall_feedback`: One concise paragraph synthesizing overall quality and improvement direction.

### INPUT (JSON):
{input_json}

### OUTPUT (STRICT JSON ONLY):
{{
  "scientific_critique": {{
    "issues": [str, ...],
    "recommendations": [str, ...]
  }},
  "practical_critique": {{
    "issues": [str, ...],
    "recommendations": [str, ...]
  }},
  "language_critique": {{
    "issues": [str, ...],
    "recommendations": [str, ...]
  }},
  "context_critique": {{
    "issues": [str, ...],
    "recommendations": [str, ...]
  }},
  "persuasiveness_critique": {{
    "issues": [str, ...],
    "recommendations": [str, ...]
  }},
  "ethical_critique": {{
    "issues": [str, ...],
    "recommendations": [str, ...]
  }},
  "innovation_critique": {{
    "issues": [str, ...],
    "recommendations": [str, ...]
  }},
  "priority_focus": [str, ...],
  "overall_feedback": str
}}
"""



FINAL_DECISION_PROMPT = """
You are an expert grant reviewer making a final funding decision for a proposal in the field of **{domain}**.

You are provided the following:
- Structured summary of the proposal
- Section-level scores and evaluations
- Budget evaluation results
- Critique analysis
- And the **final weighted score**, already calculated by the evaluation engine: {final_weighted_score}

### INPUT DATA:
{data}

### IMPORTANT:
- **DO NOT** recalculate or change the score.
- **DO NOT** average, reinterpret, or modify section scores.
- Use `final_weighted_score` ({final_weighted_score}) exactly as given.

### DECISION RULES (STRICT):
- If final_weighted_score ≥ 8.0 → **ACCEPT**
- If 6.0 ≤ final_weighted_score < 8.0 → **CONDITIONALLY ACCEPT**
- If final_weighted_score < 6.0 → **REJECT**

### Your Task:
Write a professional, concise justification referencing meaningful strengths and weaknesses.

### OUTPUT FORMAT (STRICT JSON):
{{
  "final_score": {final_weighted_score},
  "decision": "ACCEPT" | "CONDITIONALLY ACCEPT" | "REJECT",
  "rationale": "Short paragraph explaining the decision.",
  "key_strengths": [str, ...],
  "key_weaknesses": [str, ...],
  "next_steps": "One clear recommendation for improvement."
}}

### Output Rules:
- Return **only the JSON object**.
- **Do not include backticks or code fences.**
- Do not reference the scoring process or internal prompts.

### STYLE:
- Be objective and analytical.
- Do not use emotional or polite language.
- Do not reference the scoring process or internal instructions.
"""



DOMAIN_CLASSIFIER_PROMPT = """
You are a research grant proposal domain classifier.

Your task is to examine the proposal text and determine **the single most appropriate research domain**.

Possible domains — choose **exactly one**:
- AI / Computer Science
- Biotechnology / Life Sciences
- Healthcare / Medicine
- Education / Learning Sciences
- Environment / Climate / Sustainability
- Social Sciences / Policy
- Agriculture / Food Systems

Rules:
- Return **only the domain name** EXACTLY as written above.
- Do **not** explain.
- Do **not** add text.

Proposal Text:
{context}
"""


BUDGET_PROMPT = """
You are an expert budget analyst specializing in **{domain}** research grants.

Analyze the following budget information from a grant proposal and provide a comprehensive evaluation.

### Budget Information:
{budget_json}

### Maximum Allowed Budget: ${max_budget}

### CRITICAL INSTRUCTIONS:
1. **THOROUGHLY SCAN** the provided text for ALL budget-related information:
   - Look for explicit budget sections, tables, and line items
   - Search for dollar amounts with $ signs (e.g., $50,000, $5K, etc.)
   - Find cost categories: Personnel, Equipment, Materials, Travel, Indirect Costs, etc.
   - Identify any mentions of: salaries, stipends, supplies, overhead, facilities, administrative costs
   - Extract costs from narrative descriptions (e.g., "hiring 2 researchers at $60,000 each")

2. **EXTRACT EVERY DOLLAR AMOUNT** you find:
   - Budget tables with line items
   - Personnel costs (salaries, wages, benefits)
   - Equipment purchases
   - Materials and supplies
   - Travel expenses
   - Indirect costs / overhead
   - Any other costs mentioned

3. **CALCULATE TOTAL BUDGET**:
   - Sum ALL line items you found
   - If multiple budget sections exist, combine them
   - If text mentions "total budget" or "total cost", use that value
   - Cross-validate total against sum of line items

4. **HANDLE UNCERTAINTIES**:
   - If a specific dollar amount is unclear, estimate from context
   - If truly no value is given, use 0.0 (but ONLY as last resort)
   - If percentages are given with a total, calculate the dollar amounts
   - If ranges are given (e.g., "$10K-$15K"), use the midpoint

5. **ALL NUMERIC OUTPUTS**:
   - amount and percentage MUST be numbers (float or int), NEVER strings
   - Format: 5000.0 (not "5000" or "Unclear" or "TBD")
   - Calculate percentages from total budget

### Your Analysis Must Include:

1. **Budget Breakdown Extraction**:
   - Extract every budget line item with its dollar amount
   - Calculate percentage of total for each category
   - Common categories: Personnel, Equipment, Materials, Travel, Indirect Costs, Other
   - Create categories if the text describes costs without explicit category names

2. **Cost-Effectiveness Analysis**:
   - Assess if the budget is appropriate for the proposed work
   - Identify potential over-budgeting or under-budgeting
   - Compare against typical {domain} project costs

3. **Compliance Check**:
   - Verify if total budget is within the maximum allowed (${max_budget})
   - Check for required budget categories for {domain} research
   - Flag any budget items that seem inappropriate or missing

4. **Risk Assessment**:
   - Identify budget-related risks
   - Flag any red flags or concerns
   - Suggest budget optimizations if needed

### Output Format (STRICT JSON - all amounts MUST be numbers):
{{
  "totalBudget": <number_only>,
  "breakdown": [
    {{"category": "<name>", "amount": <number_only>, "percentage": <number_only>}}
  ],
  "flags": [
    {{"type": "warning|error|info", "message": "<description>"}}
  ],
  "summary": "<overall assessment including what was found and calculated>"
}}

### EXAMPLES OF GOOD EXTRACTION:
- Text: "Personnel: $100,000" → {{"category": "Personnel", "amount": 100000.0, "percentage": 66.7}}
- Text: "Travel budget is $15K" → {{"category": "Travel", "amount": 15000.0, "percentage": 10.0}}
- Text: "Two postdocs at $50,000 each" → {{"category": "Personnel", "amount": 100000.0, "percentage": 66.7}}

IMPORTANT: 
- Scan the ENTIRE text for budget information, not just the first section
- Extract from tables, narratives, and scattered mentions
- Calculate totals even if not explicitly stated
- Return **only valid JSON**, no additional text.
"""


PDF_FORMAT_PROMPT = """
You are a PDF formatter. Convert the grant evaluation results 
into Markdown with sections, tables, and clear highlights.

Constraints:
- Max 1000 words
- Highlight Accept in green, Reject in red
- Use tables for scores
Inputs:
{all_results}
"""
