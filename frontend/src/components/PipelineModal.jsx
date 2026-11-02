import React, { useEffect, useState } from 'react';
import { ShieldCheck, CheckCircle2, Loader2, Sparkles } from 'lucide-react';
import { PIPELINE_STEPS } from '../utils/constants';

export const PipelineModal = ({ isOpen, onComplete }) => {
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    if (!isOpen) {
      setCurrentStep(0);
      return;
    }

    const interval = setInterval(() => {
      setCurrentStep(prev => {
        if (prev < PIPELINE_STEPS.length - 1) {
          return prev + 1;
        } else {
          clearInterval(interval);
          setTimeout(() => {
            onComplete();
          }, 350);
          return prev;
        }
      });
    }, 180); // Smooth 180ms per step

    return () => clearInterval(interval);
  }, [isOpen]);

  if (!isOpen) return null;

  const progressPct = Math.round(((currentStep + 1) / PIPELINE_STEPS.length) * 100);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fadeIn">
      <div className="glass-panel w-full max-w-lg rounded-2xl p-6 border border-blue-500/30 shadow-2xl shadow-blue-500/20 space-y-6">
        
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400">
              <Sparkles className="w-5 h-5 animate-spin" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">
                Multi-Factor Intelligence Pipeline
              </h3>
              <p className="text-xs text-slate-400">
                Executing 10-tier linguistic & machine learning models
              </p>
            </div>
          </div>
          <span className="text-xs font-mono font-bold text-blue-400 bg-blue-500/10 px-2 py-1 rounded border border-blue-500/20">
            {progressPct}%
          </span>
        </div>

        {/* Live Progress Bar */}
        <div className="space-y-1.5">
          <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
            <div 
              className="bg-gradient-to-r from-blue-600 to-indigo-500 h-2 rounded-full transition-all duration-200"
              style={{ width: `${progressPct}%` }}
            />
          </div>
          <p className="text-xs font-medium text-blue-300 font-mono flex items-center gap-2">
            <Loader2 className="w-3.5 h-3.5 animate-spin text-blue-400" />
            {PIPELINE_STEPS[currentStep]}...
          </p>
        </div>

        {/* Step Items List */}
        <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
          {PIPELINE_STEPS.map((step, idx) => {
            const isFinished = idx < currentStep;
            const isCurrent = idx === currentStep;

            return (
              <div 
                key={step}
                className={`flex items-center gap-3 p-2 rounded-lg text-xs transition-all ${
                  isCurrent 
                    ? 'bg-blue-600/15 text-white border border-blue-500/30 font-semibold' 
                    : isFinished 
                    ? 'text-slate-300' 
                    : 'text-slate-600'
                }`}
              >
                {isFinished ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                ) : isCurrent ? (
                  <Loader2 className="w-4 h-4 text-blue-400 animate-spin shrink-0" />
                ) : (
                  <div className="w-4 h-4 rounded-full border border-slate-700 shrink-0 flex items-center justify-center text-[9px] text-slate-600 font-mono">
                    {idx + 1}
                  </div>
                )}
                <span className="truncate">Step {idx + 1}: {step}</span>
              </div>
            );
          })}
        </div>

        <div className="text-[11px] text-slate-500 text-center">
          Inference running via Scikit-Learn TF-IDF vectorizer & ensemble rules
        </div>
      </div>
    </div>
  );
};
