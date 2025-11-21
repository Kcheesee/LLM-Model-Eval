/**
 * New Evaluation Creation Page
 */
import { useState, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { ArrowLeft, Plus, X, Play, Save } from 'lucide-react';
import { api } from '@/lib/api';
import type { ModelConfig } from '@/types';

export default function NewEvaluation() {
    const router = useRouter();
    const [loading, setLoading] = useState(false);
    const [availableModels, setAvailableModels] = useState<any>(null);

    // Form state
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');
    const [prompts, setPrompts] = useState<string[]>(['']);
    const [selectedModels, setSelectedModels] = useState<ModelConfig[]>([]);
    const [temperature, setTemperature] = useState(0.7);
    const [maxTokens, setMaxTokens] = useState(1000);
    const [includeConstitutional, setIncludeConstitutional] = useState(false);

    // Load available models on mount
    useEffect(() => {
        loadAvailableModels();
    }, []);

    const loadAvailableModels = async () => {
        try {
            const models = await api.getAvailableModels();
            setAvailableModels(models);
        } catch (error) {
            console.error('Failed to load models:', error);
        }
    };

    const addPrompt = () => {
        setPrompts([...prompts, '']);
    };

    const removePrompt = (index: number) => {
        if (prompts.length > 1) {
            setPrompts(prompts.filter((_, i) => i !== index));
        }
    };

    const updatePrompt = (index: number, value: string) => {
        const newPrompts = [...prompts];
        newPrompts[index] = value;
        setPrompts(newPrompts);
    };

    const toggleModel = (provider: string, model: string) => {
        const exists = selectedModels.some(
            (m) => m.provider === provider && m.model === model
        );

        if (exists) {
            setSelectedModels(
                selectedModels.filter(
                    (m) => !(m.provider === provider && m.model === model)
                )
            );
        } else {
            setSelectedModels([...selectedModels, { provider, model }]);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);

        try {
            const evaluation = await api.createEvaluation({
                name,
                description,
                prompts: prompts.filter(p => p.trim()),
                models: selectedModels,
                temperature,
                max_tokens: maxTokens,
                include_constitutional: includeConstitutional,
            });

            router.push(`/evaluations/${evaluation.id}`);
        } catch (error: any) {
            console.error('Failed to create evaluation:', error);
            alert(error.response?.data?.detail || 'Failed to create evaluation');
            setLoading(false);
        }
    };

    const isValid = name.trim() && prompts.some(p => p.trim()) && selectedModels.length > 0;

    return (
        <>
            <Head>
                <title>New Evaluation - Model Eval Studio</title>
            </Head>

            <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
                {/* Header */}
                <header className="border-b border-slate-700 bg-slate-900/50 backdrop-blur">
                    <div className="container mx-auto px-6 py-4">
                        <div className="flex items-center gap-4">
                            <Link
                                href="/"
                                className="flex items-center gap-2 text-slate-400 hover:text-white transition"
                            >
                                <ArrowLeft className="w-5 h-5" />
                                Back
                            </Link>
                            <h1 className="text-2xl font-bold text-white">
                                New Evaluation
                            </h1>
                        </div>
                    </div>
                </header>

                {/* Main Content */}
                <main className="container mx-auto px-6 py-8 max-w-4xl">
                    <form onSubmit={handleSubmit} className="space-y-8">
                        {/* Basic Info */}
                        <div className="p-6 rounded-xl bg-slate-800/50 border border-slate-700">
                            <h2 className="text-xl font-semibold text-white mb-4">
                                Basic Information
                            </h2>

                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-slate-300 mb-2">
                                        Evaluation Name *
                                    </label>
                                    <input
                                        type="text"
                                        value={name}
                                        onChange={(e) => setName(e.target.value)}
                                        placeholder="e.g., Customer Support Responses"
                                        className="w-full px-4 py-2 rounded-lg bg-slate-900 border border-slate-700 text-white placeholder-slate-500 focus:border-primary-500 focus:outline-none"
                                        required
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-slate-300 mb-2">
                                        Description (Optional)
                                    </label>
                                    <textarea
                                        value={description}
                                        onChange={(e) => setDescription(e.target.value)}
                                        placeholder="Describe what you're evaluating..."
                                        rows={3}
                                        className="w-full px-4 py-2 rounded-lg bg-slate-900 border border-slate-700 text-white placeholder-slate-500 focus:border-primary-500 focus:outline-none resize-none"
                                    />
                                </div>
                            </div>
                        </div>

                        {/* Prompts */}
                        <div className="p-6 rounded-xl bg-slate-800/50 border border-slate-700">
                            <div className="flex items-center justify-between mb-4">
                                <h2 className="text-xl font-semibold text-white">
                                    Test Prompts *
                                </h2>
                                <button
                                    type="button"
                                    onClick={addPrompt}
                                    className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-primary-600 hover:bg-primary-700 text-white text-sm transition"
                                >
                                    <Plus className="w-4 h-4" />
                                    Add Prompt
                                </button>
                            </div>

                            <div className="space-y-3">
                                {prompts.map((prompt, index) => (
                                    <div key={index} className="flex gap-2">
                                        <textarea
                                            value={prompt}
                                            onChange={(e) => updatePrompt(index, e.target.value)}
                                            placeholder={`Prompt ${index + 1}`}
                                            rows={2}
                                            className="flex-1 px-4 py-2 rounded-lg bg-slate-900 border border-slate-700 text-white placeholder-slate-500 focus:border-primary-500 focus:outline-none resize-none"
                                            required
                                        />
                                        {prompts.length > 1 && (
                                            <button
                                                type="button"
                                                onClick={() => removePrompt(index)}
                                                className="px-3 text-slate-400 hover:text-red-400 transition"
                                            >
                                                <X className="w-5 h-5" />
                                            </button>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Model Selection */}
                        <div className="p-6 rounded-xl bg-slate-800/50 border border-slate-700">
                            <h2 className="text-xl font-semibold text-white mb-4">
                                Select Models * ({selectedModels.length} selected)
                            </h2>

                            {availableModels && (
                                <div className="space-y-4">
                                    {Object.entries(availableModels.providers || {}).map(([provider, models]: [string, any]) => (
                                        <div key={provider}>
                                            <h3 className="text-sm font-medium text-slate-400 mb-2 capitalize">
                                                {provider}
                                            </h3>
                                            <div className="grid grid-cols-2 gap-2">
                                                {models.map((model: string) => {
                                                    const isSelected = selectedModels.some(
                                                        (m) => m.provider === provider && m.model === model
                                                    );
                                                    return (
                                                        <button
                                                            key={model}
                                                            type="button"
                                                            onClick={() => toggleModel(provider, model)}
                                                            className={`px-4 py-2 rounded-lg text-sm font-medium transition ${isSelected
                                                                ? 'bg-primary-600 text-white border-2 border-primary-500'
                                                                : 'bg-slate-900 text-slate-300 border border-slate-700 hover:border-slate-600'
                                                                }`}
                                                        >
                                                            {model}
                                                        </button>
                                                    );
                                                })}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>

                        {/* Advanced Settings */}
                        <div className="p-6 rounded-xl bg-slate-800/50 border border-slate-700">
                            <h2 className="text-xl font-semibold text-white mb-4">
                                Advanced Settings
                            </h2>

                            <div className="grid md:grid-cols-2 gap-4">
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
                                    <div className="flex justify-between text-xs text-slate-500 mt-1">
                                        <span>Focused</span>
                                        <span>Creative</span>
                                    </div>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-slate-300 mb-2">
                                        Max Tokens: {maxTokens}
                                    </label>
                                    <input
                                        type="range"
                                        min="100"
                                        max="4000"
                                        step="100"
                                        value={maxTokens}
                                        onChange={(e) => setMaxTokens(parseInt(e.target.value))}
                                        className="w-full"
                                    />
                                    <div className="flex justify-between text-xs text-slate-500 mt-1">
                                        <span>100</span>
                                        <span>4000</span>
                                    </div>
                                </div>
                            </div>

                            <div className="mt-4">
                                <label className="flex items-center gap-2 cursor-pointer">
                                    <input
                                        type="checkbox"
                                        checked={includeConstitutional}
                                        onChange={(e) => setIncludeConstitutional(e.target.checked)}
                                        className="w-4 h-4 rounded border-slate-700 bg-slate-900 text-primary-600 focus:ring-primary-500"
                                    />
                                    <span className="text-sm text-slate-300">
                                        Include Constitutional AI evaluation (ethics & safety scoring)
                                    </span>
                                </label>
                            </div>
                        </div>

                        {/* Submit */}
                        <div className="flex gap-4">
                            <button
                                type="submit"
                                disabled={!isValid || loading}
                                className="flex-1 flex items-center justify-center gap-2 px-6 py-3 rounded-lg bg-primary-600 hover:bg-primary-700 disabled:bg-slate-700 disabled:text-slate-500 text-white font-semibold transition"
                            >
                                {loading ? (
                                    <>
                                        <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                        Creating...
                                    </>
                                ) : (
                                    <>
                                        <Play className="w-5 h-5" />
                                        Run Evaluation
                                    </>
                                )}
                            </button>
                        </div>
                    </form>
                </main>
            </div>
        </>
    );
}
