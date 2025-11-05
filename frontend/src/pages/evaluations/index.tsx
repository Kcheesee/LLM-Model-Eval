/**
 * Evaluations history page
 */
import { useState, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { ArrowLeft, Trash2, ExternalLink } from 'lucide-react';
import { api } from '@/lib/api';
import type { EvaluationRun } from '@/types';

export default function EvaluationsHistory() {
  const [evaluations, setEvaluations] = useState<EvaluationRun[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadEvaluations();
  }, []);

  const loadEvaluations = async () => {
    try {
      const data = await api.listEvaluations();
      setEvaluations(data);
    } catch (error) {
      console.error('Failed to load evaluations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this evaluation?')) return;

    try {
      await api.deleteEvaluation(id);
      setEvaluations(evaluations.filter((e) => e.id !== id));
    } catch (error) {
      console.error('Failed to delete evaluation:', error);
      alert('Failed to delete evaluation');
    }
  };

  return (
    <>
      <Head>
        <title>Evaluation History - Model Eval Studio</title>
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
        <header className="border-b border-slate-700 bg-slate-900/50 backdrop-blur">
          <div className="container mx-auto px-6 py-4">
            <div className="flex items-center gap-4">
              <Link href="/" className="text-slate-400 hover:text-white transition">
                <ArrowLeft className="w-6 h-6" />
              </Link>
              <h1 className="text-2xl font-bold text-white">Evaluation History</h1>
            </div>
          </div>
        </header>

        <main className="container mx-auto px-6 py-12 max-w-6xl">
          {loading ? (
            <div className="text-center py-12">
              <p className="text-slate-400">Loading evaluations...</p>
            </div>
          ) : evaluations.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-slate-400 mb-4">No evaluations yet</p>
              <Link
                href="/new-evaluation"
                className="inline-block px-6 py-3 rounded-lg bg-primary-600 hover:bg-primary-700 text-white font-semibold transition"
              >
                Create Your First Evaluation
              </Link>
            </div>
          ) : (
            <div className="space-y-4">
              {evaluations.map((evaluation) => (
                <div
                  key={evaluation.id}
                  className="p-6 rounded-xl bg-slate-800/50 border border-slate-700 hover:bg-slate-800 transition"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <Link href={`/evaluations/${evaluation.id}`}>
                        <h3 className="text-lg font-semibold text-white mb-1 hover:text-primary-400 transition">
                          {evaluation.name}
                        </h3>
                      </Link>
                      {evaluation.description && (
                        <p className="text-slate-400 text-sm mb-2">{evaluation.description}</p>
                      )}
                      <div className="flex items-center gap-4 text-sm text-slate-500">
                        <span>{new Date(evaluation.created_at).toLocaleString()}</span>
                        {evaluation.completed_at && (
                          <span>
                            Completed {new Date(evaluation.completed_at).toLocaleString()}
                          </span>
                        )}
                      </div>
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
                      <Link
                        href={`/evaluations/${evaluation.id}`}
                        className="p-2 rounded-lg hover:bg-slate-700 text-slate-400 hover:text-white transition"
                      >
                        <ExternalLink className="w-5 h-5" />
                      </Link>
                      <button
                        onClick={() => handleDelete(evaluation.id)}
                        className="p-2 rounded-lg hover:bg-red-500/20 text-slate-400 hover:text-red-400 transition"
                      >
                        <Trash2 className="w-5 h-5" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </main>
      </div>
    </>
  );
}
