import { motion } from 'motion/react'
import { Reasoning, ReasoningTrigger, ReasoningContent } from './ui/reasoning'
import type { AnalysisState } from '../hooks/useForexAnalysis'

interface ComprehensiveReportProps {
  state: AnalysisState
  onNewAnalysis: () => void
}

export function ComprehensiveReport({ state, onNewAnalysis }: ComprehensiveReportProps) {
  if (!state.decision) return null

  const decision = state.decision
  const actionColor = {
    BUY: { bg: '#10b981', text: 'Emerald' },
    SELL: { bg: '#dc2626', text: 'Ruby' },
    WAIT: { bg: '#f59e0b', text: 'Gold' }
  }[decision.action as 'BUY' | 'SELL' | 'WAIT'] || { bg: '#71717a', text: 'Gray' }

  return (
    <div className="min-h-screen relative overflow-hidden bg-black">
      {/* Animated Grid Background */}
      <div className="absolute inset-0 animated-grid opacity-20" />

      <div className="relative z-10 container-custom py-12">
        {/* Header */}
        <motion.div
          className="mb-12 text-center"
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <h1 className="text-6xl font-bold mb-4">
            <span className="bg-gradient-to-r from-[#f59e0b] via-[#fbbf24] to-[#f59e0b] bg-clip-text text-transparent">
              Analysis Complete
            </span>
          </h1>
          <p className="text-[hsl(var(--text-secondary))] text-lg font-mono">
            {state.queryContext?.pair} • {state.query}
          </p>
        </motion.div>

        {/* Main Decision Card */}
        <motion.div
          className="mb-8"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          <div className="glass rounded-3xl p-8 glow-gold">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-sm font-mono text-[hsl(var(--text-secondary))] uppercase tracking-wider mb-2">
                  Recommended Action
                </h2>
                <div
                  className="text-6xl font-bold inline-block px-8 py-4 rounded-2xl"
                  style={{ backgroundColor: `${actionColor.bg}20`, color: actionColor.bg }}
                >
                  {decision.action}
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm font-mono text-[hsl(var(--text-secondary))] uppercase tracking-wider mb-2">
                  Confidence Level
                </div>
                <div className="text-5xl font-bold text-[#f59e0b]">
                  {(decision.confidence * 100).toFixed(0)}%
                </div>
                <div className="mt-4 h-3 w-48 bg-[hsl(var(--bg-tertiary))] rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-gradient-to-r from-[#f59e0b] to-[#fbbf24]"
                    initial={{ width: 0 }}
                    animate={{ width: `${decision.confidence * 100}%` }}
                    transition={{ duration: 1, delay: 0.5 }}
                  />
                </div>
              </div>
            </div>

            {/* Quick Stats */}
            {decision.trade_parameters && (
              <div className="grid grid-cols-4 gap-4 pt-6 border-t border-[hsl(var(--border))]">
                <StatCard label="Entry Price" value={decision.trade_parameters.entry_price} icon="📍" />
                <StatCard label="Stop Loss" value={decision.trade_parameters.stop_loss} icon="🛑" />
                <StatCard label="Take Profit" value={decision.trade_parameters.take_profit} icon="🎯" />
                <StatCard label="Position Size" value={decision.trade_parameters.position_size.toString()} icon="💰" />
              </div>
            )}
          </div>
        </motion.div>

        {/* Two Column Layout */}
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Left Column - Reasoning & Factors */}
          <div className="lg:col-span-2 space-y-6">
            {/* AI Reasoning */}
            <motion.div
              initial={{ opacity: 0, x: -30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
            >
              <Reasoning className="glass rounded-2xl">
                <div className="p-6">
                  <ReasoningTrigger className="text-xl font-semibold mb-4 text-[#06b6d4] hover:text-[#0ea5e9]">
                    🧠 AI Reasoning & Analysis
                  </ReasoningTrigger>

                  <ReasoningContent className="pt-4">
                    <div className="space-y-4">
                      <div>
                        <h4 className="text-sm font-mono text-[hsl(var(--text-secondary))] uppercase tracking-wider mb-3">
                          Summary
                        </h4>
                        <p className="text-[hsl(var(--text-primary))] leading-relaxed">
                          {decision.reasoning.summary}
                        </p>
                      </div>

                      {decision.reasoning.key_factors && decision.reasoning.key_factors.length > 0 && (
                        <div>
                          <h4 className="text-sm font-mono text-[hsl(var(--text-secondary))] uppercase tracking-wider mb-3">
                            Key Factors
                          </h4>
                          <ul className="space-y-2">
                            {decision.reasoning.key_factors.map((factor: string, idx: number) => (
                              <li key={idx} className="flex items-start gap-3 text-[hsl(var(--text-primary))]">
                                <span className="text-[#f59e0b] mt-1">▸</span>
                                <span className="flex-1">{factor}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {decision.reasoning.web_verification && (
                        <div>
                          <h4 className="text-sm font-mono text-[hsl(var(--text-secondary))] uppercase tracking-wider mb-3">
                            Web Verification
                          </h4>
                          <p className="text-[hsl(var(--text-primary))] leading-relaxed">
                            {decision.reasoning.web_verification}
                          </p>
                        </div>
                      )}
                    </div>
                  </ReasoningContent>
                </div>
              </Reasoning>
            </motion.div>

            {/* Comprehensive Report */}
            {state.reportResult && state.reportResult.success && (
              <motion.div
                initial={{ opacity: 0, x: -30 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.8, delay: 0.45 }}
              >
                <Reasoning className="glass rounded-2xl">
                  <div className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <ReasoningTrigger className="text-xl font-semibold text-[#06b6d4] hover:text-[#0ea5e9]">
                        📄 Comprehensive Report
                      </ReasoningTrigger>
                      <div className="flex gap-2">
                        <button
                          onClick={() => {
                            const blob = new Blob([state.reportResult!.html], { type: 'text/html' });
                            const url = URL.createObjectURL(blob);
                            const a = document.createElement('a');
                            a.href = url;
                            a.download = `trading-report-${state.queryContext?.pair || 'analysis'}-${Date.now()}.html`;
                            document.body.appendChild(a);
                            a.click();
                            document.body.removeChild(a);
                            URL.revokeObjectURL(url);
                          }}
                          className="px-4 py-2 rounded-lg bg-[#06b6d4]/20 text-[#06b6d4] hover:bg-[#06b6d4]/30 transition-colors text-sm font-mono"
                        >
                          Download HTML
                        </button>
                        <button
                          onClick={() => {
                            const iframe = document.getElementById('report-iframe') as HTMLIFrameElement;
                            if (iframe && iframe.contentWindow) {
                              iframe.contentWindow.print();
                            }
                          }}
                          className="px-4 py-2 rounded-lg bg-[#10b981]/20 text-[#10b981] hover:bg-[#10b981]/30 transition-colors text-sm font-mono"
                        >
                          Print
                        </button>
                      </div>
                    </div>

                    <div className="text-sm text-[hsl(var(--text-secondary))] mb-4 font-mono">
                      {state.reportResult.metadata.word_count} words • {state.reportResult.metadata.sections.length} sections
                    </div>

                    <ReasoningContent className="pt-4">
                      <iframe
                        id="report-iframe"
                        srcDoc={state.reportResult.html}
                        className="w-full min-h-[600px] border border-[hsl(var(--border))] rounded-lg bg-white"
                        sandbox="allow-same-origin"
                        title="Trading Analysis Report"
                      />
                    </ReasoningContent>
                  </div>
                </Reasoning>
              </motion.div>
            )}

            {/* Agent Results */}
            <motion.div
              initial={{ opacity: 0, x: -30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, delay: 0.5 }}
            >
              <div className="glass rounded-2xl p-6">
                <h3 className="text-xl font-semibold mb-6 text-[#06b6d4]">
                  Multi-Agent Analysis
                </h3>

                <div className="space-y-4">
                  {state.newsResult && (
                    <AgentResultCard
                      title="News Sentiment"
                      icon="📰"
                      result={state.newsResult}
                      color="#06b6d4"
                    />
                  )}
                  {state.technicalResult && (
                    <AgentResultCard
                      title="Technical Indicators"
                      icon="📊"
                      result={state.technicalResult}
                      color="#10b981"
                    />
                  )}
                  {state.fundamentalResult && (
                    <AgentResultCard
                      title="Fundamental Data"
                      icon="💼"
                      result={state.fundamentalResult}
                      color="#f59e0b"
                    />
                  )}
                </div>
              </div>
            </motion.div>

            {/* Grounding Sources */}
            {decision.grounding_metadata && decision.grounding_metadata.sources && decision.grounding_metadata.sources.length > 0 && (
              <motion.div
                initial={{ opacity: 0, x: -30 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.8, delay: 0.6 }}
              >
                <div className="glass rounded-2xl p-6">
                  <h3 className="text-xl font-semibold mb-6 text-[#06b6d4]">
                    📚 Research Sources
                  </h3>

                  <div className="space-y-3">
                    {decision.grounding_metadata.sources.map((source: any, idx: number) => (
                      <a
                        key={idx}
                        href={source.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block p-4 rounded-xl bg-[#1a1f3a] border border-[hsl(var(--gold)/0.3)] hover:border-[hsl(var(--gold)/0.6)] hover:bg-[#242943] transition-all duration-300"
                      >
                        <div className="flex items-start gap-3">
                          <div className="text-xl">🔗</div>
                          <div className="flex-1 min-w-0">
                            <div className="font-semibold text-white mb-1 truncate">
                              {source.title}
                            </div>
                            {source.snippet && (
                              <p className="text-sm text-gray-300 line-clamp-2">
                                {source.snippet}
                              </p>
                            )}
                          </div>
                          <div className="text-gray-400">
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                            </svg>
                          </div>
                        </div>
                      </a>
                    ))}
                  </div>
                </div>
              </motion.div>
            )}
          </div>

          {/* Right Column - Risk & Context */}
          <div className="space-y-6">
            {/* Risk Assessment */}
            {state.riskResult && state.riskResult.data && (
              <motion.div
                initial={{ opacity: 0, x: 30 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.8, delay: 0.4 }}
              >
                <div className="glass rounded-2xl p-6">
                  <h3 className="text-xl font-semibold mb-6 text-[#f59e0b]">
                    ⚖️ Risk Management
                  </h3>

                  <div className="space-y-4">
                    <div className={`p-4 rounded-xl ${state.riskResult.data.trade_approved ? 'bg-[#10b981]/20' : 'bg-[#dc2626]/20'}`}>
                      <div className={`font-bold mb-2 ${state.riskResult.data.trade_approved ? 'text-[#10b981]' : 'text-[#dc2626]'}`}>
                        {state.riskResult.data.trade_approved ? '✓ Risk Approved' : '✗ Risk Rejected'}
                      </div>
                      {!state.riskResult.data.trade_approved && state.riskResult.data.rejection_reason && (
                        <p className="text-sm text-[hsl(var(--text-secondary))]">
                          {state.riskResult.data.rejection_reason}
                        </p>
                      )}
                    </div>

                    {state.riskResult.data.trade_approved && (
                      <>
                        <div className="grid grid-cols-2 gap-3">
                          <div className="p-3 rounded-lg bg-[hsl(var(--bg-tertiary))]">
                            <div className="text-xs text-[hsl(var(--text-muted))] mb-1 font-mono">Risk Amount</div>
                            <div className="font-bold text-[#f59e0b] font-mono">${state.riskResult.data.risk_amount}</div>
                          </div>
                          <div className="p-3 rounded-lg bg-[hsl(var(--bg-tertiary))]">
                            <div className="text-xs text-[hsl(var(--text-muted))] mb-1 font-mono">R/R Ratio</div>
                            <div className="font-bold text-[#f59e0b] font-mono">{state.riskResult.data.risk_reward_ratio}:1</div>
                          </div>
                        </div>

                        <div className="grid grid-cols-2 gap-3">
                          <div className="p-3 rounded-lg bg-[hsl(var(--bg-tertiary))]">
                            <div className="text-xs text-[hsl(var(--text-muted))] mb-1 font-mono">Stop Loss</div>
                            <div className="font-bold text-[#06b6d4] font-mono">{state.riskResult.data.stop_loss_pips} pips</div>
                          </div>
                          <div className="p-3 rounded-lg bg-[hsl(var(--bg-tertiary))]">
                            <div className="text-xs text-[hsl(var(--text-muted))] mb-1 font-mono">Position</div>
                            <div className="font-bold text-[#06b6d4] font-mono">{state.riskResult.data.position_size}</div>
                          </div>
                        </div>
                      </>
                    )}
                  </div>
                </div>
              </motion.div>
            )}

            {/* Query Context */}
            {state.queryContext && (
              <motion.div
                initial={{ opacity: 0, x: 30 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.8, delay: 0.5 }}
              >
                <div className="glass rounded-2xl p-6">
                  <h3 className="text-xl font-semibold mb-6 text-[#06b6d4]">
                    📋 Analysis Context
                  </h3>

                  <div className="space-y-3">
                    <ContextItem label="Trading Pair" value={state.queryContext.pair} />
                    <ContextItem label="Asset Type" value={state.queryContext.asset_type} />
                    <ContextItem label="Timeframe" value={state.queryContext.timeframe} />
                    <ContextItem label="Risk Tolerance" value={state.queryContext.risk_tolerance} />
                    <div className="pt-3 border-t border-[hsl(var(--border))]">
                      <div className="text-xs text-[hsl(var(--text-muted))] mb-2 font-mono uppercase tracking-wider">
                        User Intent
                      </div>
                      <div className="text-sm text-[hsl(var(--text-primary))]">
                        {state.queryContext.user_intent}
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}

            {/* Action Buttons */}
            <motion.div
              initial={{ opacity: 0, x: 30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, delay: 0.6 }}
            >
              <button
                onClick={onNewAnalysis}
                className="w-full px-6 py-4 rounded-xl font-semibold bg-gradient-to-r from-[#f59e0b] to-[#fbbf24] text-[hsl(var(--bg-primary))] hover:glow-gold transition-all duration-300"
              >
                🔍 New Analysis
              </button>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  )
}

function StatCard({ label, value, icon }: { label: string; value: string; icon: string }) {
  return (
    <div className="p-4 rounded-xl bg-[hsl(var(--bg-tertiary))]">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-xl">{icon}</span>
        <div className="text-xs text-[hsl(var(--text-muted))] font-mono uppercase tracking-wider">
          {label}
        </div>
      </div>
      <div className="font-bold text-[#06b6d4] font-mono text-lg">
        {value}
      </div>
    </div>
  )
}

function AgentResultCard({ title, icon, result, color }: { title: string; icon: string; result: any; color: string }) {
  return (
    <Reasoning>
      <div className="p-4 rounded-xl bg-[hsl(var(--bg-tertiary))]">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">{icon}</span>
            <div>
              <ReasoningTrigger className="font-semibold hover:opacity-80" style={{ color }}>
                {title}
              </ReasoningTrigger>
              {result.summary && (
                <p className="text-sm text-[hsl(var(--text-secondary))] mt-1">
                  {result.summary}
                </p>
              )}
            </div>
          </div>
          <div className={`px-3 py-1 rounded-full text-xs font-mono ${result.success ? 'bg-[#10b981]/20 text-[#10b981]' : 'bg-[#dc2626]/20 text-[#dc2626]'}`}>
            {result.success ? 'SUCCESS' : 'FAILED'}
          </div>
        </div>

        {result.data && (
          <ReasoningContent className="pt-4" contentClassName="!prose-sm">
            <pre className="text-xs font-mono bg-[hsl(var(--bg-primary))] p-3 rounded-lg overflow-auto max-h-64 text-[hsl(var(--text-secondary))]">
              {JSON.stringify(result.data, null, 2)}
            </pre>
          </ReasoningContent>
        )}
      </div>
    </Reasoning>
  )
}

function ContextItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between py-2">
      <span className="text-sm text-[hsl(var(--text-muted))] font-mono">
        {label}
      </span>
      <span className="font-semibold text-[hsl(var(--text-primary))] font-mono">
        {value}
      </span>
    </div>
  )
}
