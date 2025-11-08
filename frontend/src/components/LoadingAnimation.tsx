import { AlertTriangle } from 'lucide-react';

import { pipelineStages, type StageStatus } from './pipelineStages';

interface LoadingAnimationProps {
  stageStatuses: StageStatus[];
  progress: number;
  message?: string;
  isError?: boolean;
}

const progressWidths: Record<number, string> = {
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
  100: 'w-[100%]'
};

export function LoadingAnimation({ stageStatuses, progress, message, isError = false }: LoadingAnimationProps) {
  const clampedProgress = Math.max(0, Math.min(100, progress));
  const activeIndex = stageStatuses.findIndex((status) => status === 'active');
  const completedCount = stageStatuses.filter((status) => status === 'complete').length;
  const derivedIndex = activeIndex >= 0 ? activeIndex : Math.min(completedCount, pipelineStages.length - 1);
  const currentStage = pipelineStages[derivedIndex] ?? pipelineStages[pipelineStages.length - 1];
  const StageIcon = isError ? AlertTriangle : currentStage.icon;
  const progressValue = clampedProgress;
  const progressStep = Math.min(100, Math.round(progressValue / 5) * 5);
  const progressWidthClass = progressWidths[progressStep as keyof typeof progressWidths] ?? 'w-[0%]';
  const ringRadius = 68;
  const ringCircumference = 2 * Math.PI * ringRadius;
  const ringOffset = ringCircumference * (1 - progressValue / 100);
  const headline = isError ? 'Evaluation interrupted' : 'AI review in progress';
  const infoText =
    message ?? 'We are orchestrating multiple AI agents to critique, benchmark, and validate your submission.';
  const ringStrokeClass = isError ? 'stroke-error' : 'stroke-secondary';
  const progressTextClass = isError ? 'text-error' : 'text-secondary';
  const statusPillClass = isError ? 'text-error' : 'text-secondary';
  const footerCopy = isError
    ? 'Please retry once the issue is resolved. Your upload stays encrypted during processing.'
    : 'We never store your documents longer than necessary. You will be redirected as soon as the full critique package is ready.';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-midnight-900/95 backdrop-blur-xl">
      <div className="mx-4 w-full max-w-4xl">
        <div className="card-premium relative overflow-hidden p-8 md:p-12">
          <div className="absolute -right-32 top-1/2 h-72 w-72 -translate-y-1/2 rounded-full bg-secondary/10 blur-3xl" />
          <div className="absolute -left-24 -top-24 h-52 w-52 rounded-full bg-primary/10 blur-3xl" />

          <div className="relative grid gap-10 lg:grid-cols-[0.9fr,1.1fr]">
            <div className="flex flex-col items-center justify-center gap-6 rounded-3xl border border-white/10 bg-white/5 p-8 text-center">
              <div className="relative h-44 w-44">
                <svg viewBox="0 0 160 160" className="h-full w-full">
                  <circle
                    className="stroke-white/10"
                    strokeWidth="10"
                    fill="transparent"
                    r={ringRadius}
                    cx="80"
                    cy="80"
                  />
                  <circle
                    className={ringStrokeClass}
                    strokeWidth="10"
                    strokeLinecap="round"
                    fill="transparent"
                    r={ringRadius}
                    cx="80"
                    cy="80"
                    strokeDasharray={ringCircumference.toString()}
                    strokeDashoffset={ringOffset.toString()}
                    transform="rotate(-90 80 80)"
                  />
                </svg>
                <div className="absolute inset-6 flex items-center justify-center rounded-full bg-surface-900/90 shadow-inner">
                  <StageIcon className={`h-10 w-10 ${statusPillClass}`} />
                </div>
              </div>
              <div className="space-y-2">
                <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Processing grant</p>
                <h2 className="text-xl font-semibold text-white">{headline}</h2>
                <p className="text-sm text-slate-400">{infoText}</p>
              </div>
              <div className="w-full space-y-2">
                <div className="flex items-center justify-between text-sm text-slate-400">
                  <span>Overall progress</span>
                  <span className={`font-semibold ${progressTextClass}`}>{Math.round(progressValue)}%</span>
                </div>
                <div className="h-3 w-full overflow-hidden rounded-full bg-white/10">
                  <div className={`h-full rounded-full bg-gradient-primary transition-all duration-200 ease-out ${progressWidthClass}`} />
                </div>
              </div>
            </div>

            <div className="space-y-5">
              <h3 className="text-lg font-semibold text-white">Pipeline status</h3>
              <div className="space-y-3.5">
                {pipelineStages.map((stage, index) => {
                  const Icon = stage.icon;
                  const status = stageStatuses[index] ?? 'pending';
                  const isComplete = status === 'complete';
                  const isActive = status === 'active';
                  const statusText = isError && isActive ? 'Issue detected' : isActive ? 'Running now…' : isComplete ? 'Completed' : 'Pending';

                  return (
                    <div
                      key={stage.label}
                      className={`group flex items-start gap-3 rounded-2xl border border-white/5 px-4 py-3 transition-all ${
                        isActive
                          ? 'border-secondary/60 bg-secondary/10'
                          : isComplete
                          ? 'border-white/10 bg-white/5 opacity-90'
                          : 'border-white/5 bg-white/10 opacity-60'
                      }`}
                    >
                      <div
                        className={`mt-0.5 flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-xl text-sm ${
                          isComplete
                            ? 'bg-secondary/20 text-secondary'
                            : isActive
                            ? 'bg-secondary/25 text-secondary'
                            : 'bg-white/10 text-slate-400'
                        }`}
                      >
                          <Icon className="h-4 w-4" />
                      </div>
                      <div>
                        <p className={`text-sm font-semibold ${isActive ? 'text-white' : 'text-slate-300'}`}>
                          {stage.label}
                        </p>
                          <p className={`text-xs ${isError && isActive ? 'text-error' : 'text-slate-400'}`}>
                            {statusText}
                        </p>
                      </div>
                    </div>
                  );
                })}
              </div>

              <p className={`text-xs ${isError ? 'text-error/80' : 'text-slate-500'}`}>{footerCopy}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
