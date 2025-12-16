import { useState, useRef, DragEvent, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, FileText, X, Brain, ShieldCheck, Sparkles, ArrowRight, ShieldAlert, LineChart } from 'lucide-react';
import { Button } from '../components/Button';
import { LoadingAnimation } from '../components/LoadingAnimation';
import { evaluationService } from '../services/evaluationService';
import { pipelineStages, type StageStatus } from '../components/pipelineStages';

const rawApiBase = ((import.meta as unknown) as { env?: Record<string, string | undefined> }).env?.VITE_API_BASE_URL
  || 'http://localhost:8000/api';
let API_BASE_URL = String(rawApiBase ?? '').replace(/\/+$/g, '');
if (!API_BASE_URL.endsWith('/api')) {
  API_BASE_URL = API_BASE_URL + '/api';
}

const deriveWebSocketBase = (apiUrl: string): string => {
  // Remove trailing slashes and /api suffix
  let trimmed = apiUrl.replace(/\/+$/, '');
  if (trimmed.endsWith('/api')) {
    trimmed = trimmed.slice(0, -4);
  }
  
  // Convert http(s):// to ws(s)://
  if (trimmed.startsWith('https://')) {
    return trimmed.replace('https://', 'wss://');
  }
  if (trimmed.startsWith('http://')) {
    return trimmed.replace('http://', 'ws://');
  }
  
  // Fallback: assume it's already a WebSocket URL or localhost
  return trimmed;
};

const WS_BASE_URL = deriveWebSocketBase(API_BASE_URL);

const featureHighlights = [
  {
    title: 'Domain-aware intelligence',
    description: 'Auto-classify proposals across specialised research domains to contextualise every score.',
    icon: Brain,
  },
  {
    title: 'Narrative-ready critiques',
    description: 'AI-crafted feedback you can forward to applicants without additional editing.',
    icon: Sparkles,
  },
  {
    title: 'Adaptive scoring framework',
    description: 'Balanced evaluation matrix that weighs innovation, impact, feasibility, and compliance.',
    icon: LineChart,
  },
  {
    title: 'Immediate risk detection',
    description: 'Flag budget anomalies, eligibility gaps, and plagiarism patterns before review meetings.',
    icon: ShieldAlert,
  },
];

