import { motion } from 'motion/react'
import { ExternalLink, Download, Printer } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Badge } from './ui/badge'
import { Button } from './ui/button'
import { Separator } from './ui/separator'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from './ui/collapsible'
import { SocialMediaShare } from './SocialMediaShare'
import type { AnalysisState } from '../hooks/useForexAnalysis'

interface ComprehensiveReportProps {
  state: AnalysisState
  onNewAnalysis: () => void
}

export function ComprehensiveReport({ state, onNewAnalysis }: ComprehensiveReportProps) {
  if (!state.decision) return null

  const decision = state.decision

  const getActionVariant = (action: string) => {
    if (action === 'BUY') return 'default'
    if (action === 'SELL') return 'destructive'
    return 'secondary'
  }

  const getActionClassName = (action: string) => {
    if (action === 'BUY') return 'bg-green-600 hover:bg-green-700'
    return ''
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container-custom py-12">
        {/* Header */}
        <motion.div
          className="mb-12 text-center"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <h1 className="text-5xl font-semibold mb-3">
            Analysis Complete
          </h1>
          <p className="text-muted-foreground text-lg">
            {state.queryContext?.pair} • {state.query}
          </p>
        </motion.div>

        {/* Main Decision Card */}
        <motion.div
          className="mb-8"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
        >
          <Card>
            <CardContent className="p-8">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-sm text-muted-foreground uppercase tracking-wider mb-3">
                    Recommended Action
                  </h2>
                  <Badge
                    variant={getActionVariant(decision.action)}
                    className={`text-4xl px-6 py-3 font-bold ${getActionClassName(decision.action)}`}
                  >
                    {decision.action}
                  </Badge>
                </div>
                <div className="text-right">
                  <div className="text-sm text-muted-foreground uppercase tracking-wider mb-2">
                    Confidence Level
                  </div>
                  <div className="text-5xl font-bold mb-3">
                    {(decision.confidence * 100).toFixed(0)}%
                  </div>
                  <div className="mt-4 h-3 w-48 bg-muted rounded-full overflow-hidden">
                    <motion.div
                      className="h-full bg-primary"
                      initial={{ width: 0 }}
                      animate={{ width: `${decision.confidence * 100}%` }}
                      transition={{ duration: 0.8, delay: 0.3 }}
                    />
                  </div>
                </div>
              </div>

              {/* Quick Stats */}
              {decision.trade_parameters && (
                <>
                  <Separator className="my-6" />
                  <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                    <StatCard label="Entry Price" value={decision.trade_parameters.entry_price} icon="📍" />
                    <StatCard label="Stop Loss" value={decision.trade_parameters.stop_loss} icon="🛑" />
                    <StatCard label="Take Profit" value={decision.trade_parameters.take_profit} icon="🎯" />
                    <StatCard label="Position Size" value={decision.trade_parameters.position_size.toString()} icon="💰" />
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* Two Column Layout */}
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Left Column - Reasoning & Factors */}
          <div className="lg:col-span-2 space-y-6">
            {/* AI Reasoning */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: 0.2 }}
            >
              <Collapsible defaultOpen>
                <Card>
                  <CardHeader>
                    <CollapsibleTrigger asChild>
                      <Button variant="ghost" className="w-full justify-start p-0 h-auto hover:bg-transparent">
                        <CardTitle className="text-xl">🧠 AI Reasoning & Analysis</CardTitle>
                      </Button>
                    </CollapsibleTrigger>
                  </CardHeader>
                  <CollapsibleContent>
                    <CardContent>
                      <div className="space-y-4">
                        <div>
                          <h4 className="text-sm text-muted-foreground uppercase tracking-wider mb-3">
                            Summary
                          </h4>
                          <p className="leading-relaxed">
                            {decision.reasoning.summary}
                          </p>
                        </div>

                        {decision.reasoning.key_factors && decision.reasoning.key_factors.length > 0 && (
                          <>
                            <Separator />
                            <div>
                              <h4 className="text-sm text-muted-foreground uppercase tracking-wider mb-3">
                                Key Factors
                              </h4>
                              <ul className="space-y-2">
                                {decision.reasoning.key_factors.map((factor: string, idx: number) => (
                                  <li key={idx} className="flex items-start gap-3">
                                    <span className="mt-1">▸</span>
                                    <span className="flex-1">{factor}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          </>
                        )}

                        {decision.reasoning.web_verification && (
                          <>
                            <Separator />
                            <div>
                              <h4 className="text-sm text-muted-foreground uppercase tracking-wider mb-3">
                                Web Verification
                              </h4>
                              <p className="leading-relaxed">
                                {decision.reasoning.web_verification}
                              </p>
                            </div>
                          </>
                        )}
                      </div>
                    </CardContent>
                  </CollapsibleContent>
                </Card>
              </Collapsible>
            </motion.div>

            {/* Comprehensive Report */}
            {state.reportResult && state.reportResult.success && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: 0.25 }}
              >
                <Collapsible defaultOpen>
                  <Card>
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <CollapsibleTrigger asChild>
                          <Button variant="ghost" className="p-0 h-auto hover:bg-transparent">
                            <CardTitle className="text-xl">📄 Comprehensive Report</CardTitle>
                          </Button>
                        </CollapsibleTrigger>
                        <div className="flex gap-2">
                          <Button
                            variant="outline"
                            size="sm"
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
                          >
                            <Download className="w-4 h-4 mr-2" />
                            Download
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              const iframe = document.getElementById('report-iframe') as HTMLIFrameElement;
                              if (iframe && iframe.contentWindow) {
                                iframe.contentWindow.print();
                              }
                            }}
                          >
                            <Printer className="w-4 h-4 mr-2" />
                            Print
                          </Button>
                        </div>
                      </div>
                      <p className="text-sm text-muted-foreground mt-2">
                        {state.reportResult.metadata.word_count} words • {state.reportResult.metadata.sections.length} sections
                      </p>
                    </CardHeader>
                    <CollapsibleContent>
                      <CardContent>
                        <iframe
                          id="report-iframe"
                          srcDoc={state.reportResult.html}
                          className="w-full min-h-[600px] border rounded-lg bg-white"
                          sandbox="allow-same-origin"
                          title="Trading Analysis Report"
                        />
                      </CardContent>
                    </CollapsibleContent>
                  </Card>
                </Collapsible>
              </motion.div>
            )}

            {/* Agent Results */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: 0.3 }}
            >
              <Card>
                <CardHeader>
                  <CardTitle>Multi-Agent Analysis</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {state.newsResult && (
                      <AgentResultCard
                        title="News Sentiment"
                        icon="📰"
                        result={state.newsResult}
                      />
                    )}
                    {state.technicalResult && (
                      <AgentResultCard
                        title="Technical Indicators"
                        icon="📊"
                        result={state.technicalResult}
                      />
                    )}
                    {state.fundamentalResult && (
                      <AgentResultCard
                        title="Fundamental Data"
                        icon="💼"
                        result={state.fundamentalResult}
                      />
                    )}
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            {/* Grounding Sources */}
            {decision.grounding_metadata && decision.grounding_metadata.sources && decision.grounding_metadata.sources.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: 0.35 }}
              >
                <Card>
                  <CardHeader>
                    <CardTitle>📚 Research Sources</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {decision.grounding_metadata.sources.map((source: any, idx: number) => (
                        <a
                          key={idx}
                          href={source.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="block p-4 rounded-lg border hover:bg-accent transition-colors"
                        >
                          <div className="flex items-start gap-3">
                            <div className="text-xl">🔗</div>
                            <div className="flex-1 min-w-0">
                              <div className="font-semibold mb-1 truncate">
                                {source.title}
                              </div>
                              {source.snippet && (
                                <p className="text-sm text-muted-foreground line-clamp-2">
                                  {source.snippet}
                                </p>
                              )}
                            </div>
                            <ExternalLink className="w-5 h-5 text-muted-foreground flex-shrink-0" />
                          </div>
                        </a>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            )}
          </div>

          {/* Right Column - Risk & Context */}
          <div className="space-y-6">
            {/* Risk Assessment */}
            {state.riskResult && state.riskResult.data && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: 0.2 }}
              >
                <Card>
                  <CardHeader>
                    <CardTitle>⚖️ Risk Management</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className={`p-4 rounded-lg ${state.riskResult.data.trade_approved ? 'bg-green-600/10' : 'bg-destructive/10'}`}>
                        <Badge
                          variant={state.riskResult.data.trade_approved ? 'default' : 'destructive'}
                          className={state.riskResult.data.trade_approved ? 'bg-green-600 hover:bg-green-700' : ''}
                        >
                          {state.riskResult.data.trade_approved ? '✓ Risk Approved' : '✗ Risk Rejected'}
                        </Badge>
                        {!state.riskResult.data.trade_approved && state.riskResult.data.rejection_reason && (
                          <p className="text-sm text-muted-foreground mt-2">
                            {state.riskResult.data.rejection_reason}
                          </p>
                        )}
                      </div>

                      {state.riskResult.data.trade_approved && (
                        <>
                          <div className="grid grid-cols-2 gap-3">
                            <Card className="bg-muted/50">
                              <CardContent className="p-3">
                                <div className="text-xs text-muted-foreground mb-1">Risk Amount</div>
                                <div className="font-bold font-mono">${state.riskResult.data.risk_amount}</div>
                              </CardContent>
                            </Card>
                            <Card className="bg-muted/50">
                              <CardContent className="p-3">
                                <div className="text-xs text-muted-foreground mb-1">R/R Ratio</div>
                                <div className="font-bold font-mono">{state.riskResult.data.risk_reward_ratio}:1</div>
                              </CardContent>
                            </Card>
                          </div>

                          <div className="grid grid-cols-2 gap-3">
                            <Card className="bg-muted/50">
                              <CardContent className="p-3">
                                <div className="text-xs text-muted-foreground mb-1">Stop Loss</div>
                                <div className="font-bold font-mono">{state.riskResult.data.stop_loss_pips} pips</div>
                              </CardContent>
                            </Card>
                            <Card className="bg-muted/50">
                              <CardContent className="p-3">
                                <div className="text-xs text-muted-foreground mb-1">Position</div>
                                <div className="font-bold font-mono">{state.riskResult.data.position_size}</div>
                              </CardContent>
                            </Card>
                          </div>
                        </>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            )}

            {/* Query Context */}
            {state.queryContext && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: 0.25 }}
              >
                <Card>
                  <CardHeader>
                    <CardTitle>📋 Analysis Context</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <ContextItem label="Trading Pair" value={state.queryContext.pair} />
                      <ContextItem label="Asset Type" value={state.queryContext.asset_type} />
                      <ContextItem label="Timeframe" value={state.queryContext.timeframe} />
                      <ContextItem label="Risk Tolerance" value={state.queryContext.risk_tolerance} />
                      <Separator />
                      <div>
                        <div className="text-xs text-muted-foreground mb-2 uppercase tracking-wider">
                          User Intent
                        </div>
                        <div className="text-sm">
                          {state.queryContext.user_intent}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            )}

            {/* Social Media Share */}
            {state.finalResult && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: 0.3 }}
              >
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <span>📱</span>
                      <span>Share Analysis</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <SocialMediaShare
                      result={state.finalResult}
                      apiUrl={import.meta.env.VITE_API_URL || 'http://localhost:8000'}
                    />
                  </CardContent>
                </Card>
              </motion.div>
            )}

            {/* Action Buttons */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: 0.35 }}
            >
              <Button
                onClick={onNewAnalysis}
                className="w-full"
                size="lg"
              >
                🔍 New Analysis
              </Button>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  )
}

