/**
 * Quick Evaluation page - fast one-off model comparisons
 */
import { useState, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { ArrowLeft, Play, Loader2 } from 'lucide-react';
import { api } from '@/lib/api';
import type { AvailableModels, ModelConfig, QuickEvalResult } from '@/types';

export default function QuickEval() {
  const [availableModels, setAvailableModels] = useState<AvailableModels | null>(null);
  const [prompt, setPrompt] = useState('');
  const [selectedModels, setSelectedModels] = useState<ModelConfig[]>([]);
  const [temperature, setTemperature] = useState(0.7);
  const [maxTokens, setMaxTokens] = useState(1000);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<QuickEvalResult[] | null>(null);

  useEffect(() => {
    loadAvailableModels();
  }, []);

  const loadAvailableModels = async () => {
    try {
      const models = await api.getAvailableModels();
      setAvailableModels(models);

      // Pre-select some default models
      const defaults: ModelConfig[] = [];
      if (models.providers.anthropic?.length > 0) {
        defaults.push({ provider: 'anthropic', model: models.providers.anthropic[0] });
      }
      if (models.providers.openai?.length > 0) {
        defaults.push({ provider: 'openai', model: models.providers.openai[0] });
      }
      setSelectedModels(defaults);
    } catch (error) {
      console.error('Failed to load models:', error);
    }
  };

  const handleRunEvaluation = async () => {
    if (!prompt.trim() || selectedModels.length === 0) return;

    setLoading(true);
    setResults(null);

    try {
      const response = await api.quickEvaluation({
        prompt,
        models: selectedModels,
        temperature,
        max_tokens: maxTokens,
      });
      setResults(response.results);
    } catch (error) {
      console.error('Evaluation failed:', error);
      alert('Evaluation failed. Check console for details.');
    } finally {
      setLoading(false);
    }
  };

  const toggleModel = (provider: string, model: string) => {
    const exists = selectedModels.some(
      (m) => m.provider === provider && m.model === model
    );

    if (exists) {
      setSelectedModels(selectedModels.filter(
        (m) => !(m.provider === provider && m.model === model)
      ));
    } else {
      setSelectedModels([...selectedModels, { provider, model }]);
    }
  };

  return (
    <>
      <Head>
        <title>Quick Eval - Model Eval Studio</title>
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
        {/* Header */}
        <header className="border-b border-slate-700 bg-slate-900/50 backdrop-blur">
          <div className="container mx-auto px-6 py-4">
            <div className="flex items-center gap-4">
              <Link href="/" className="text-slate-400 hover:text-white transition">
                <ArrowLeft className="w-6 h-6" />
              </Link>
              <h1 className="text-2xl font-bold text-white">Quick Evaluation</h1>
            </div>
          </div>
        </header>

        <main className="container mx-auto px-6 py-12 max-w-7xl">
          <div className="grid lg:grid-cols-3 gap-8">
            {/* Configuration Panel */}
            <div className="lg:col-span-1 space-y-6">
              {/* Model Selection */}
              <div className="p-6 rounded-xl bg-slate-800/50 border border-slate-700">
                <h3 className="text-lg font-semibold text-white mb-4">Select Models</h3>
                {availableModels && (
                  <div className="space-y-4">
                    {Object.entries(availableModels.providers).map(([provider, models]) => (
                      <div key={provider}>
                        <h4 className="text-sm font-medium text-slate-400 mb-2 capitalize">
                          {provider}
                        </h4>
                        <div className="space-y-2">
                          {models.map((model) => (
                            <label
                              key={`${provider}-${model}`}
                              className="flex items-center gap-2 cursor-pointer"
                            >
                              <input
                                type="checkbox"
                                checked={selectedModels.some(
                                  (m) => m.provider === provider && m.model === model
                                )}
                                onChange={() => toggleModel(provider, model)}
                                className="rounded border-slate-600 bg-slate-700 text-primary-600 focus:ring-primary-600"
                              />
                              <span className="text-sm text-slate-300">{model}</span>
                            </label>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Parameters */}
              <div className="p-6 rounded-xl bg-slate-800/50 border border-slate-700">
                <h3 className="text-lg font-semibold text-white mb-4">Parameters</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Temperature: {temperature}
                    </label>
                    <input
                      type="range"
                      min="0"
                      max="2"
                      step="0.1"
                      value={temperature}
                      onChange={(e) => setTemperature(parseFloat(e.target.value))}
                      className="w-full"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Max Tokens
                    </label>
                    <input
                      type="number"
                      value={maxTokens}
                      onChange={(e) => setMaxTokens(parseInt(e.target.value))}
                      className="w-full px-3 py-2 rounded-lg bg-slate-700 border border-slate-600 text-white focus:outline-none focus:ring-2 focus:ring-primary-600"
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Main Content */}
            <div className="lg:col-span-2 space-y-6">
              {/* Prompt Input */}
              <div className="p-6 rounded-xl bg-slate-800/50 border border-slate-700">
                <h3 className="text-lg font-semibold text-white mb-4">Test Prompt</h3>
                <textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="Enter your prompt here..."
                  className="w-full h-40 px-4 py-3 rounded-lg bg-slate-700 border border-slate-600 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary-600 resize-none"
                />
                <div className="mt-4 flex justify-end">
                  <button
                    onClick={handleRunEvaluation}
                    disabled={!prompt.trim() || selectedModels.length === 0 || loading}
                    className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-primary-600 hover:bg-primary-700 text-white font-semibold transition disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="w-5 h-5 animate-spin" />
                        Running...
                      </>
                    ) : (
                      <>
                        <Play className="w-5 h-5" />
                        Run Evaluation
                      </>
                    )}
                  </button>
                </div>
              </div>

              {/* Results */}
              {results && (
                <div className="space-y-4">
                  <h3 className="text-2xl font-bold text-white">Results</h3>
                  <div className="grid gap-4">
                    {results.map((result, index) => (
                      <div
                        key={index}
                        className="p-6 rounded-xl bg-slate-800/50 border border-slate-700"
                      >
                        <div className="flex items-center justify-between mb-4">
                          <h4 className="text-lg font-semibold text-white">
                            {result.provider} / {result.model}
                          </h4>
                          {!result.error && (
                            <div className="flex gap-4 text-sm">
                              <span className="text-slate-400">
                                {result.response_time_ms?.toFixed(0)}ms
                              </span>
                              <span className="text-slate-400">
                                {result.tokens} tokens
                              </span>
                              <span className="text-green-400">
                                ${result.cost?.toFixed(6)}
                              </span>
                            </div>
                          )}
                        </div>
                        {result.error ? (
                          <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/30">
                            <p className="text-red-400">{result.error}</p>
                          </div>
                        ) : (
                          <div className="prose prose-invert max-w-none">
                            <p className="text-slate-300 whitespace-pre-wrap">{result.text}</p>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </main>
      </div>
    </>
  );
}
