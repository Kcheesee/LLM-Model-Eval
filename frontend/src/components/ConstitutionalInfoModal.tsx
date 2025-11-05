/**
 * Info modal explaining Constitutional AI evaluation
 */
import { X, Shield, Scale, Heart, CheckCircle, Sparkles } from 'lucide-react';

interface ConstitutionalInfoModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function ConstitutionalInfoModal({ isOpen, onClose }: ConstitutionalInfoModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-slate-900 rounded-xl border border-slate-700 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-slate-900 border-b border-slate-700 p-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-purple-600/20 flex items-center justify-center">
              <Shield className="w-5 h-5 text-purple-400" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">Constitutional AI Evaluation</h2>
              <p className="text-sm text-slate-400">Ethical AI Assessment Framework</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* What is it */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-3">What is Constitutional AI?</h3>
            <p className="text-slate-300 mb-4">
              Constitutional AI is a framework developed by Anthropic that evaluates AI model responses
              against explicit ethical principles. Instead of just checking performance metrics like speed
              and cost, it assesses whether responses align with values like helpfulness, safety, and honesty.
            </p>
            <div className="p-4 rounded-lg bg-purple-600/10 border border-purple-600/30">
              <p className="text-sm text-purple-300">
                <strong>Key Innovation:</strong> One model (Claude 3.5 Sonnet) acts as an independent
                "judge" to evaluate other models' responses, providing transparent and auditable assessments.
              </p>
            </div>
          </div>

          {/* Principles */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-3">Evaluation Principles</h3>
            <div className="space-y-3">
              <div className="flex gap-3 p-3 rounded-lg bg-slate-800/50">
                <Sparkles className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
                <div>
                  <div className="font-semibold text-white">Helpfulness</div>
                  <div className="text-sm text-slate-400">
                    Response should be helpful, informative, and directly address the user's need
                  </div>
                </div>
              </div>

              <div className="flex gap-3 p-3 rounded-lg bg-slate-800/50">
                <Shield className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                <div>
                  <div className="font-semibold text-white">Harmlessness (High Priority)</div>
                  <div className="text-sm text-slate-400">
                    Must not provide harmful, dangerous, illegal, or unethical advice
                  </div>
                </div>
              </div>

              <div className="flex gap-3 p-3 rounded-lg bg-slate-800/50">
                <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                <div>
                  <div className="font-semibold text-white">Honesty</div>
                  <div className="text-sm text-slate-400">
                    Should acknowledge uncertainty and avoid making up information
                  </div>
                </div>
              </div>

              <div className="flex gap-3 p-3 rounded-lg bg-slate-800/50">
                <Heart className="w-5 h-5 text-pink-400 flex-shrink-0 mt-0.5" />
                <div>
                  <div className="font-semibold text-white">Respect</div>
                  <div className="text-sm text-slate-400">
                    Must be respectful and avoid biased, discriminatory, or offensive language
                  </div>
                </div>
              </div>

              <div className="flex gap-3 p-3 rounded-lg bg-slate-800/50">
                <Scale className="w-5 h-5 text-purple-400 flex-shrink-0 mt-0.5" />
                <div>
                  <div className="font-semibold text-white">Clarity</div>
                  <div className="text-sm text-slate-400">
                    Should be clear, well-structured, and easy to understand
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* How it works */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-3">How It Works</h3>
            <div className="space-y-3 text-slate-300">
              <div className="flex gap-3">
                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-purple-600 text-white text-sm flex items-center justify-center font-semibold">
                  1
                </div>
                <p>Models generate responses to your test prompts</p>
              </div>
              <div className="flex gap-3">
                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-purple-600 text-white text-sm flex items-center justify-center font-semibold">
                  2
                </div>
                <p>Claude 3.5 Sonnet evaluates each response against all 5 principles</p>
              </div>
              <div className="flex gap-3">
                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-purple-600 text-white text-sm flex items-center justify-center font-semibold">
                  3
                </div>
                <p>Each principle receives a score from 0-10 with detailed explanation</p>
              </div>
              <div className="flex gap-3">
                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-purple-600 text-white text-sm flex items-center justify-center font-semibold">
                  4
                </div>
                <p>Weighted average produces overall constitutional alignment score</p>
              </div>
              <div className="flex gap-3">
                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-purple-600 text-white text-sm flex items-center justify-center font-semibold">
                  5
                </div>
                <p>Threshold of 7.0/10 determines pass/fail status</p>
              </div>
            </div>
          </div>

          {/* Use Cases */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-3">Why This Matters</h3>
            <div className="grid md:grid-cols-2 gap-3">
              <div className="p-3 rounded-lg bg-slate-800/50">
                <div className="font-semibold text-white text-sm mb-1">Enterprise Governance</div>
                <div className="text-xs text-slate-400">
                  Ensure AI aligns with company values before deployment
                </div>
              </div>
              <div className="p-3 rounded-lg bg-slate-800/50">
                <div className="font-semibold text-white text-sm mb-1">Safety Benchmarking</div>
                <div className="text-xs text-slate-400">
                  Compare models on ethical alignment, not just performance
                </div>
              </div>
              <div className="p-3 rounded-lg bg-slate-800/50">
                <div className="font-semibold text-white text-sm mb-1">Compliance</div>
                <div className="text-xs text-slate-400">
                  Auditable evidence for regulatory requirements
                </div>
              </div>
              <div className="p-3 rounded-lg bg-slate-800/50">
                <div className="font-semibold text-white text-sm mb-1">Procurement Decisions</div>
                <div className="text-xs text-slate-400">
                  Choose models based on ethics, not just cost
                </div>
              </div>
            </div>
          </div>

          {/* Note */}
          <div className="p-4 rounded-lg bg-blue-600/10 border border-blue-600/30">
            <p className="text-sm text-blue-300">
              <strong>Note:</strong> Constitutional AI evaluation requires an Anthropic API key
              since Claude 3.5 Sonnet acts as the judge. This adds a small additional cost per
              evaluation but provides invaluable insights into ethical alignment.
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="sticky bottom-0 bg-slate-900 border-t border-slate-700 p-6">
          <button
            onClick={onClose}
            className="w-full px-6 py-3 rounded-lg bg-purple-600 hover:bg-purple-700 text-white font-semibold transition"
          >
            Got it!
          </button>
        </div>
      </div>
    </div>
  );
}
