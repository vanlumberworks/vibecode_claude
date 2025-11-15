import { useState } from 'react';
import { motion } from 'motion/react';
import { Clock, CheckCircle2, AlertCircle, Loader2, Search } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from './ui/collapsible';
import { Button } from './ui/button';
import { ShiningText } from './ui/shining-text';
import type { AnalysisState } from '../hooks/useForexAnalysis';

interface AgentExecutionDetailsProps {
  state: AnalysisState;
  isAnalyzing: boolean;
}

export function AgentExecutionDetails({ state, isAnalyzing }: AgentExecutionDetailsProps) {
  const [expandedCards, setExpandedCards] = useState<Record<string, boolean>>({});

  const toggleCard = (agentId: string) => {
    setExpandedCards(prev => ({
      ...prev,
      [agentId]: !prev[agentId]
    }));
  };

  const agents = [
    {
      id: 'news',
      title: 'News Agent',
      icon: '📰',
      agentState: state.agents.news,
    },
    {
      id: 'technical',
      title: 'Technical Agent',
      icon: '📊',
      agentState: state.agents.technical,
    },
    {
      id: 'fundamental',
      title: 'Fundamental Agent',
      icon: '💼',
      agentState: state.agents.fundamental,
    }
  ];

  // Don't show if no agents are running or completed
  if (!isAnalyzing && !agents.some(a => a.agentState.status !== 'pending')) {
    return null;
  }

  // Format execution time
  const formatExecutionTime = (timeInSeconds: number | null) => {
    if (!timeInSeconds) return 'N/A';
    return `${timeInSeconds.toFixed(2)}s`;
  };

  return (
    <motion.div
      className="mt-8"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-semibold">
          Parallel Agent Execution
        </h2>
        <Badge variant="secondary">
          {agents.filter(a => a.agentState.status === 'completed').length} / {agents.length} agents completed
        </Badge>
      </div>

      {/* 3 Agent Cards in Horizontal Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {agents.map((agent, index) => {
          const agentData = agent.agentState;
          const isActive = agentData.status === 'running';
          const isCompleted = agentData.status === 'completed';
          const isFailed = agentData.status === 'failed';

          return (
            <motion.div
              key={agent.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <Card>
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">{agent.icon}</span>
                      <div>
                        <CardTitle className="text-lg">{agent.title}</CardTitle>
                        <div className="mt-1">
                          {isActive && (
                            <Badge variant="default" className="text-xs">
                              <Loader2 className="w-3 h-3 mr-1 animate-spin" />
                              <ShiningText text="Processing..." className="text-xs" />
                            </Badge>
                          )}
                          {isCompleted && (
                            <Badge variant="default" className="text-xs bg-green-600 hover:bg-green-700">
                              <CheckCircle2 className="w-3 h-3 mr-1" />
                              Completed
                            </Badge>
                          )}
                          {isFailed && (
                            <Badge variant="destructive" className="text-xs">
                              <AlertCircle className="w-3 h-3 mr-1" />
                              Failed
                            </Badge>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </CardHeader>

                <CardContent>
                  {/* Researching Status (when analyzing or running) */}
                  {(isActive || (isAnalyzing && !isCompleted && !isFailed)) && (
                    <div className="mb-4 flex items-center justify-center py-3">
                      <ShiningText text="Researching..." className="text-base" />
                    </div>
                  )}

                  {/* Current Step (when running) */}
                  {isActive && agentData.currentStep && (
                    <Card className="mb-4 bg-muted/50">
                      <CardContent className="p-3">
                        <div className="text-xs text-muted-foreground mb-1">Current Step:</div>
                        <ShiningText text={agentData.currentStep} className="text-sm" />
                      </CardContent>
                    </Card>
                  )}

                  {/* Progress Bar */}
                  <div className="mb-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs text-muted-foreground">Progress</span>
                      <span className="text-sm font-mono font-semibold">
                        {agentData.progress}%
                      </span>
                    </div>
                    <Progress value={agentData.progress} className="h-2" />
                  </div>

                  {/* Execution Time */}
                  {agentData.executionTime !== null && (
                    <div className="flex items-center gap-2 mb-4 text-sm text-muted-foreground">
                      <Clock className="w-4 h-4" />
                      <span>Execution time: {formatExecutionTime(agentData.executionTime)}</span>
                    </div>
                  )}

                  {/* Intermediate Data - Collapsible */}
                  {agentData.intermediateData && Object.keys(agentData.intermediateData).length > 0 && (
                    <div className="mb-4">
                      <Collapsible
                        open={expandedCards[`${agent.id}-data`]}
                        onOpenChange={() => toggleCard(`${agent.id}-data`)}
                      >
                        <CollapsibleTrigger asChild>
                          <Button variant="outline" className="w-full justify-between" size="sm">
                            <div className="flex items-center gap-2">
                              <span className="text-xs">📊</span>
                              <span>Intermediate Data ({Object.keys(agentData.intermediateData).length} items)</span>
                            </div>
                          </Button>
                        </CollapsibleTrigger>

                        <CollapsibleContent className="mt-3">
                          <div className="space-y-2 max-h-64 overflow-y-auto">
                            {Object.entries(agentData.intermediateData).map(([key, value]) => (
                              <Card key={key} className="bg-muted/50">
                                <CardContent className="p-3">
                                  <div className="text-xs text-muted-foreground mb-1.5 font-semibold">{key}:</div>
                                  <div className="text-sm">
                                    {typeof value === 'object' && value !== null ? (
                                      Array.isArray(value) ? (
                                        <ul className="space-y-1 ml-2">
                                          {value.map((item: any, idx: number) => (
                                            <li key={idx} className="flex items-start gap-2">
                                              <span className="text-muted-foreground mt-1">•</span>
                                              <span className="flex-1 break-words">{typeof item === 'object' ? JSON.stringify(item) : String(item)}</span>
                                            </li>
                                          ))}
                                        </ul>
                                      ) : (
                                        <div className="space-y-1">
                                          {Object.entries(value).map(([k, v]) => (
                                            <div key={k} className="flex gap-2">
                                              <span className="text-muted-foreground">{k}:</span>
                                              <span className="flex-1 break-words font-mono text-xs">{String(v)}</span>
                                            </div>
                                          ))}
                                        </div>
                                      )
                                    ) : (
                                      <span className="break-words font-mono text-xs">{String(value)}</span>
                                    )}
                                  </div>
                                </CardContent>
                              </Card>
                            ))}
                          </div>
                        </CollapsibleContent>
                      </Collapsible>
                    </div>
                  )}

                  {/* Web Search Collapsible */}
                  {(agentData.webSearchQueries.length > 0 || agentData.webSearchSources.length > 0) && (
                    <Collapsible
                      open={expandedCards[agent.id]}
                      onOpenChange={() => toggleCard(agent.id)}
                    >
                      <CollapsibleTrigger asChild>
                        <Button variant="outline" className="w-full justify-between" size="sm">
                          <div className="flex items-center gap-2">
                            <Search className="w-4 h-4" />
                            <span>Web Search ({agentData.webSearchQueries.length + agentData.webSearchSources.length} items)</span>
                          </div>
                        </Button>
                      </CollapsibleTrigger>

                      <CollapsibleContent className="mt-3">
                        <Card className="bg-muted/50">
                          <CardContent className="p-4">
                            {/* Search Queries */}
                            {agentData.webSearchQueries.length > 0 && (
                              <div className="mb-4">
                                <h5 className="text-xs font-semibold text-muted-foreground mb-2 flex items-center gap-2">
                                  <Search className="w-3 h-3" />
                                  Search Queries:
                                </h5>
                                <div className="space-y-2">
                                  {agentData.webSearchQueries.map((query: string, idx: number) => (
                                    <div
                                      key={idx}
                                      className="px-3 py-1.5 rounded-md bg-background border text-xs font-mono"
                                    >
                                      "{query}"
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}

                            {/* Search Sources */}
                            {agentData.webSearchSources.length > 0 && (
                              <div>
                                <h5 className="text-xs font-semibold text-muted-foreground mb-2">
                                  Sources ({agentData.webSearchSources.length}):
                                </h5>
                                <div className="space-y-2 max-h-48 overflow-y-auto">
                                  {agentData.webSearchSources.map((source: { title: string; url: string }, idx: number) => (
                                    <a
                                      key={idx}
                                      href={source.url}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      className="block px-3 py-2 rounded-md bg-background border hover:bg-accent transition-colors"
                                    >
                                      <div className="text-xs font-semibold mb-1">
                                        {source.title}
                                      </div>
                                      <div className="text-xs text-muted-foreground truncate">
                                        {source.url}
                                      </div>
                                    </a>
                                  ))}
                                </div>
                              </div>
                            )}

                            {/* Messages (if any) */}
                            {agentData.messages.length > 0 && (
                              <div className="mt-4 pt-4 border-t">
                                <h5 className="text-xs font-semibold text-muted-foreground mb-2">
                                  Activity Log ({agentData.messages.length}):
                                </h5>
                                <div className="space-y-1 max-h-32 overflow-y-auto">
                                  {agentData.messages.slice(-5).map((msg: string, idx: number) => (
                                    <div
                                      key={idx}
                                      className="text-xs font-mono flex items-start gap-2"
                                    >
                                      <span className="text-muted-foreground mt-0.5">›</span>
                                      <span className="flex-1">{msg}</span>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                          </CardContent>
                        </Card>
                      </CollapsibleContent>
                    </Collapsible>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          );
        })}
      </div>
    </motion.div>
  );
}
