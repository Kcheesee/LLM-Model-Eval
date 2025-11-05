/**
 * Constitutional AI Score Display Component
 * Shows detailed constitutional evaluation with principle breakdown
 */
import { ConstitutionalEvaluation } from '@/types';
import { CheckCircle, XCircle, AlertCircle, Info } from 'lucide-react';

interface ConstitutionalScoreProps {
  data: ConstitutionalEvaluation;
  compact?: boolean;
}

export default function ConstitutionalScore({ data, compact = false }: ConstitutionalScoreProps) {
  const getScoreColor = (score: number) => {
    if (score >= 9) return 'text-green-400';
    if (score >= 7) return 'text-blue-400';
    if (score >= 5) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getScoreBarColor = (score: number) => {
    if (score >= 9) return 'bg-green-500';
    if (score >= 7) return 'bg-blue-500';
    if (score >= 5) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getPassIcon = () => {
    if (data.passed) {
      return <CheckCircle className="w-5 h-5 text-green-400" />;
    }
    return <XCircle className="w-5 h-5 text-red-400" />;
  };

  // Compact view for side-by-side comparisons
  if (compact) {
    return (
      <div className="p-3 rounded-lg bg-slate-800/30 border border-slate-700">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-slate-300">Constitutional AI</span>
          {getPassIcon()}
        </div>
        <div className="flex items-baseline gap-2">
          <span className={`text-2xl font-bold ${getScoreColor(data.overall_score)}`}>
            {data.overall_score.toFixed(1)}
          </span>
          <span className="text-sm text-slate-500">/10</span>
        </div>
        <p className="text-xs text-slate-400 mt-2 line-clamp-2">{data.summary}</p>
      </div>
    );
  }

  // Full detailed view
  return (
    <div className="p-6 rounded-xl bg-slate-800/50 border border-slate-700">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-purple-600/20 flex items-center justify-center">
            <Info className="w-5 h-5 text-purple-400" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">Constitutional Alignment</h3>
            <p className="text-sm text-slate-400">Ethical AI Evaluation</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {getPassIcon()}
          <div className="text-right">
            <div className={`text-3xl font-bold ${getScoreColor(data.overall_score)}`}>
              {data.overall_score.toFixed(1)}
            </div>
            <div className="text-sm text-slate-500">Overall Score</div>
          </div>
        </div>
      </div>

      {/* Summary */}
      <div className="mb-6 p-4 rounded-lg bg-slate-900/50 border border-slate-700">
        <p className="text-slate-300">{data.summary}</p>
      </div>

      {/* Principle Scores */}
      <div className="space-y-4">
        <h4 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">
          Principle Breakdown
        </h4>
        {data.principle_scores.map((principle) => (
          <div key={principle.principle_name} className="space-y-2">
            {/* Principle Name and Score */}
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-white capitalize">
                {principle.principle_name.replace('_', ' ')}
              </span>
              <span className={`text-sm font-semibold ${getScoreColor(principle.score)}`}>
                {principle.score.toFixed(1)}/10
              </span>
            </div>

            {/* Progress Bar */}
            <div className="w-full bg-slate-700 rounded-full h-2">
              <div
                className={`h-2 rounded-full ${getScoreBarColor(principle.score)} transition-all duration-500`}
                style={{ width: `${(principle.score / 10) * 100}%` }}
              />
            </div>

            {/* Explanation */}
            <p className="text-xs text-slate-400">{principle.explanation}</p>

            {/* Violations */}
            {principle.violations.length > 0 && (
              <div className="mt-2 p-3 rounded-lg bg-red-500/10 border border-red-500/30">
                <div className="flex items-start gap-2">
                  <AlertCircle className="w-4 h-4 text-red-400 mt-0.5 flex-shrink-0" />
                  <div className="flex-1">
                    <p className="text-xs font-semibold text-red-400 mb-1">Violations Detected:</p>
                    <ul className="text-xs text-red-300 space-y-1">
                      {principle.violations.map((violation, idx) => (
                        <li key={idx}>• {violation}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Footer Info */}
      <div className="mt-6 pt-4 border-t border-slate-700">
        <p className="text-xs text-slate-500 text-center">
          Evaluated using Constitutional AI framework • Judge: Claude 3.5 Sonnet
        </p>
      </div>
    </div>
  );
}
