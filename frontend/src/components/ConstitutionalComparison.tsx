/**
 * Side-by-side Constitutional AI comparison
 * Compares multiple models' constitutional scores
 */
import { ModelResponse } from '@/types';
import { Trophy, Award, Medal } from 'lucide-react';

interface ConstitutionalComparisonProps {
  responses: ModelResponse[];
}

export default function ConstitutionalComparison({ responses }: ConstitutionalComparisonProps) {
  // Filter responses with constitutional data
  const responsesWithConstitutional = responses.filter(
    (r) => r.constitutional_data && !r.error_message
  );

  if (responsesWithConstitutional.length === 0) {
    return null;
  }

  // Sort by constitutional score (highest first)
  const sorted = [...responsesWithConstitutional].sort(
    (a, b) => (b.constitutional_score || 0) - (a.constitutional_score || 0)
  );

  const getRankIcon = (index: number) => {
    if (index === 0) return <Trophy className="w-5 h-5 text-yellow-400" />;
    if (index === 1) return <Award className="w-5 h-5 text-slate-300" />;
    if (index === 2) return <Medal className="w-5 h-5 text-orange-400" />;
    return null;
  };

  const getScoreColor = (score: number) => {
    if (score >= 9) return 'text-green-400';
    if (score >= 7) return 'text-blue-400';
    if (score >= 5) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getBorderColor = (index: number) => {
    if (index === 0) return 'border-yellow-500/50';
    if (index === 1) return 'border-slate-500/50';
    if (index === 2) return 'border-orange-500/50';
    return 'border-slate-700';
  };

  return (
    <div className="p-6 rounded-xl bg-slate-800/50 border border-slate-700">
      <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
        <Trophy className="w-5 h-5 text-purple-400" />
        Constitutional AI Rankings
      </h3>

      <div className="space-y-3">
        {sorted.map((response, index) => {
          const data = response.constitutional_data!;

          return (
            <div
              key={response.id}
              className={`p-4 rounded-lg bg-slate-900/50 border-2 ${getBorderColor(index)} transition-all hover:bg-slate-900/70`}
            >
              <div className="flex items-center justify-between">
                {/* Model Info */}
                <div className="flex items-center gap-3">
                  {getRankIcon(index)}
                  <div>
                    <div className="font-semibold text-white">
                      {response.provider} / {response.model_name}
                    </div>
                    <div className="text-xs text-slate-400">
                      {data.passed ? '✅ Passed' : '❌ Failed'} • {data.summary.split('.')[0]}
                    </div>
                  </div>
                </div>

                {/* Score */}
                <div className="text-right">
                  <div className={`text-2xl font-bold ${getScoreColor(data.overall_score)}`}>
                    {data.overall_score.toFixed(1)}
                  </div>
                  <div className="text-xs text-slate-500">
                    {index === 0 ? 'Highest' : `Rank #${index + 1}`}
                  </div>
                </div>
              </div>

              {/* Mini principle scores */}
              <div className="mt-3 grid grid-cols-5 gap-2">
                {data.principle_scores.map((ps) => (
                  <div key={ps.principle_name} className="text-center">
                    <div className={`text-xs font-semibold ${getScoreColor(ps.score)}`}>
                      {ps.score.toFixed(1)}
                    </div>
                    <div className="text-[10px] text-slate-500 capitalize truncate">
                      {ps.principle_name.replace('_', ' ')}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      {/* Summary Stats */}
      <div className="mt-4 p-3 rounded-lg bg-purple-600/10 border border-purple-600/30">
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-xl font-bold text-purple-400">
              {sorted[0].constitutional_score?.toFixed(1)}
            </div>
            <div className="text-xs text-slate-400">Best Score</div>
          </div>
          <div>
            <div className="text-xl font-bold text-purple-400">
              {(sorted.reduce((sum, r) => sum + (r.constitutional_score || 0), 0) / sorted.length).toFixed(1)}
            </div>
            <div className="text-xs text-slate-400">Average</div>
          </div>
          <div>
            <div className="text-xl font-bold text-purple-400">
              {sorted.filter((r) => r.constitutional_passed).length}/{sorted.length}
            </div>
            <div className="text-xs text-slate-400">Passed</div>
          </div>
        </div>
      </div>
    </div>
  );
}
