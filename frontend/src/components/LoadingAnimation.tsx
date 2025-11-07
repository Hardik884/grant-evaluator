import { useEffect, useState } from 'react';
import { Sparkles, FileSearch, BarChart3, CheckCircle2, Brain, DollarSign, AlertTriangle } from 'lucide-react';

const stages = [
  { icon: FileSearch, label: 'Loading document and analyzing pages', duration: 2000 },
  { icon: Brain, label: 'Detecting research domain', duration: 1500 },
  { icon: Sparkles, label: 'Generating structured summary', duration: 3000 },
  { icon: BarChart3, label: 'Running scoring analysis', duration: 2500 },
  { icon: AlertTriangle, label: 'Generating detailed critique', duration: 2500 },
  { icon: DollarSign, label: 'Evaluating budget breakdown', duration: 2000 },
  { icon: CheckCircle2, label: 'Finalizing decision and scores', duration: 1500 }
];

export function LoadingAnimation() {
  const [currentStage, setCurrentStage] = useState(0);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    // Update stage
    if (currentStage >= stages.length) return;

    const timer = setTimeout(() => {
      setCurrentStage(prev => prev + 1);
    }, stages[currentStage].duration);

    return () => clearTimeout(timer);
  }, [currentStage]);

  useEffect(() => {
    // Smooth progress bar animation
    const targetProgress = Math.min(100, ((currentStage + 1) / stages.length) * 100);
    
    setProgress(prev => {
      // Smoothly animate to target, but never exceed 100
      const diff = targetProgress - prev;
      if (Math.abs(diff) < 0.1) return targetProgress;
      return Math.min(100, prev + diff * 0.3);
    });
  }, [currentStage]);

  return (
    <div className="fixed inset-0 bg-navy-900/95 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="max-w-md w-full mx-4">
        <div className="card-premium p-8">
          <div className="flex flex-col items-center gap-6">
            <div className="relative">
              <div className="w-24 h-24 rounded-full bg-gradient-primary opacity-20 animate-pulse-slow"></div>
              <div className="absolute inset-0 flex items-center justify-center">
                {stages.map((stage, index) => {
                  const Icon = stage.icon;
                  return (
                    <Icon
                      key={index}
                      className={`absolute w-12 h-12 transition-all duration-500 ${
                        index === currentStage
                          ? 'text-accent-magenta scale-100 opacity-100'
                          : index < currentStage
                          ? 'text-success scale-75 opacity-0'
                          : 'text-gray-600 scale-75 opacity-0'
                      }`}
                    />
                  );
                })}
              </div>
            </div>

            {/* Progress Bar */}
            <div className="w-full space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-400">Progress</span>
                <span className="text-accent-magenta font-semibold">{Math.round(progress)}%</span>
              </div>
              <div className="w-full h-2 bg-charcoal-800 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-primary transition-all duration-300 ease-out"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>

            {/* Stage List */}
            <div className="w-full space-y-3">
              {stages.map((stage, index) => (
                <div key={index} className="flex items-center gap-3">
                  <div
                    className={`w-3 h-3 rounded-full transition-all duration-300 ${
                      index < currentStage
                        ? 'bg-success shadow-glow-green'
                        : index === currentStage
                        ? 'bg-accent-magenta shadow-glow-pink animate-pulse'
                        : 'bg-charcoal-700'
                    }`}
                  />
                  <span
                    className={`text-sm transition-colors duration-300 ${
                      index <= currentStage ? 'text-gray-200 font-medium' : 'text-gray-500'
                    }`}
                  >
                    {stage.label}
                  </span>
                </div>
              ))}
            </div>

            <p className="text-sm text-gray-400 text-center mt-4">
              This may take a minute... Our AI is thoroughly analyzing your proposal.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
