/**
 * TypeScript type definitions for Model Eval Studio
 */

export interface ModelConfig {
  provider: string;
  model: string;
}

export interface EvaluationRun {
  id: number;
  name: string;
  description?: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  created_at: string;
  completed_at?: string;
}

export interface TestCase {
  id: number;
  prompt: string;
  order_index: number;
  responses: ModelResponse[];
}

export interface ConstitutionalScore {
  principle_name: string;
  score: number;
  explanation: string;
  violations: string[];
}

export interface ConstitutionalEvaluation {
  overall_score: number;
  passed: boolean;
  summary: string;
  principle_scores: ConstitutionalScore[];
}

export interface ModelResponse {
  id: number;
  test_case_id: number;
  model_name: string;
  provider: string;
  response_text: string;
  response_time_ms: number;
  input_tokens?: number;
  output_tokens?: number;
  total_tokens?: number;
  estimated_cost?: number;
  constitutional_score?: number;
  constitutional_passed?: boolean;
  constitutional_data?: ConstitutionalEvaluation;
  error_message?: string;
  metadata?: Record<string, any>;
}

export interface EvaluationResults {
  evaluation_run: EvaluationRun;
  test_cases: TestCase[];
  summary: {
    total_responses: number;
    model_statistics: ModelStatistics[];
  };
}

export interface ModelStatistics {
  provider: string;
  model: string;
  total_requests: number;
  successful_requests: number;
  failed_requests: number;
  avg_response_time_ms: number;
  total_tokens: number;
  total_cost: number;
}

export interface AvailableModels {
  providers: Record<string, string[]>;
}

export interface QuickEvalResult {
  provider: string;
  model: string;
  text?: string;
  response_time_ms?: number;
  tokens?: number;
  cost?: number;
  error?: string;
}
