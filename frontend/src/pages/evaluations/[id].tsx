/**
 * Individual evaluation results page with side-by-side comparison
 */
import { useState, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { ArrowLeft, Clock, DollarSign, Hash, AlertCircle } from 'lucide-react';
import { api } from '@/lib/api';
import type { EvaluationResults, TestCase } from '@/types';

export default function EvaluationDetail() {
  const router = useRouter();
  const { id } = router.query;
  const [data, setData] = useState<EvaluationResults | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedTestCase, setSelectedTestCase] = useState<number>(0);

  useEffect(() => {
    if (id) {
      loadEvaluation(parseInt(id as string));
    }
  }, [id]);

  const loadEvaluation = async (evaluationId: number) => {
    try {
      const results = await api.getEvaluation(evaluationId);
      setData(results);
    } catch (error) {
      console.error('Failed to load evaluation:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
        <p className="text-slate-400">Loading evaluation...</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <p className="text-slate-400 mb-4">Evaluation not found</p>
          <Link href="/evaluations" className="text-primary-400 hover:text-primary-300">
            Back to History
          </Link>
        </div>
      </div>
    );
  }

  const currentTestCase = data.test_cases[selectedTestCase];

  return (
    <>
      <Head>
        <title>{data.evaluation_run.name} - Model Eval Studio</title>
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
        {/* Header */}
        <header className="border-b border-slate-700 bg-slate-900/50 backdrop-blur">
          <div className="container mx-auto px-6 py-4">
            <div className="flex items-center gap-4">
              <Link href="/evaluations" className="text-slate-400 hover:text-white transition">
                <ArrowLeft className="w-6 h-6" />
              </Link>
              <div>
                <h1 className="text-2xl font-bold text-white">{data.evaluation_run.name}</h1>
                {data.evaluation_run.description && (
                  <p className="text-slate-400 text-sm">{data.evaluation_run.description}</p>
                )}
              </div>
            </div>
          </div>
        </header>

        <main className="container mx-auto px-6 py-12 max-w-7xl">
          {/* Summary Statistics */}
          <div className="grid md:grid-cols-4 gap-4 mb-8">
            {data.summary.model_statistics.map((stats) => (
              <div
                key={`${stats.provider}-${stats.model}`}
                className="p-4 rounded-xl bg-slate-800/50 border border-slate-700"
              >
                <h3 className="text-sm font-medium text-slate-400 mb-2">
                  {stats.provider} / {stats.model}
                </h3>
                <div className="space-y-1 text-sm">
                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-slate-500" />
                    <span className="text-white">{stats.avg_response_time_ms.toFixed(0)}ms</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Hash className="w-4 h-4 text-slate-500" />
                    <span className="text-white">{stats.total_tokens} tokens</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <DollarSign className="w-4 h-4 text-slate-500" />
                    <span className="text-white">${stats.total_cost.toFixed(6)}</span>
                  </div>
                  {stats.failed_requests > 0 && (
                    <div className="flex items-center gap-2">
                      <AlertCircle className="w-4 h-4 text-red-500" />
                      <span className="text-red-400">{stats.failed_requests} failed</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Test Case Selector */}
          {data.test_cases.length > 1 && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-white mb-3">Test Cases</h3>
              <div className="flex gap-2 flex-wrap">
                {data.test_cases.map((testCase, index) => (
                  <button
                    key={testCase.id}
                    onClick={() => setSelectedTestCase(index)}
                    className={`px-4 py-2 rounded-lg font-medium transition ${
                      selectedTestCase === index
                        ? 'bg-primary-600 text-white'
                        : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                    }`}
                  >
                    Test Case {index + 1}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Prompt Display */}
          <div className="mb-6 p-6 rounded-xl bg-slate-800/50 border border-slate-700">
            <h3 className="text-lg font-semibold text-white mb-3">Prompt</h3>
            <p className="text-slate-300 whitespace-pre-wrap">{currentTestCase.prompt}</p>
          </div>

          {/* Side-by-Side Responses */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-4">Model Responses</h3>
            <div className="grid lg:grid-cols-2 gap-6">
              {currentTestCase.responses.map((response) => (
                <div
                  key={response.id}
                  className="p-6 rounded-xl bg-slate-800/50 border border-slate-700"
                >
                  <div className="mb-4">
                    <h4 className="text-lg font-semibold text-white mb-2">
                      {response.provider} / {response.model_name}
                    </h4>
                    <div className="flex flex-wrap gap-4 text-sm">
                      <span className="text-slate-400">
                        {response.response_time_ms.toFixed(0)}ms
                      </span>
                      {response.total_tokens && (
                        <span className="text-slate-400">{response.total_tokens} tokens</span>
                      )}
                      {response.estimated_cost && (
                        <span className="text-green-400">
                          ${response.estimated_cost.toFixed(6)}
                        </span>
                      )}
                    </div>
                  </div>

                  {response.error_message ? (
                    <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/30">
                      <p className="text-red-400">{response.error_message}</p>
                    </div>
                  ) : (
                    <div className="prose prose-invert max-w-none">
                      <p className="text-slate-300 whitespace-pre-wrap">
                        {response.response_text}
                      </p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </main>
      </div>
    </>
  );
}
