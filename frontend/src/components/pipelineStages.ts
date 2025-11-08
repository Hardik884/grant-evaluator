import type { LucideIcon } from 'lucide-react';
import {
  Sparkles,
  FileSearch,
  BarChart3,
  CheckCircle2,
  Brain,
  DollarSign,
  AlertTriangle,
  ShieldCheck,
} from 'lucide-react';

export type StageStatus = 'pending' | 'active' | 'complete';

export interface PipelineStage {
  key: string;
  label: string;
  icon: LucideIcon;
}

export const pipelineStages: PipelineStage[] = [
  { key: 'document_ingest', icon: FileSearch, label: 'Parsing document and detecting sections' },
  { key: 'domain_detection', icon: Brain, label: 'Identifying research domain context' },
  { key: 'summarisation', icon: Sparkles, label: 'Summarising narrative and metadata' },
  { key: 'scoring', icon: BarChart3, label: 'Scoring against rubric benchmarks' },
  { key: 'critique', icon: AlertTriangle, label: 'Reviewing critique and risk signals' },
  { key: 'budget', icon: DollarSign, label: 'Auditing budget structure and anomalies' },
  { key: 'compliance', icon: ShieldCheck, label: 'Validating compliance and plagiarism scan' },
  { key: 'finalisation', icon: CheckCircle2, label: 'Compiling final recommendation package' },
];
