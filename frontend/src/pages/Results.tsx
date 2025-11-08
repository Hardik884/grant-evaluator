import { useCallback, useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Download,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Gauge,
  CalendarClock,
  FileText,
  Sparkles,
  ShieldCheck,
  TrendingUp,
  TrendingDown,
  Check,
  X,
  AlertTriangle,
  DollarSign,
  Brain,
  ShieldAlert,
  FolderOpen,
  Layers,
} from 'lucide-react';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { Tabs } from '../components/Tabs';
import { RadarChartComponent } from '../components/charts/RadarChart';
import { BarChartComponent } from '../components/charts/BarChart';
import { evaluationService } from '../services/evaluationService';
import type { Evaluation } from '../types/evaluation';

const formatFileSize = (bytes: number) => {
  if (!bytes) return '—';
  const units = ['B', 'KB', 'MB', 'GB'];
  let size = bytes;
  let unitIndex = 0;

  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex += 1;
  }

  return `${size.toFixed(unitIndex === 0 ? 0 : 1)} ${units[unitIndex]}`;
};

const formatDateTime = (value: string) =>
  new Date(value).toLocaleString(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  });

const truncateText = (value: string | undefined, maxLength = 36) => {
  if (!value) return '—';
  return value.length > maxLength ? `${value.slice(0, maxLength - 3)}...` : value;
};

const budgetWidthClasses: Record<number, string> = {
  0: 'w-[0%]',
  5: 'w-[5%]',
  10: 'w-[10%]',
  15: 'w-[15%]',
  20: 'w-[20%]',
  25: 'w-[25%]',
  30: 'w-[30%]',
  35: 'w-[35%]',
  40: 'w-[40%]',
  45: 'w-[45%]',
  50: 'w-[50%]',
  55: 'w-[55%]',
  60: 'w-[60%]',
  65: 'w-[65%]',
  70: 'w-[70%]',
  75: 'w-[75%]',
  80: 'w-[80%]',
  85: 'w-[85%]',
  90: 'w-[90%]',
  95: 'w-[95%]',
  100: 'w-[100%]',
};