function StatCard({ label, value, icon }: { label: string; value: string; icon: string }) {
  return (
    <Card className="bg-muted/50">
      <CardContent className="p-4">
        <div className="flex items-center gap-2 mb-2">
          <span className="text-xl">{icon}</span>
          <div className="text-xs text-muted-foreground uppercase tracking-wider">
            {label}
          </div>
        </div>
        <div className="font-bold font-mono text-lg">
          {value}
        </div>
      </CardContent>
    </Card>
  )
}

function AgentResultCard({ title, icon, result }: { title: string; icon: string; result: any }) {
  return (
    <Collapsible>
      <Card className="bg-muted/50">
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="text-2xl">{icon}</span>
              <div>
                <CollapsibleTrigger asChild>
                  <Button variant="ghost" className="p-0 h-auto font-semibold hover:bg-transparent">
                    {title}
                  </Button>
                </CollapsibleTrigger>
                {result.summary && (
                  <p className="text-sm text-muted-foreground mt-1">
                    {result.summary}
                  </p>
                )}
              </div>
            </div>
            <Badge variant={result.success ? 'default' : 'destructive'} className={result.success ? 'bg-green-600 hover:bg-green-700' : ''}>
              {result.success ? 'SUCCESS' : 'FAILED'}
            </Badge>
          </div>

          {result.data && (
            <CollapsibleContent className="pt-4">
              <pre className="text-xs font-mono bg-background p-3 rounded-lg overflow-auto max-h-64">
                {JSON.stringify(result.data, null, 2)}
              </pre>
            </CollapsibleContent>
          )}
        </CardContent>
      </Card>
    </Collapsible>
  )
}

function ContextItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between py-2">
      <span className="text-sm text-muted-foreground">
        {label}
      </span>
      <span className="font-semibold font-mono">
        {value}
      </span>
    </div>
  )
}
