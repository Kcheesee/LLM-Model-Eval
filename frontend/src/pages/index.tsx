/**
 * Main dashboard page
 */
import { useState, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { Play, History, Zap, TrendingUp } from 'lucide-react';
import { api } from '@/lib/api';
import type { EvaluationRun } from '@/types';

export default function Home() {
  const [recentEvaluations, setRecentEvaluations] = useState<EvaluationRun[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRecentEvaluations();
  }, []);

  const loadRecentEvaluations = async () => {
    try {
      const evaluations = await api.listEvaluations(0, 5);
      setRecentEvaluations(evaluations);
    } catch (error) {
      console.error('Failed to load evaluations:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Head>
        <title>Model Eval Studio - AI Evaluation Platform</title>
        <meta name="description" content="Compare and evaluate LLM performance" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
        {/* Header */}
        <header className="border-b border-slate-700 bg-slate-900/50 backdrop-blur">
          <div className="container mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <h1 className="text-2xl font-bold text-white">
                Model Eval Studio
              </h1>
              <nav className="flex gap-4">
                <Link
                  href="/quick-eval"
                  className="px-4 py-2 rounded-lg bg-primary-600 hover:bg-primary-700 text-white transition"
                >
                  Quick Eval
                </Link>
                <Link
                  href="/evaluations"
                  className="px-4 py-2 rounded-lg border border-slate-600 hover:bg-slate-800 text-white transition"
                >
                  History
                </Link>
              </nav>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="container mx-auto px-6 py-12">
          {/* Hero Section */}
          <div className="text-center mb-16">
            <h2 className="text-5xl font-bold text-white mb-4">
              Compare LLMs with Confidence
            </h2>
            <p className="text-xl text-slate-300 mb-8 max-w-2xl mx-auto">
              Evaluate and compare AI models side-by-side on your specific use cases.
              Make informed decisions before committing to a provider.
            </p>
            <div className="flex gap-4 justify-center">
              <Link
                href="/new-evaluation"
                className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-primary-600 hover:bg-primary-700 text-white font-semibold transition"
              >
                <Play className="w-5 h-5" />
                Start New Evaluation
              </Link>
              <Link
                href="/quick-eval"
                className="inline-flex items-center gap-2 px-6 py-3 rounded-lg border-2 border-primary-600 hover:bg-primary-600/10 text-white font-semibold transition"
              >
                <Zap className="w-5 h-5" />
                Quick Compare
              </Link>
            </div>
          </div>

          {/* Features Grid */}
          <div className="grid md:grid-cols-3 gap-6 mb-16">
            <div className="p-6 rounded-xl bg-slate-800/50 border border-slate-700">
              <div className="w-12 h-12 rounded-lg bg-primary-600/20 flex items-center justify-center mb-4">
                <TrendingUp className="w-6 h-6 text-primary-400" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">
                Side-by-Side Comparison
              </h3>
              <p className="text-slate-400">
                Compare Claude, GPT-4, and Gemini responses in real-time with detailed metrics.
              </p>
            </div>

            <div className="p-6 rounded-xl bg-slate-800/50 border border-slate-700">
              <div className="w-12 h-12 rounded-lg bg-primary-600/20 flex items-center justify-center mb-4">
                <Zap className="w-6 h-6 text-primary-400" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">
                Performance Metrics
              </h3>
              <p className="text-slate-400">
                Track response time, token usage, and cost per request across all models.
              </p>
            </div>

            <div className="p-6 rounded-xl bg-slate-800/50 border border-slate-700">
              <div className="w-12 h-12 rounded-lg bg-primary-600/20 flex items-center justify-center mb-4">
                <History className="w-6 h-6 text-primary-400" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">
                Evaluation History
              </h3>
              <p className="text-slate-400">
                Save and review past evaluations to inform future decisions.
              </p>
            </div>
          </div>

          {/* Recent Evaluations */}
          {!loading && recentEvaluations.length > 0 && (
            <div>
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-2xl font-bold text-white">Recent Evaluations</h3>
                <Link
                  href="/evaluations"
                  className="text-primary-400 hover:text-primary-300 transition"
                >
                  View all →
                </Link>
              </div>

              <div className="grid gap-4">
                {recentEvaluations.map((evaluation) => (
                  <Link
                    key={evaluation.id}
                    href={`/evaluations/${evaluation.id}`}
                    className="block p-6 rounded-xl bg-slate-800/50 border border-slate-700 hover:bg-slate-800 transition"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="text-lg font-semibold text-white mb-1">
                          {evaluation.name}
                        </h4>
                        {evaluation.description && (
                          <p className="text-slate-400 text-sm">{evaluation.description}</p>
                        )}
                      </div>
                      <div className="flex items-center gap-3">
                        <span
                          className={`px-3 py-1 rounded-full text-sm font-medium ${
                            evaluation.status === 'completed'
                              ? 'bg-green-500/20 text-green-400'
                              : evaluation.status === 'running'
                              ? 'bg-blue-500/20 text-blue-400'
                              : evaluation.status === 'failed'
                              ? 'bg-red-500/20 text-red-400'
                              : 'bg-slate-500/20 text-slate-400'
                          }`}
                        >
                          {evaluation.status}
                        </span>
                        <span className="text-slate-500 text-sm">
                          {new Date(evaluation.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          )}
        </main>

        {/* Footer */}
        <footer className="border-t border-slate-700 mt-16">
          <div className="container mx-auto px-6 py-8">
            <p className="text-center text-slate-500">
              Model Eval Studio · Built with FastAPI + Next.js
            </p>
          </div>
        </footer>
      </div>
    </>
  );
}
