import { motion } from 'motion/react'
import {
  Loader2,
  Download,
  FileText,
  Sparkles,
  Zap,
  GitMerge,
  ClipboardCheck
} from 'lucide-react'
import { AgentExecutionDetails } from './AgentExecutionDetails'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Badge } from './ui/badge'
import { Progress } from './ui/progress'
import { Button } from './ui/button'
import { ShiningText } from './ui/shining-text'
import { Timeline, type TimelineItem } from './ui/timeline'
import type { AnalysisState } from '../hooks/useForexAnalysis'

interface ReasoningTimelineProps {
  state: AnalysisState
  isAnalyzing: boolean
  query: string
  onViewReport?: () => void
}

export function ReasoningTimeline({ state, isAnalyzing, query, onViewReport }: ReasoningTimelineProps) {
  // Timeline items for process flow
  const timelineItems: TimelineItem[] = [
    {
      id: 'query',
      title: 'Understanding Your Request',
      description: 'Our AI is reading and interpreting your trading question',
      status: state.queryContext ? 'completed' : (state.progress.stage === 'parsing' ? 'active' : 'pending'),
      icon: <Sparkles className="h-3 w-3" />,
    },
    {
      id: 'parallel',
      title: 'Expert Agents at Work',
      description: 'Three specialist agents analyzing news, charts, and market fundamentals for you',
      status: state.progress.agentsCompleted === 3 ? 'completed' : (state.progress.stage === 'analyzing' || state.progress.totalAgents > 0 ? 'active' : 'pending'),
      icon: <Zap className="h-3 w-3" />,
    },
    {
      id: 'synthesis',
      title: 'Connecting the Dots',
      description: 'Combining insights from all agents to form a complete picture',
      status: state.decision ? 'completed' : (state.progress.stage === 'decision' ? 'active' : 'pending'),
      icon: <GitMerge className="h-3 w-3" />,
    },
    {
      id: 'report',
      title: 'Preparing Your Report',
      description: 'Crafting a clear, actionable trading recommendation just for you',
      status: state.reportResult?.success ? 'completed' : (state.progress.stage === 'report' || state.progress.currentAgent === 'report' ? 'active' : 'pending'),
      icon: <ClipboardCheck className="h-3 w-3" />,
    },
  ]

  const completedSteps = timelineItems.filter(s => s.status === 'completed').length
  const totalSteps = timelineItems.length
  const progressPercentage = (completedSteps / totalSteps) * 100

  return (
    <div className="min-h-screen bg-background">
      <div className="container-custom py-12">
        {/* Header */}
        <motion.div
          className="mb-8"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-sm text-muted-foreground mb-1">Analysis Query</h2>
                  <p className="text-2xl font-semibold">{query}</p>
                </div>
                <div className="flex items-center gap-3">
                  {isAnalyzing ? (
                    <Badge variant="default">
                      <div className="w-2 h-2 rounded-full bg-current animate-pulse mr-2" />
                      <ShiningText text={`Processing ${Math.round(progressPercentage)}%`} className="text-xs" />
                    </Badge>
                  ) : (
                    <Badge variant="default" className="bg-green-600 hover:bg-green-700">
                      <div className="w-2 h-2 rounded-full bg-current mr-2" />
                      Completed 100%
                    </Badge>
                  )}
                </div>
              </div>

              {/* Overall Progress Bar */}
              <div className="mt-6">
                <Progress value={progressPercentage} className="h-2" />
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* 2-Column Layout: Process Flow (Left) + Content (Right) */}
        <div className="grid grid-cols-1 lg:grid-cols-[240px_1fr] gap-6">
          {/* LEFT SIDEBAR: Process Flow */}
          <motion.div
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1, duration: 0.3 }}
          >
            <Card>
              <CardHeader>
                <CardTitle className="text-xs uppercase tracking-wider text-muted-foreground">
                  Process Flow
                </CardTitle>
              </CardHeader>
              <CardContent>
                <Timeline
                  items={timelineItems}
                  variant="compact"
                  showTimestamps={false}
                  isAnalyzing={isAnalyzing}
                />
              </CardContent>
            </Card>
          </motion.div>

          {/* RIGHT CONTENT AREA */}
          <div className="space-y-6">
            {/* Parallel Agent Execution */}
            <AgentExecutionDetails state={state} isAnalyzing={isAnalyzing} />

            {/* Data Synthesis Section */}
            {state.decision && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
              >
                <Card>
                  <CardHeader>
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 rounded-full bg-muted flex items-center justify-center">
                        <span className="text-2xl">🧠</span>
                      </div>
                      <div>
                        <CardTitle>Data Synthesis</CardTitle>
                        <p className="text-sm text-muted-foreground mt-1">Synthesis completed</p>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex items-center gap-2">
                        <svg className="w-5 h-5 text-green-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        <p className="text-sm text-muted-foreground">
                          All three analysis dimensions (News, Technical, Fundamental) indicate favorable conditions for gold investment
                        </p>
                      </div>

                      <div className="flex items-center gap-2">
                        <svg className="w-5 h-5 text-green-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        <p className="text-sm text-muted-foreground">
                          Confluence of bullish technical signals and positive fundamental factors
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            )}

            {/* Final Report Section */}
            {(state.progress.stage === 'report' || state.reportResult) && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
              >
                <Card>
                  <CardHeader>
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 rounded-full bg-muted flex items-center justify-center">
                        {state.progress.stage === 'report' && !state.reportResult?.success ? (
                          <Loader2 className="w-6 h-6 animate-spin" />
                        ) : (
                          <span className="text-2xl">📊</span>
                        )}
                      </div>
                      <div>
                        <CardTitle>Final Analysis Report</CardTitle>
                        <div className="text-sm text-muted-foreground mt-1">
                          {state.reportResult?.success ? (
                            <span>Report generated</span>
                          ) : (
                            <ShiningText text="Generating report..." className="text-sm" />
                          )}
                        </div>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="p-4">
                    {state.reportResult?.success ? (
                      <div className="space-y-4">
                        {/* Report Success Message */}
                        <div className="flex items-center justify-between">
                          <div>
                            <h4 className="text-base font-semibold mb-1">
                              Report Generated Successfully
                            </h4>
                            <p className="text-xs text-muted-foreground">
                              {state.reportResult.metadata.word_count} words • {state.reportResult.metadata.sections.length} sections
                            </p>
                          </div>
                          <div className="text-3xl">📊</div>
                        </div>

                        {/* Action Buttons */}
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                          {onViewReport && state.finalResult && (
                            <Button
                              variant="default"
                              className="w-full"
                              onClick={onViewReport}
                            >
                              <FileText className="w-4 h-4 mr-2" />
                              View Full Report
                            </Button>
                          )}
                          <Button
                            variant="secondary"
                            className="w-full"
                            onClick={() => {
                              const blob = new Blob([state.reportResult!.html], { type: 'text/html' });
                              const url = URL.createObjectURL(blob);
                              const a = document.createElement('a');
                              a.href = url;
                              a.download = `trading-report-${Date.now()}.html`;
                              document.body.appendChild(a);
                              a.click();
                              document.body.removeChild(a);
                              URL.revokeObjectURL(url);
                            }}
                          >
                            <Download className="w-4 h-4 mr-2" />
                            Download Report
                          </Button>
                        </div>
                      </div>
                    ) : (
                      <div className="flex items-center justify-center py-12">
                        <div className="flex flex-col items-center gap-4">
                          <Loader2 className="w-12 h-12 animate-spin" />
                          <ShiningText text="Generating comprehensive report..." className="text-sm font-mono" />
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </motion.div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
