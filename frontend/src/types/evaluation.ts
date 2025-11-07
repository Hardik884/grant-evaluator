export interface ScoreDetail {
  category: string;
  score: number;
  maxScore: number;
  strengths: string[];
  weaknesses: string[];
}

export interface CritiqueDomain {
  domain: string;
  name?: string; // Alias for domain
  score: number;
}

export interface SectionScore {
  section: string;
  score: number;
}

export interface CritiqueIssue {
  severity: 'high' | 'medium' | 'low';
  category: string;
  domain?: string; // Added for domain filtering
  description: string;
}

export interface CritiqueRecommendation {
  priority: 'high' | 'medium' | 'low';
  domain?: string; // Added for domain filtering
  recommendation: string;
}

export interface FullCritique {
  summary: string;
  issues: CritiqueIssue[];
  recommendations: CritiqueRecommendation[];
}

export interface BudgetItem {
  category: string;
  amount: number;
  percentage: number;
}

export interface BudgetFlag {
  type: 'warning' | 'error' | 'info';
  message: string;
}

export interface BudgetAnalysis {
  totalBudget: number;
  breakdown: BudgetItem[];
  flags: BudgetFlag[];
  summary: string;
}

export interface PlagiarismCheck {
  similarity_score?: number;
  matched_reference_text?: string;
  risk_level: 'HIGH' | 'MEDIUM' | 'LOW' | 'UNKNOWN';
  error?: string;
}

export interface SummarySection {
  text?: string;
  notes?: string[];
  references?: string[];
}

export interface Summary {
  [key: string]: SummarySection;
}

export interface Evaluation {
  id: string;
  file_name: string;
  file_size: number;
  decision: 'ACCEPT' | 'REJECT' | 'REVISE' | 'CONDITIONALLY ACCEPT';
  overall_score: number;
  domain: string;
  scores: ScoreDetail[];
  critique_domains: CritiqueDomain[];
  section_scores: SectionScore[];
  full_critique: FullCritique;
  budget_analysis: BudgetAnalysis;
  summary?: Summary;
  plagiarism_check?: PlagiarismCheck;
  created_at: string;
  updated_at: string;
}

export interface Settings {
  id: string;
  max_budget: number;
  chunk_size: number;
  created_at: string;
  updated_at: string;
}