export function Results() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [evaluation, setEvaluation] = useState<Evaluation | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const loadEvaluation = useCallback(async (evaluationId: string) => {
    try {
      const data = await evaluationService.getEvaluationById(evaluationId);
      if (!data) {
        navigate('/');
        return;
      }
      setEvaluation(data);
    } catch (error) {
      console.error('Failed to load evaluation:', error);
      navigate('/');
    } finally {
      setIsLoading(false);
    }
  }, [navigate]);

  useEffect(() => {
    if (!id) {
      navigate('/');
      return;
    }
    loadEvaluation(id);
  }, [id, loadEvaluation, navigate]);

  const handleDownloadPDF = () => {
    if (!id) return;
    const downloadUrl = `http://localhost:8000/api/evaluations/${id}/download`;
    window.open(downloadUrl, '_blank');
  };

  if (isLoading) {
    return (
      <div className="flex min-h-[calc(100vh-6rem)] items-center justify-center">
        <div className="h-12 w-12 animate-spin rounded-full border-2 border-secondary border-t-transparent" />
      </div>
    );
  }

  if (!evaluation) {
    return null;
  }

  const safeEvaluation = {
    ...evaluation,
    critique_domains: evaluation.critique_domains || [],
    section_scores: evaluation.section_scores || [],
    scores: evaluation.scores || [],
    full_critique: evaluation.full_critique || { summary: '', issues: [], recommendations: [] },
    budget_analysis: evaluation.budget_analysis || { totalBudget: 0, breakdown: [], flags: [], summary: '' },
    summary: evaluation.summary || {},
    plagiarism_check: evaluation.plagiarism_check || null,
  };

  const DecisionBadge = () => {
    const decisionConfig: Record<
      Evaluation['decision'],
      { icon: typeof CheckCircle2; container: string; text: string }
    > = {
      ACCEPT: {
        icon: CheckCircle2,
        container: 'border-secondary/60 bg-secondary/10 text-secondary shadow-glow-secondary',
        text: 'text-secondary',
      },
      REJECT: {
        icon: XCircle,
        container: 'border-error/50 bg-error/10 text-error shadow-glow-primary',
        text: 'text-error',
      },
      REVISE: {
        icon: AlertCircle,
        container: 'border-warning/60 bg-warning/10 text-warning shadow-glow-primary',
        text: 'text-warning',
      },
      'CONDITIONALLY ACCEPT': {
        icon: CheckCircle2,
        container: 'border-primary/60 bg-primary/10 text-primary shadow-glow-primary',
        text: 'text-primary',
      },
    };

    const { icon: Icon, container, text } = decisionConfig[safeEvaluation.decision];

    return (
      <div className={`inline-flex items-center gap-3 rounded-2xl border px-5 py-3 text-sm font-semibold ${container}`}>
        <Icon className={`h-5 w-5 ${text}`} />
        <span className={`tracking-wide ${text}`}>{safeEvaluation.decision}</span>
      </div>
    );
  };

  const summaryMetrics = [
    {
      label: 'Overall Score',
      value: `${safeEvaluation.overall_score.toFixed(1)}/10`,
      icon: Gauge,
      accent: 'text-secondary',
    },
    {
      label: 'Research Domain',
      value: safeEvaluation.domain || 'Unassigned',
      icon: Brain,
      accent: 'text-slate-200',
    },
    {
      label: 'Document Size',
      value: formatFileSize(safeEvaluation.file_size),
      icon: FileText,
      accent: 'text-slate-200',
    },
    {
      label: 'Evaluated On',
      value: formatDateTime(safeEvaluation.created_at),
      icon: CalendarClock,
      accent: 'text-slate-200',
    },
  ];

  const quickFacts = [
    { label: 'File name', value: truncateText(safeEvaluation.file_name), hint: safeEvaluation.file_name },
    { label: 'Evaluation ID', value: safeEvaluation.id },
    { label: 'Updated', value: formatDateTime(safeEvaluation.updated_at) },
  ];

  const plagiarismRisk = safeEvaluation.plagiarism_check?.risk_level ?? 'UNKNOWN';
  const plagiarismSimilarity = safeEvaluation.plagiarism_check?.similarity_score;

  const tabs = [
    {
      id: 'visual',
      label: 'Visual Dashboard',
      content: (
        <div className="grid gap-6 lg:grid-cols-2">
          <Card>
            <h3 className="mb-4 text-xl font-semibold text-white">Critique Domains</h3>
            {safeEvaluation.critique_domains.length > 0 ? (
              <RadarChartComponent data={safeEvaluation.critique_domains} />
            ) : (
              <p className="text-sm text-slate-400">No critique domain data available.</p>
            )}
          </Card>
          <Card>
            <h3 className="mb-4 text-xl font-semibold text-white">Section Scores</h3>
            {safeEvaluation.section_scores.length > 0 ? (
              <BarChartComponent data={safeEvaluation.section_scores} />
            ) : (
              <p className="text-sm text-slate-400">No section score data available.</p>
            )}
          </Card>
        </div>
      ),
    },
    {
      id: 'detailed',
      label: 'Detailed Scoring',
      content: (
        <div className="grid gap-6 md:grid-cols-2">
          {safeEvaluation.scores.map((score, index) => (
            <Card key={index} hover>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-white">{score.category}</h3>
                  <div className="text-2xl font-bold text-secondary">
                    {score.score}/{score.maxScore}
                  </div>
                </div>
                <div className="space-y-4 text-sm">
                  <div>
                    <div className="mb-2 flex items-center gap-2 text-secondary">
                      <TrendingUp className="h-4 w-4" />
                      <span className="font-semibold uppercase tracking-wide">Strengths</span>
                    </div>
                    <ul className="space-y-1 text-slate-300">
                      {score.strengths.length > 0 ? (
                        score.strengths.map((strength, i) => (
                          <li key={i} className="flex gap-2">
                            <Check className="mt-0.5 h-4 w-4 flex-shrink-0 text-secondary" />
                            <span>{strength}</span>
                          </li>
                        ))
                      ) : (
                        <li className="flex gap-2 text-slate-400">
                          <Check className="mt-0.5 h-4 w-4 flex-shrink-0 text-secondary opacity-50" />
                          <span>No standout strengths recorded.</span>
                        </li>
                      )}
                    </ul>
                  </div>
                  <div>
                    <div className="mb-2 flex items-center gap-2 text-warning">
                      <TrendingDown className="h-4 w-4" />
                      <span className="font-semibold uppercase tracking-wide">Weaknesses</span>
                    </div>
                    <ul className="space-y-1 text-slate-300">
                      {score.weaknesses.length > 0 ? (
                        score.weaknesses.map((weakness, i) => (
                          <li key={i} className="flex gap-2">
                            <X className="mt-0.5 h-4 w-4 flex-shrink-0 text-warning" />
                            <span>{weakness}</span>
                          </li>
                        ))
                      ) : (
                        <li className="flex gap-2 text-slate-400">
                          <X className="mt-0.5 h-4 w-4 flex-shrink-0 text-warning opacity-50" />
                          <span>No critical weaknesses identified.</span>
                        </li>
                      )}
                    </ul>
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      ),
    },
    {
      id: 'critique',
      label: 'Full Critique',
      content: (
        <div className="space-y-6">
          <Card>
            <h3 className="mb-4 text-2xl font-semibold text-white">Executive Summary</h3>
            <p className="text-sm leading-relaxed text-slate-200">
              {safeEvaluation.full_critique.summary || 'No summary provided.'}
            </p>
          </Card>

          {safeEvaluation.critique_domains.map((domain, domainIndex) => {
            const domainName = domain.name || domain.domain;
            const domainIssues = safeEvaluation.full_critique.issues.filter(
              (issue) => issue.domain === domainName || issue.category === domainName,
            );
            const domainRecommendations = safeEvaluation.full_critique.recommendations.filter(
              (rec) => rec.domain === domainName,
            );

            return (
              <Card key={domainIndex} className="space-y-6">
                <div className="flex flex-wrap items-center justify-between gap-3 border-b border-white/10 pb-4">
                  <div>
                    <p className="text-sm uppercase tracking-[0.3em] text-secondary">{domainName}</p>
                    <h4 className="text-lg font-semibold text-white">Domain insight</h4>
                  </div>
                  <div className="flex items-center gap-2 rounded-2xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-semibold text-secondary">
                    <Sparkles className="h-4 w-4" />
                    Score {domain.score}/10
                  </div>
                </div>

                <div className="space-y-6">
                  <div>
                    <div className="mb-3 flex items-center gap-2 text-warning">
                      <AlertTriangle className="h-5 w-5" />
                      <span className="text-sm font-semibold uppercase tracking-wide">Issues</span>
                    </div>
                    {domainIssues.length > 0 ? (
                      <div className="space-y-3">
                        {domainIssues.map((issue, issueIndex) => {
                          const severityConfig = {
                            high: 'border-error/50 bg-error/10 text-error',
                            medium: 'border-warning/50 bg-warning/10 text-warning',
                            low: 'border-secondary/40 bg-secondary/5 text-secondary',
                          } as const;
                          const severityClass = severityConfig[issue.severity];

                          return (
                            <div
                              key={issueIndex}
                              className={`rounded-2xl border px-4 py-3 text-sm ${severityClass}`}
                            >
                              <div className="flex items-center justify-between">
                                <span className="uppercase tracking-wide">{issue.severity} severity</span>
                              </div>
                              <p className="mt-2 text-slate-200">{issue.description}</p>
                            </div>
                          );
                        })}
                      </div>
                    ) : (
                      <p className="text-sm text-slate-400">No critical issues flagged in this domain.</p>
                    )}
                  </div>

                  <div>
                    <div className="mb-3 flex items-center gap-2 text-secondary">
                      <ShieldCheck className="h-5 w-5" />
                      <span className="text-sm font-semibold uppercase tracking-wide">Recommendations</span>
                    </div>
                    {domainRecommendations.length > 0 ? (
                      <div className="space-y-3">
                        {domainRecommendations.map((rec, recIndex) => {
                          const priorityConfig = {
                            high: 'text-white border-secondary/60 bg-secondary/15',
                            medium: 'text-white border-primary/60 bg-primary/10',
                            low: 'text-slate-200 border-white/10 bg-white/5',
                          } as const;
                          const priorityClass = priorityConfig[rec.priority];

                          return (
                            <div
                              key={recIndex}
                              className={`rounded-2xl border px-4 py-3 text-sm leading-relaxed ${priorityClass}`}
                            >
                              <p className="mb-1 text-xs uppercase tracking-wide">{rec.priority} priority</p>
                              <p>{rec.recommendation}</p>
                            </div>
                          );
                        })}
                      </div>
                    ) : (
                      <p className="text-sm text-slate-400">No recommendations recorded for this domain.</p>
                    )}
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      ),
    },
    {
      id: 'summary',
      label: 'Narrative Summary',
      content: safeEvaluation.summary && Object.keys(safeEvaluation.summary).length > 0 ? (
        <Card>
          <div className="space-y-6">
            <div className="flex items-center gap-2 text-secondary">
              <FolderOpen className="h-5 w-5" />
              <h3 className="text-2xl font-semibold text-white">Section breakdown</h3>
            </div>
            {Object.entries(safeEvaluation.summary).map(([section, data]) => {
              const formattedSection = section.replace(/([a-z])([A-Z])/g, '$1 $2');

              return (
                <div key={section} className="rounded-2xl border border-white/10 bg-white/5 p-5">
                  <h4 className="text-lg font-semibold text-white">{formattedSection}</h4>
                  {data.text && (
                    <p className="mt-2 text-sm leading-relaxed text-slate-200">{data.text}</p>
                  )}
                  {Array.isArray(data.notes) && data.notes.length > 0 && (
                    <div className="mt-3 space-y-1 text-sm text-slate-300">
                      <p className="text-xs font-semibold uppercase tracking-wide text-secondary">Notes</p>
                      <ul className="list-disc pl-4">
                        {data.notes.map((note, i) => (
                          <li key={i}>{note}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {typeof data.notes === 'string' && (
                    <div className="mt-3 text-sm text-slate-300">
                      <p className="text-xs font-semibold uppercase tracking-wide text-secondary">Notes</p>
                      <p>{data.notes}</p>
                    </div>
                  )}
                  {Array.isArray(data.references) && data.references.length > 0 && (
                    <div className="mt-3 space-y-1 text-sm text-slate-300">
                      <p className="text-xs font-semibold uppercase tracking-wide text-secondary">References</p>
                      <ul className="list-disc pl-4">
                        {data.references.map((ref, i) => (
                          <li key={i}>{ref}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </Card>
      ) : (
        <Card>
          <p className="text-sm text-slate-400">No narrative summary available for this evaluation.</p>
        </Card>
      ),
    },
    {
      id: 'budget',
      label: 'Budget Analysis',
      content: (
        <div className="space-y-6">
          <Card>
            <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
              <div>
                <p className="text-xs uppercase tracking-[0.3em] text-secondary">Budget Overview</p>
                <h3 className="text-2xl font-semibold text-white">Resource allocation snapshot</h3>
              </div>
              <div className="text-right">
                <p className="text-xs uppercase tracking-wide text-slate-400">Total budget</p>
                <p className="text-3xl font-bold text-secondary">
                  ${safeEvaluation.budget_analysis.totalBudget.toLocaleString()}
                </p>
              </div>
            </div>

            <div className="space-y-4">
              {safeEvaluation.budget_analysis.breakdown.map((item, index) => {
                const normalizedPercentage = Math.min(100, Math.round(item.percentage / 5) * 5);
                const widthClass =
                  budgetWidthClasses[normalizedPercentage as keyof typeof budgetWidthClasses] ?? 'w-[0%]';

                return (
                  <div key={index} className="space-y-2">
                    <div className="flex items-center justify-between text-sm text-slate-300">
                      <span>{item.category}</span>
                      <div className="flex items-center gap-3 font-semibold text-white">
                        <span className="text-slate-400">{item.percentage}%</span>
                        <span>${item.amount.toLocaleString()}</span>
                      </div>
                    </div>
                    <div className="h-2 w-full overflow-hidden rounded-full bg-white/10">
                      <div className={`h-full rounded-full bg-gradient-primary transition-all duration-200 ${widthClass}`} />
                    </div>
                  </div>
                );
              })}
            </div>
          </Card>

          <Card>
            <div className="flex items-center gap-2 text-secondary">
              <Layers className="h-5 w-5" />
              <h3 className="text-2xl font-semibold text-white">Budget Flags</h3>
            </div>
            <div className="mt-4 space-y-3">
              {safeEvaluation.budget_analysis.flags.length === 0 && (
                <p className="text-sm text-slate-400">
                  No budget irregularities detected across the reviewed sections.
                </p>
              )}
              {safeEvaluation.budget_analysis.flags.map((flag, index) => {
                const flagConfig = {
                  warning: 'border-warning/50 bg-warning/10 text-warning',
                  error: 'border-error/50 bg-error/10 text-error',
                  info: 'border-secondary/40 bg-secondary/10 text-secondary',
                } as const;
                const flagClass = flagConfig[flag.type];
                const Icon = flag.type === 'error' ? XCircle : flag.type === 'warning' ? AlertTriangle : DollarSign;

                return (
                  <div key={index} className={`flex gap-3 rounded-2xl border px-4 py-3 text-sm ${flagClass}`}>
                    <Icon className="mt-0.5 h-4 w-4 flex-shrink-0" />
                    <p className="text-slate-100">{flag.message}</p>
                  </div>
                );
              })}
            </div>
            {safeEvaluation.budget_analysis.summary && (
              <div className="mt-6 rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-slate-300">
                <p className="text-xs font-semibold uppercase tracking-wide text-secondary">Summary</p>
                <p className="mt-2 leading-relaxed text-slate-200">
                  {safeEvaluation.budget_analysis.summary}
                </p>
              </div>
            )}
          </Card>
        </div>
      ),
    },
  ];

  if (safeEvaluation.plagiarism_check) {
    tabs.push({
      id: 'plagiarism',
      label: 'Plagiarism Check',
      content: (
        <Card>
          <div className="space-y-6">
            <div className="flex items-center gap-2 text-secondary">
              <ShieldAlert className="h-5 w-5" />
              <h3 className="text-2xl font-semibold text-white">Plagiarism Detection</h3>
            </div>

            {safeEvaluation.plagiarism_check.error ? (
              <div className="rounded-2xl border border-error/60 bg-error/10 p-4 text-sm text-error">
                Error: {safeEvaluation.plagiarism_check.error}
              </div>
            ) : (
              <div className="space-y-5">
                <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
                  <div className="flex items-center justify-between">
                    <span className="text-sm uppercase tracking-wide text-slate-400">Risk level</span>
                    <span
                      className={`text-xl font-bold ${
                        plagiarismRisk === 'HIGH'
                          ? 'text-error'
                          : plagiarismRisk === 'MEDIUM'
                          ? 'text-warning'
                          : 'text-secondary'
                      }`}
                    >
                      {plagiarismRisk}
                    </span>
                  </div>
                  {plagiarismSimilarity !== undefined && (
                    <div className="mt-4 flex items-center justify-between text-sm text-slate-300">
                      <span>Similarity score</span>
                      <span className="text-lg font-semibold text-white">
                        {(plagiarismSimilarity * 100).toFixed(1)}%
                      </span>
                    </div>
                  )}
                </div>

                {safeEvaluation.plagiarism_check.matched_reference_text && (
                  <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
                    <p className="text-xs font-semibold uppercase tracking-wide text-secondary">
                      Matched reference text
                    </p>
                    <p className="mt-3 text-sm italic text-slate-200">
                      "{safeEvaluation.plagiarism_check.matched_reference_text.slice(0, 320)}..."
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        </Card>
      ),
    });
  }

  return (
    <div className="mx-auto max-w-6xl space-y-10 px-4 pb-24 pt-10 lg:px-8">
      <Card className="space-y-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <DecisionBadge />
          <Button onClick={handleDownloadPDF} className="flex items-center gap-2">
            <Download className="h-5 w-5" />
            Download report
          </Button>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          {summaryMetrics.map(({ label, value, icon: Icon, accent }) => (
            <div key={label} className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <div className="mb-2 flex items-center gap-2 text-xs uppercase tracking-wide text-slate-400">
                <Icon className="h-4 w-4 text-secondary" />
                {label}
              </div>
              <p className={`text-lg font-semibold ${accent}`}>{value}</p>
            </div>
          ))}
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          {quickFacts.map(({ label, value, hint }) => (
            <div key={label} className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm" title={hint ?? value}>
              <p className="text-xs uppercase tracking-wide text-slate-400">{label}</p>
              <p className="mt-2 truncate text-slate-200">{value}</p>
            </div>
          ))}
        </div>
      </Card>

      <Tabs tabs={tabs} defaultTab="visual" />
    </div>
  );
}
