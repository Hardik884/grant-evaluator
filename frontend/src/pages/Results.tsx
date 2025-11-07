import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Download, CheckCircle, XCircle, AlertCircle, TrendingUp, TrendingDown, Check, X, AlertTriangle, DollarSign, Brain, FileText, ShieldAlert } from 'lucide-react';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { Tabs } from '../components/Tabs';
import { RadarChartComponent } from '../components/charts/RadarChart';
import { BarChartComponent } from '../components/charts/BarChart';
import { evaluationService } from '../services/evaluationService';
import type { Evaluation } from '../types/evaluation';

export function Results() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [evaluation, setEvaluation] = useState<Evaluation | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!id) {
      navigate('/');
      return;
    }

    loadEvaluation(id);
  }, [id, navigate]);

  const loadEvaluation = async (evaluationId: string) => {
    try {
      const data = await evaluationService.getEvaluationById(evaluationId);
      console.log('Loaded evaluation data:', data);
      if (!data) {
        console.error('No evaluation data returned');
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
  };

  const handleDownloadPDF = () => {
    if (!id) return;
    
    // Create download URL
    const downloadUrl = `http://localhost:8000/api/evaluations/${id}/download`;
    
    // Open in new window to trigger download
    window.open(downloadUrl, '_blank');
  };

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto p-6 flex items-center justify-center min-h-[calc(100vh-4rem)]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-accent-purple"></div>
      </div>
    );
  }

  if (!evaluation) {
    return null;
  }

  // Safety checks for data integrity
  const safeEvaluation = {
    ...evaluation,
    critique_domains: evaluation.critique_domains || [],
    section_scores: evaluation.section_scores || [],
    scores: evaluation.scores || [],
    full_critique: evaluation.full_critique || { summary: '', issues: [], recommendations: [] },
    budget_analysis: evaluation.budget_analysis || { totalBudget: 0, breakdown: [], flags: [], summary: '' },
    summary: evaluation.summary || {},
    plagiarism_check: evaluation.plagiarism_check || null
  };

  const DecisionBadge = () => {
    const config = {
      ACCEPT: { icon: CheckCircle, color: 'text-success', bg: 'bg-success/20', border: 'border-success', shadow: 'shadow-glow-green' },
      REJECT: { icon: XCircle, color: 'text-error', bg: 'bg-error/20', border: 'border-error', shadow: 'shadow-glow-red' },
      REVISE: { icon: AlertCircle, color: 'text-warning', bg: 'bg-warning/20', border: 'border-warning', shadow: 'shadow-glow-purple' },
      'CONDITIONALLY ACCEPT': { icon: CheckCircle, color: 'text-accent-cyan', bg: 'bg-accent-cyan/20', border: 'border-accent-cyan', shadow: 'shadow-glow-cyan' },
    };

    const { icon: Icon, color, bg, border, shadow } = config[safeEvaluation.decision];

    return (
      <div className={`inline-flex items-center gap-2 px-6 py-3 rounded-xl ${bg} ${border} border-2 ${shadow}`}>
        <Icon className={`w-6 h-6 ${color}`} />
        <span className={`text-xl font-bold ${color}`}>{safeEvaluation.decision}</span>
      </div>
    );
  };

  const tabs = [
    {
      id: 'visual',
      label: 'Visual Dashboard',
      content: (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <h3 className="text-xl font-semibold text-gray-200 mb-4">Critique Domains</h3>
            {safeEvaluation.critique_domains.length > 0 ? (
              <RadarChartComponent data={safeEvaluation.critique_domains} />
            ) : (
              <p className="text-gray-400">No critique domain data available</p>
            )}
          </Card>
          <Card>
            <h3 className="text-xl font-semibold text-gray-200 mb-4">Section Scores</h3>
            {safeEvaluation.section_scores.length > 0 ? (
              <BarChartComponent data={safeEvaluation.section_scores} />
            ) : (
              <p className="text-gray-400">No section score data available</p>
            )}
          </Card>
        </div>
      ),
    },
    {
      id: 'detailed',
      label: 'Detailed Scoring',
      content: (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {safeEvaluation.scores.map((score, index) => (
            <Card key={index} hover>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-xl font-semibold text-gray-200">{score.category}</h3>
                  <div className="text-2xl font-bold gradient-text">
                    {score.score}/{score.maxScore}
                  </div>
                </div>

                <div className="space-y-3">
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <TrendingUp className="w-4 h-4 text-success" />
                      <span className="font-medium text-success text-sm">Strengths</span>
                    </div>
                    <ul className="space-y-1">
                      {score.strengths.map((strength, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm text-gray-300">
                          <Check className="w-4 h-4 text-success mt-0.5 flex-shrink-0" />
                          <span>{strength}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <TrendingDown className="w-4 h-4 text-warning" />
                      <span className="font-medium text-warning text-sm">Weaknesses</span>
                    </div>
                    <ul className="space-y-1">
                      {score.weaknesses.map((weakness, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm text-gray-300">
                          <X className="w-4 h-4 text-warning mt-0.5 flex-shrink-0" />
                          <span>{weakness}</span>
                        </li>
                      ))}
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
            <h3 className="text-2xl font-semibold text-gray-200 mb-4">Overall Summary</h3>
            <p className="text-gray-300 leading-relaxed">{safeEvaluation.full_critique.summary}</p>
          </Card>

          {/* Organize by Domain */}
          {safeEvaluation.critique_domains.map((domain, domainIndex) => {
            // Filter issues and recommendations for this domain using explicit domain tag
            const domainName = domain.name || domain.domain;
            const domainIssues = safeEvaluation.full_critique.issues.filter(
              issue => issue.domain === domainName || 
                      (issue.category && issue.category === domainName)
            );
            const domainRecs = safeEvaluation.full_critique.recommendations.filter(
              rec => rec.domain === domainName
            );

            // Always show all domains (don't skip any)
            return (
              <Card key={domainIndex}>
                <div className="mb-4 pb-4 border-b border-charcoal-700">
                  <div className="flex items-center justify-between">
                    <h3 className="text-xl font-semibold text-gray-200">{domainName}</h3>
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-gray-400">Score:</span>
                      <span className="text-lg font-bold gradient-text">{domain.score}/10</span>
                    </div>
                  </div>
                </div>

                {domainIssues.length > 0 ? (
                  <div className="mb-6">
                    <h4 className="text-lg font-semibold text-gray-300 mb-3 flex items-center gap-2">
                      <AlertTriangle className="w-5 h-5 text-warning" />
                      Issues ({domainIssues.length})
                    </h4>
                    <div className="space-y-3">
                      {domainIssues.map((issue, index) => {
                        const severityConfig = {
                          high: { color: 'text-error', bg: 'bg-error/20', border: 'border-error' },
                          medium: { color: 'text-warning', bg: 'bg-warning/20', border: 'border-warning' },
                          low: { color: 'text-blue-400', bg: 'bg-blue-400/20', border: 'border-blue-400' },
                        };
                        const config = severityConfig[issue.severity];

                        return (
                          <div key={index} className={`p-4 rounded-xl ${config.bg} border ${config.border}`}>
                            <div className="flex items-start gap-3">
                              <span className={`text-xs font-semibold uppercase ${config.color}`}>
                                {issue.severity}
                              </span>
                              <p className="text-sm text-gray-300 flex-1">{issue.description}</p>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                ) : (
                  <div className="mb-6">
                    <p className="text-sm text-gray-400 italic">No issues identified in this domain.</p>
                  </div>
                )}

                {domainRecs.length > 0 ? (
                  <div>
                    <h4 className="text-lg font-semibold text-gray-300 mb-3 flex items-center gap-2">
                      <Check className="w-5 h-5 text-success" />
                      Recommendations ({domainRecs.length})
                    </h4>
                    <div className="space-y-3">
                      {domainRecs.map((rec, index) => {
                        const priorityConfig = {
                          high: { color: 'text-accent-magenta', icon: '!' },
                          medium: { color: 'text-accent-purple', icon: '•' },
                          low: { color: 'text-gray-400', icon: '·' },
                        };
                        const config = priorityConfig[rec.priority];

                        return (
                          <div key={index} className="flex items-start gap-3 p-4 bg-charcoal-900 rounded-xl">
                            <span className={`text-xl font-bold ${config.color}`}>{config.icon}</span>
                            <div className="flex-1">
                              <span className={`text-xs font-semibold uppercase ${config.color} mb-1 block`}>
                                {rec.priority} Priority
                              </span>
                              <p className="text-sm text-gray-300">{rec.recommendation}</p>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                ) : (
                  <div>
                    <p className="text-sm text-gray-400 italic">No recommendations for this domain.</p>
                  </div>
                )}
              </Card>
            );
          })}
        </div>
      ),
    },
    {
      id: 'summary',
      label: 'Summary',
      content: safeEvaluation.summary && Object.keys(safeEvaluation.summary).length > 0 ? (
        <Card>
          <div className="space-y-6">
            <div className="flex items-center gap-2 mb-4">
              <FileText className="w-6 h-6 text-accent-cyan" />
              <h3 className="text-2xl font-semibold text-gray-200">Proposal Summary</h3>
            </div>
            {Object.entries(safeEvaluation.summary).map(([section, data]) => {
              // Add spaces to camelCase section names
              const formattedSection = section.replace(/([a-z])([A-Z])/g, '$1 $2');
              
              return (
                <div key={section} className="p-4 bg-charcoal-900 rounded-xl space-y-3">
                  <h4 className="text-lg font-semibold text-accent-purple">{formattedSection}</h4>
                  {data.text && (
                    <p className="text-gray-300 leading-relaxed">{data.text}</p>
                  )}
                  {data.notes && Array.isArray(data.notes) && data.notes.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-gray-400 mb-2">Notes:</p>
                    <ul className="list-disc list-inside space-y-1">
                      {data.notes.map((note, i) => (
                        <li key={i} className="text-sm text-gray-300">{note}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {data.notes && typeof data.notes === 'string' && (
                  <div>
                    <p className="text-sm font-medium text-gray-400 mb-2">Notes:</p>
                    <p className="text-sm text-gray-300">{data.notes}</p>
                  </div>
                )}
                {data.references && Array.isArray(data.references) && data.references.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-gray-400 mb-2">References:</p>
                    <ul className="list-disc list-inside space-y-1">
                      {data.references.map((ref, i) => (
                        <li key={i} className="text-sm text-gray-300">{ref}</li>
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
          <p className="text-gray-400">No summary available.</p>
        </Card>
      ),
    },
    {
      id: 'budget',
      label: 'Budget Analysis',
      content: (
        <div className="space-y-6">
          <Card>
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-2xl font-semibold text-gray-200">Budget Overview</h3>
              <div className="text-right">
                <p className="text-sm text-gray-400">Total Budget</p>
                <p className="text-3xl font-bold gradient-text">
                  ${safeEvaluation.budget_analysis.totalBudget.toLocaleString()}
                </p>
              </div>
            </div>

            <div className="space-y-3">
              {safeEvaluation.budget_analysis.breakdown.map((item, index) => (
                <div key={index} className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-300">{item.category}</span>
                    <div className="flex items-center gap-3">
                      <span className="text-gray-400">{item.percentage}%</span>
                      <span className="font-semibold text-gray-200">
                        ${item.amount.toLocaleString()}
                      </span>
                    </div>
                  </div>
                  <div className="w-full bg-charcoal-700 rounded-full h-2 overflow-hidden">
                    <div
                      className="h-full bg-gradient-primary transition-all duration-500"
                      style={{ width: `${item.percentage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </Card>

          <Card>
            <h3 className="text-2xl font-semibold text-gray-200 mb-4">Budget Flags</h3>
            <div className="space-y-3">
              {safeEvaluation.budget_analysis.flags.map((flag, index) => {
                const flagConfig = {
                  warning: { icon: AlertTriangle, color: 'text-warning', bg: 'bg-warning/20', border: 'border-warning' },
                  error: { icon: XCircle, color: 'text-error', bg: 'bg-error/20', border: 'border-error' },
                  info: { icon: DollarSign, color: 'text-blue-400', bg: 'bg-blue-400/20', border: 'border-blue-400' },
                };
                const config = flagConfig[flag.type];
                const Icon = config.icon;

                return (
                  <div key={index} className={`flex items-start gap-3 p-4 rounded-xl ${config.bg} border ${config.border}`}>
                    <Icon className={`w-5 h-5 ${config.color} mt-0.5 flex-shrink-0`} />
                    <p className="text-sm text-gray-300">{flag.message}</p>
                  </div>
                );
              })}
            </div>
          </Card>

          <Card>
            <h3 className="text-2xl font-semibold text-gray-200 mb-4">Summary</h3>
            <p className="text-gray-300 leading-relaxed">{safeEvaluation.budget_analysis.summary}</p>
          </Card>
        </div>
      ),
    },
  ];

  // Add plagiarism tab if plagiarism check was run
  if (safeEvaluation.plagiarism_check) {
    tabs.push({
      id: 'plagiarism',
      label: 'Plagiarism Check',
      content: (
        <Card>
          <div className="space-y-6">
            <div className="flex items-center gap-2 mb-4">
              <ShieldAlert className="w-6 h-6 text-accent-magenta" />
              <h3 className="text-2xl font-semibold text-gray-200">Plagiarism Detection Results</h3>
            </div>

            {safeEvaluation.plagiarism_check.error ? (
              <div className="p-4 bg-error/20 border border-error rounded-xl">
                <p className="text-error">Error: {safeEvaluation.plagiarism_check.error}</p>
              </div>
            ) : (
              <div className="space-y-4">
                <div className={`p-6 rounded-xl border-2 ${
                  safeEvaluation.plagiarism_check.risk_level === 'HIGH' ? 'bg-error/20 border-error' :
                  safeEvaluation.plagiarism_check.risk_level === 'MEDIUM' ? 'bg-warning/20 border-warning' :
                  'bg-success/20 border-success'
                }`}>
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-lg font-semibold text-gray-200">Risk Level</span>
                    <span className={`text-2xl font-bold ${
                      safeEvaluation.plagiarism_check.risk_level === 'HIGH' ? 'text-error' :
                      safeEvaluation.plagiarism_check.risk_level === 'MEDIUM' ? 'text-warning' :
                      'text-success'
                    }`}>
                      {safeEvaluation.plagiarism_check.risk_level}
                    </span>
                  </div>
                  {safeEvaluation.plagiarism_check.similarity_score !== undefined && (
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-300">Similarity Score</span>
                      <span className="text-xl font-bold text-gray-200">
                        {(safeEvaluation.plagiarism_check.similarity_score * 100).toFixed(1)}%
                      </span>
                    </div>
                  )}
                </div>

                {safeEvaluation.plagiarism_check.matched_reference_text && (
                  <div className="p-4 bg-charcoal-900 rounded-xl">
                    <h4 className="text-sm font-semibold text-gray-400 mb-2">Matched Reference Text</h4>
                    <p className="text-sm text-gray-300 italic">
                      "{safeEvaluation.plagiarism_check.matched_reference_text.slice(0, 300)}..."
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
    <div className="max-w-7xl mx-auto p-6 space-y-6 animate-fade-in">
      <Card className="bg-gradient-dark">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <DecisionBadge />
              <div className="text-5xl font-bold gradient-text">
                {safeEvaluation.overall_score.toFixed(2)}/10
              </div>
            </div>
            <div>
              <div className="flex items-center gap-2 mb-1">
                <Brain className="w-4 h-4 text-accent-purple" />
                <p className="text-sm font-semibold text-accent-purple">
                  Domain: {safeEvaluation.domain || 'Unknown'}
                </p>
              </div>
              <p className="text-sm text-gray-400">File: {safeEvaluation.file_name}</p>
              <p className="text-sm text-gray-400">
                Evaluated: {new Date(safeEvaluation.created_at).toLocaleDateString()}
              </p>
            </div>
          </div>
          <Button onClick={handleDownloadPDF} className="flex items-center gap-2">
            <Download className="w-5 h-5" />
            Download PDF Report
          </Button>
        </div>
      </Card>

      <Tabs tabs={tabs} defaultTab="visual" />
    </div>
  );
}
