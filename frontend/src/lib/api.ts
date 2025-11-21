/**
 * API client for Model Eval Studio backend
 */
import axios from 'axios';
import type {
  EvaluationRun,
  EvaluationResults,
  AvailableModels,
  ModelConfig,
  QuickEvalResult,
} from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  /**
   * Health check
   */
  async healthCheck() {
    const { data } = await apiClient.get('/');
    return data;
  },

  /**
   * Get available models from all providers
   */
  async getAvailableModels(): Promise<AvailableModels> {
    const { data } = await apiClient.get<AvailableModels>('/api/models');
    return data;
  },

  /**
   * Create a new evaluation run
   */
  async createEvaluation(params: {
    name: string;
    description?: string;
    prompts: string[];
    models: ModelConfig[];
    temperature?: number;
    max_tokens?: number;
    include_constitutional?: boolean;
  }): Promise<EvaluationRun> {
    const { data } = await apiClient.post<EvaluationRun>('/api/evaluations', params);
    return data;
  },

  /**
   * List all evaluation runs
   */
  async listEvaluations(skip = 0, limit = 20): Promise<EvaluationRun[]> {
    const { data } = await apiClient.get<EvaluationRun[]>('/api/evaluations', {
      params: { skip, limit },
    });
    return data;
  },

  /**
   * Get detailed results for a specific evaluation
   */
  async getEvaluation(id: number): Promise<EvaluationResults> {
    const { data } = await apiClient.get<EvaluationResults>(`/api/evaluations/${id}`);
    return data;
  },

  /**
   * Delete an evaluation run
   */
  async deleteEvaluation(id: number): Promise<void> {
    await apiClient.delete(`/api/evaluations/${id}`);
  },

  /**
   * Quick one-off evaluation (not saved to database)
   */
  async quickEvaluation(params: {
    prompt: string;
    models: ModelConfig[];
    temperature?: number;
    max_tokens?: number;
  }): Promise<{ prompt: string; results: QuickEvalResult[] }> {
    const { data } = await apiClient.post('/api/quick-eval', params);
    return data;
  },

  /**
   * Get cost breakdown for an evaluation
   */
  async getCostBreakdown(evaluationId: number): Promise<any> {
    const { data } = await apiClient.get(`/api/cost/evaluation/${evaluationId}`);
    return data;
  },

  /**
   * Get cost comparison for an evaluation
   */
  async getCostComparison(evaluationId: number): Promise<any> {
    const { data } = await apiClient.get(`/api/cost/evaluation/${evaluationId}/comparison`);
    return data;
  },

  /**
   * Get current pricing information
   */
  async getPricing(): Promise<any> {
    const { data } = await apiClient.get('/api/cost/pricing');
    return data;
  },
};