export function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [domains, setDomains] = useState<string[]>([]);
  const [selectedDomain, setSelectedDomain] = useState<string>('');
  const [checkPlagiarism, setCheckPlagiarism] = useState(false);
  const [useAutoDomain, setUseAutoDomain] = useState(true);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();
  const [stageStatuses, setStageStatuses] = useState<StageStatus[]>(() => pipelineStages.map(() => 'pending'));
  const [pipelineProgress, setPipelineProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState<string>('Preparing evaluation pipeline...');
  const [pipelineError, setPipelineError] = useState<string | null>(null);
  const websocketRef = useRef<WebSocket | null>(null);
  const stageIndexMap = useMemo(() => {
    const mapping: Record<string, number> = {};
    pipelineStages.forEach((stage, index) => {
      mapping[stage.key] = index;
    });
    return mapping;
  }, []);

  useEffect(() => {
    evaluationService.getDomains().then(setDomains).catch(console.error);
  }, []);

  useEffect(() => {
    return () => {
      const socket = websocketRef.current;
      socket?.close();
    };
  }, []);

  const getStageIndexFromPayload = (payload: unknown): number | null => {
    if (!payload || typeof payload !== 'object') {
      return null;
    }
    const data = payload as Record<string, unknown>;
    if (typeof data.stage_index === 'number' && data.stage_index >= 0) {
      return Math.min(data.stage_index, pipelineStages.length - 1);
    }
    if (typeof data.stage_key === 'string' && stageIndexMap[data.stage_key] !== undefined) {
      return stageIndexMap[data.stage_key];
    }
    return null;
  };

  const handlePipelineEvent = (payload: unknown) => {
    if (!payload || typeof payload !== 'object') {
      return;
    }
    const data = payload as Record<string, unknown>;
    const eventType = typeof data.event === 'string' ? data.event : undefined;

    if (eventType === 'connected') {
      setStageStatuses(pipelineStages.map(() => 'pending'));
      setPipelineProgress(0);
      setStatusMessage('Preparing evaluation pipeline...');
      setPipelineError(null);
      return;
    }

    if (eventType === 'status') {
      const status = typeof data.status === 'string' ? data.status : undefined;
      if (status === 'queued') {
        setStageStatuses(pipelineStages.map(() => 'pending'));
      } else {
        const stageIndex = getStageIndexFromPayload(data);
        if (stageIndex !== null) {
          if (status === 'started') {
            setStageStatuses(
              pipelineStages.map((_, index) => {
                if (index < stageIndex) {
                  return 'complete';
                }
                if (index === stageIndex) {
                  return 'active';
                }
                return 'pending';
              }),
            );
          } else if (status === 'completed') {
            setStageStatuses((prev) => {
              const updated = [...prev];
              updated[stageIndex] = 'complete';
              return updated;
            });
          }
        }
      }

      if (typeof data.progress === 'number') {
        setPipelineProgress(Math.max(0, Math.min(100, data.progress)));
      }

      if (typeof data.message === 'string' && data.message.trim().length > 0) {
        setStatusMessage(data.message);
      }

      setPipelineError(null);
      return;
    }

    if (eventType === 'complete') {
      setStageStatuses(pipelineStages.map(() => 'complete'));
      setPipelineProgress(
        typeof data.progress === 'number' ? Math.max(0, Math.min(100, data.progress)) : 100,
      );
      setStatusMessage('Evaluation complete. Redirecting to results…');
      setPipelineError(null);
      const socket = websocketRef.current;
      socket?.close();
      websocketRef.current = null;
      return;
    }

    if (eventType === 'error') {
      const errorMessage = typeof data.message === 'string' ? data.message : 'Evaluation failed';
      setPipelineError(errorMessage);
      setStatusMessage(errorMessage);
      const socket = websocketRef.current;
      socket?.close();
      websocketRef.current = null;
    }
  };

  const openStatusSocket = (id: string) => {
    try {
      websocketRef.current?.close();
    } catch (error) {
      console.warn('Previous websocket close error:', error);
    }

    try {
      const socket = new WebSocket(`${WS_BASE_URL}/ws/evaluation/${id}`);
      websocketRef.current = socket;

      socket.onopen = () => {
        setPipelineError(null);
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handlePipelineEvent(data);
        } catch (error) {
          console.error('Failed to parse pipeline status message:', error);
        }
      };

      socket.onerror = (error) => {
        console.error('WebSocket error:', error);
        // Only set error if this is an unexpected error, not a normal close
        if (socket.readyState !== WebSocket.CLOSING && socket.readyState !== WebSocket.CLOSED) {
          setPipelineError((prev) => prev ?? 'Connection issue while streaming status updates.');
        }
      };

      socket.onclose = (event) => {
        websocketRef.current = null;
        // Only show error if the close was unexpected (not a normal close with code 1000)
        if (event.code !== 1000 && event.code !== 1001) {
          console.warn(`WebSocket closed unexpectedly with code ${event.code}`);
        }
      };
    } catch (error) {
      console.error('Failed to open websocket for status updates:', error);
      setPipelineError('Unable to connect for live status updates.');
      setStatusMessage('Unable to connect for live status updates.');
    }
  };

  const handleDragOver = (e: DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && isValidFile(droppedFile)) {
      setFile(droppedFile);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile && isValidFile(selectedFile)) {
      setFile(selectedFile);
    }
  };

  const isValidFile = (incomingFile: File) => {
    const validTypes = [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    ];
    return validTypes.includes(incomingFile.type);
  };

  const handleEvaluate = async () => {
    if (!file) {
      alert('Please select a file first');
      return;
    }

    console.log('[DEBUG] Starting evaluation for file:', file.name);
    console.log('[DEBUG] API Base URL:', API_BASE_URL);
    console.log('[DEBUG] WebSocket Base URL:', WS_BASE_URL);

    const newSessionId =
      typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function'
        ? crypto.randomUUID()
        : Math.random().toString(36).slice(2);

    setStageStatuses(pipelineStages.map(() => 'pending'));
    setPipelineProgress(0);
    setStatusMessage('Uploading file and starting evaluation...');
    setPipelineError(null);
    setIsEvaluating(true);

    console.log('[DEBUG] Loading state set to true');

    // openStatusSocket(newSessionId); // Disabled: WebSocket status updates (uncomment to re-enable)

    // Simulate progress updates without websocket - cycle through stages
    let currentStageIndex = 0;
    const progressInterval = setInterval(() => {
      setPipelineProgress((prev) => {
        const next = prev + 3;
        return next >= 95 ? 95 : next;
      });
      
      setStageStatuses((prev) => {
        const updated = [...prev];
        // Mark previous stages as complete
        for (let i = 0; i < currentStageIndex; i++) {
          updated[i] = 'complete';
        }
        // Mark current stage as active
        if (currentStageIndex < pipelineStages.length) {
          updated[currentStageIndex] = 'active';
          // Update status message to current stage
          setStatusMessage(pipelineStages[currentStageIndex].label);
        }
        // Mark future stages as pending
        for (let i = currentStageIndex + 1; i < pipelineStages.length; i++) {
          updated[i] = 'pending';
        }
        return updated;
      });
      
      // Move to next stage
      currentStageIndex++;
      if (currentStageIndex >= pipelineStages.length) {
        currentStageIndex = pipelineStages.length - 1; // Stay on last stage
      }
    }, 3000); // Change stage every 3 seconds

    try {
      const domain = useAutoDomain ? undefined : selectedDomain || undefined;
      console.log('[DEBUG] Sending request to backend...');
      setStatusMessage('Processing grant proposal...');
      const saved = await evaluationService.saveEvaluation(file, domain, checkPlagiarism, newSessionId);
      console.log('[DEBUG] Evaluation saved:', saved);
      clearInterval(progressInterval);
      setPipelineProgress(100);
      setStageStatuses(pipelineStages.map(() => 'complete'));
      setStatusMessage('Evaluation complete! Redirecting to results...');
      setTimeout(() => {
        navigate(`/results/${saved.id}`);
      }, 500);
    } catch (error) {
      clearInterval(progressInterval);
      console.error('[ERROR] Evaluation failed:', error);
      
      let errorMessage = 'Evaluation failed. ';
      if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
        errorMessage += 'Cannot connect to backend. Check: 1) CORS settings on Render (ALLOWED_ORIGINS), 2) Backend is running, 3) VITE_API_BASE_URL is correct in Vercel.';
      } else if (error instanceof Error) {
        errorMessage += error.message;
      } else {
        errorMessage += 'Unknown error occurred.';
      }
      
      setPipelineError(errorMessage);
      setStatusMessage(errorMessage);
      setIsEvaluating(false);
      alert(errorMessage);
      websocketRef.current?.close();
      websocketRef.current = null;
    }
  };

  const removeFile = () => {
    setFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const isEvaluateDisabled = !file || (!useAutoDomain && !selectedDomain);

  return (
    <div className="relative">
      {isEvaluating && (
        <LoadingAnimation
          stageStatuses={stageStatuses}
          progress={pipelineProgress}
          message={statusMessage}
          isError={Boolean(pipelineError)}
        />
      )}

      <div className="mx-auto max-w-5xl space-y-12 px-4 pb-24 pt-16 lg:px-8">
        <section className="space-y-3 text-center">
          <h1 className="text-4xl font-semibold text-white sm:text-5xl">AI Grant Evaluator</h1>
          <p className="mx-auto max-w-2xl text-base text-slate-300">
            Upload a proposal and receive a complete AI-assisted review package in minutes.
          </p>
        </section>

        <section className="relative">
          <div className="pointer-events-none absolute -inset-4 rounded-3xl bg-gradient-primary opacity-15 blur-2xl" />
          <div className="relative rounded-3xl border border-white/10 bg-surface-900/90 p-8 shadow-card backdrop-blur-xl">
            <header className="mb-6 flex items-center justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Review workspace</p>
                <h2 className="text-2xl font-semibold text-white">Upload a proposal</h2>
              </div>
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-primary text-white shadow-glow-primary">
                <Upload className="h-6 w-6" />
              </div>
            </header>

            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className={`group relative flex cursor-pointer flex-col items-center justify-center rounded-2xl border border-dashed border-white/15 bg-surface-800/60 px-6 py-12 text-center transition-all duration-300 ${
                isDragging ? 'border-secondary/70 bg-secondary/5 ring-2 ring-secondary/50' : 'hover:border-secondary/60 hover:bg-white/5'
              }`}
            >
              {!file ? (
                <>
                  <div className="mb-4 flex items-center justify-center">
                    <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-white/5 text-secondary">
                      <Sparkles className="h-8 w-8" />
                    </div>
                  </div>
                  <h3 className="text-lg font-semibold text-white">Drag & drop your grant proposal</h3>
                  <p className="mt-2 max-w-sm text-sm text-slate-400">
                    Secure upload for PDF or DOCX files up to 25 MB.
                  </p>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".pdf,.docx"
                    onChange={handleFileSelect}
                    className="hidden"
                    id="file-upload"
                  />
                  <label
                    htmlFor="file-upload"
                    className="mt-6 inline-flex items-center gap-2 rounded-2xl border border-white/10 bg-white/5 px-5 py-2.5 text-sm font-semibold text-white transition-all duration-300 hover:border-secondary/60 hover:bg-secondary/20"
                  >
                    Browse files
                    <ArrowRight className="h-4 w-4" />
                  </label>
                </>
              ) : (
                <div className="w-full space-y-6 text-left">
                  <div className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/5 p-4">
                    <div className="flex items-center gap-4">
                      <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-primary text-white">
                        <FileText className="h-6 w-6" />
                      </div>
                      <div>
                        <p className="text-sm font-semibold text-white">{file.name}</p>
                        <p className="text-xs text-slate-400">{Math.max(1, Math.round(file.size / 1024))} KB</p>
                      </div>
                    </div>
                    <button
                      onClick={removeFile}
                      className="rounded-xl border border-transparent bg-white/5 p-2 text-slate-300 transition hover:border-white/20 hover:text-white"
                      aria-label="Remove file"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>

                  <div className="space-y-4 rounded-2xl border border-white/10 bg-white/5 p-4">
                    <div className="flex items-center gap-2 text-sm font-semibold text-white/80">
                      <Brain className="h-4 w-4 text-secondary" />
                      Domain classification
                    </div>
                    <label className="flex items-center gap-3 text-sm text-slate-300">
                      <input
                        type="checkbox"
                        checked={useAutoDomain}
                        onChange={(e) => setUseAutoDomain(e.target.checked)}
                        className="h-4 w-4 rounded border-white/20 bg-surface-900 text-secondary focus:ring-secondary"
                      />
                      Auto-detect dominant research domain
                    </label>

                    {!useAutoDomain && (
                      <select
                        value={selectedDomain}
                        onChange={(e) => setSelectedDomain(e.target.value)}
                        className="w-full rounded-2xl border border-white/15 bg-surface-900 px-4 py-3 text-sm text-white focus:border-secondary/60 focus:outline-none"
                        aria-label="Manual domain selection"
                      >
                        <option value="">Select a domain…</option>
                        {domains.map((domain) => (
                          <option key={domain} value={domain}>
                            {domain}
                          </option>
                        ))}
                      </select>
                    )}
                  </div>

                  <div className="space-y-4 rounded-2xl border border-white/10 bg-white/5 p-4">
                    <div className="flex items-center gap-2 text-sm font-semibold text-white/80">
                      <ShieldCheck className="h-4 w-4 text-secondary" />
                      Additional checks
                    </div>
                    <label className="flex items-center gap-3 text-sm text-slate-300">
                      <input
                        type="checkbox"
                        checked={checkPlagiarism}
                        onChange={(e) => setCheckPlagiarism(e.target.checked)}
                        className="h-4 w-4 rounded border-white/20 bg-surface-900 text-secondary focus:ring-secondary"
                      />
                      Run plagiarism scan against indexed research corpus
                    </label>
                  </div>

                  <Button
                    onClick={handleEvaluate}
                    className="w-full"
                    size="lg"
                    disabled={isEvaluateDisabled}
                  >
                    Launch evaluation
                  </Button>
                </div>
              )}
            </div>
          </div>
        </section>

        <section className="space-y-6">
          <div className="space-y-2 text-center">
            <h2 className="text-2xl font-semibold text-white">Why use AI Grant Evaluator</h2>
            <p className="mx-auto max-w-2xl text-sm text-slate-400">
              A focused toolkit that pairs automated scoring with the guardrails reviewers expect.
            </p>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            {featureHighlights.map(({ title, description, icon: Icon }) => (
              <div key={title} className="card-variant flex h-full items-start gap-4 p-5">
                <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl bg-white/5 text-secondary">
                  <Icon className="h-5 w-5" />
                </div>
                <div className="space-y-1">
                  <h3 className="text-base font-semibold text-white">{title}</h3>
                  <p className="text-sm leading-relaxed text-slate-300">{description}</p>
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
