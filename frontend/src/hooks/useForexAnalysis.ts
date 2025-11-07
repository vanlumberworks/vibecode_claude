/**
 * React Hook for Forex Agent System Streaming API
 *
 * This custom hook provides a clean interface for consuming the streaming API
 * in React applications. It handles connection management, event parsing,
 * and state updates automatically.
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import type {
  AnalysisResult,
  QueryContext,
  AgentResult,
  Decision,
  ReportData,
} from '../types/forex-api';

// ============================================================================
// Types
// ============================================================================

export interface AgentState {
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number; // 0-100
  messages: string[];
  currentStep: string | null;
  startTime: string | null;
  endTime: string | null;
  executionTime: number | null;
  intermediateData: any;
  webSearchQueries: string[];
  webSearchSources: Array<{ title: string; url: string }>;
  result: AgentResult | null;
}

export interface AnalysisState {
  query: string | null;
  queryContext: QueryContext | null;

  // Per-agent state tracking
  agents: {
    news: AgentState;
    technical: AgentState;
    fundamental: AgentState;
  };

  // Legacy support (deprecated)
  newsResult: AgentResult | null;
  technicalResult: AgentResult | null;
  fundamentalResult: AgentResult | null;

  riskResult: AgentResult | null;
  decision: Decision | null;
  reportResult: ReportData | null;
  finalResult: AnalysisResult | null;
  progress: {
    stage: 'idle' | 'parsing' | 'analyzing' | 'risk' | 'decision' | 'report' | 'complete';
    agentsCompleted: number;
    totalAgents: number;
    currentAgent: string | null;
    currentStep: string | null;
    progressMessages: string[];
  };
}

export interface UseForexAnalysisOptions {
  apiUrl?: string;
  onStart?: () => void;
  onComplete?: (result: AnalysisResult) => void;
  onError?: (error: string) => void;
  autoReconnect?: boolean;
  maxReconnectAttempts?: number;
}

export interface UseForexAnalysisReturn {
  analyze: (query: string) => void;
  cancel: () => void;
  state: AnalysisState;
  isAnalyzing: boolean;
  error: string | null;
}

// ============================================================================
// Initial State
// ============================================================================

const initialAgentState: AgentState = {
  status: 'pending',
  progress: 0,
  messages: [],
  currentStep: null,
  startTime: null,
  endTime: null,
  executionTime: null,
  intermediateData: null,
  webSearchQueries: [],
  webSearchSources: [],
  result: null,
};

const initialState: AnalysisState = {
  query: null,
  queryContext: null,

  // Initialize per-agent state
  agents: {
    news: { ...initialAgentState },
    technical: { ...initialAgentState },
    fundamental: { ...initialAgentState },
  },

  // Legacy support (deprecated)
  newsResult: null,
  technicalResult: null,
  fundamentalResult: null,

  riskResult: null,
  decision: null,
  reportResult: null,
  finalResult: null,
  progress: {
    stage: 'idle',
    agentsCompleted: 0,
    totalAgents: 3,
    currentAgent: null,
    currentStep: null,
    progressMessages: [],
  },
};

// ============================================================================
// Custom Hook
// ============================================================================

export function useForexAnalysis(
  options: UseForexAnalysisOptions = {}
): UseForexAnalysisReturn {
  const {
    apiUrl = 'http://localhost:8000',
    onStart,
    onComplete,
    onError,
    autoReconnect = false,
    maxReconnectAttempts = 3,
  } = options;

  const [state, setState] = useState<AnalysisState>(initialState);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef<number | null>(null);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, []);

  // Cancel analysis
  const cancel = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    setIsAnalyzing(false);
    setState(initialState);
  }, []);

  // Handle reconnection
  const handleReconnect = useCallback(
    (query: string) => {
      if (!autoReconnect || reconnectAttemptsRef.current >= maxReconnectAttempts) {
        setError('Connection lost. Please try again.');
        setIsAnalyzing(false);
        return;
      }

      reconnectAttemptsRef.current += 1;
      const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 10000);

      reconnectTimeoutRef.current = setTimeout(() => {
        console.log(`Reconnecting... (attempt ${reconnectAttemptsRef.current})`);
        analyze(query);
      }, delay);
    },
    [autoReconnect, maxReconnectAttempts]
  );

  // Start analysis
  const analyze = useCallback(
    (query: string) => {
      // Close existing connection
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }

      // Reset state
      setState(initialState);
      setError(null);
      setIsAnalyzing(true);
      reconnectAttemptsRef.current = 0;

      // Call onStart callback
      onStart?.();

      // Create EventSource connection
      const url = `${apiUrl}/analyze/stream?query=${encodeURIComponent(query)}`;
      const eventSource = new EventSource(url);
      eventSourceRef.current = eventSource;

      // ======================================================================
      // Event Handlers
      // ======================================================================

      // Helper function to safely parse JSON
      const safeJsonParse = (data: string, eventType: string) => {
        try {
          if (!data || data.trim() === '') {
            console.warn(`Empty data received for event: ${eventType}`);
            return null;
          }
          return JSON.parse(data);
        } catch (err) {
          console.error(`Failed to parse ${eventType} event data:`, data, err);
          return null;
        }
      };

      // START event
      eventSource.addEventListener('start', (event) => {
        const data = safeJsonParse(event.data, 'start');
        if (!data) return;

        setState((prev) => ({
          ...prev,
          query: data.query,
          progress: {
            ...prev.progress,
            stage: 'parsing',
            progressMessages: [...prev.progress.progressMessages, 'Analysis started']
          },
        }));
      });

      // QUERY_PARSED event
      eventSource.addEventListener('query_parsed', (event) => {
        const data = safeJsonParse(event.data, 'query_parsed');
        if (!data) return;

        setState((prev) => ({
          ...prev,
          queryContext: data.query_context,
          progress: {
            ...prev.progress,
            stage: 'analyzing',
            progressMessages: [...prev.progress.progressMessages, `Query parsed: ${data.pair}`]
          },
        }));
      });

      // AGENT_START event (new)
      eventSource.addEventListener('agent_start', (event) => {
        const data = safeJsonParse(event.data, 'agent_start');
        if (!data || !data.agent_start) return;

        const agentName = data.agent_start.agent;
        setState((prev) => ({
          ...prev,
          progress: {
            ...prev.progress,
            currentAgent: agentName,
            progressMessages: [...prev.progress.progressMessages, `${agentName} agent starting...`]
          },
        }));
      });

      // AGENT_PROGRESS event (enhanced with per-agent state tracking)
      eventSource.addEventListener('agent_progress', (event) => {
        const data = safeJsonParse(event.data, 'agent_progress');
        if (!data || !data.agent_progress) return;

        const {
          agent,
          step,
          message,
          progress_percentage,
          intermediate_data,
          execution_start_time,
          execution_end_time,
          execution_time
        } = data.agent_progress;

        setState((prev) => {
          // Only update agent state for known agents (not query_parser)
          const isAgentUpdate = agent === 'news' || agent === 'technical' || agent === 'fundamental';

          if (isAgentUpdate) {
            const agentName = agent as 'news' | 'technical' | 'fundamental';
            const currentAgent = prev.agents[agentName];

            return {
              ...prev,
              agents: {
                ...prev.agents,
                [agentName]: {
                  ...currentAgent,
                  status: progress_percentage === 100 ? 'completed' : 'running',
                  progress: progress_percentage ?? currentAgent.progress,
                  messages: [...currentAgent.messages, message],
                  currentStep: step,
                  startTime: execution_start_time ?? currentAgent.startTime,
                  endTime: execution_end_time ?? currentAgent.endTime,
                  executionTime: execution_time ?? currentAgent.executionTime,
                  intermediateData: intermediate_data ?? currentAgent.intermediateData,
                },
              },
              progress: {
                ...prev.progress,
                currentAgent: agent,
                currentStep: step,
                progressMessages: [...prev.progress.progressMessages, `${agent}: ${message}`],
              },
            };
          }

          // For non-agent updates (like query_parser), just update progress
          return {
            ...prev,
            progress: {
              ...prev.progress,
              currentAgent: agent,
              currentStep: step,
              progressMessages: [...prev.progress.progressMessages, `${agent}: ${message}`],
            },
          };
        });
      });

      // WEB_SEARCH event (new)
      eventSource.addEventListener('web_search', (event) => {
        const data = safeJsonParse(event.data, 'web_search');
        if (!data || !data.web_search) return;

        const { agent, queries, sources } = data.web_search;

        setState((prev) => {
          const agentName = agent as 'news' | 'technical' | 'fundamental';
          const currentAgent = prev.agents[agentName];

          return {
            ...prev,
            agents: {
              ...prev.agents,
              [agentName]: {
                ...currentAgent,
                webSearchQueries: queries,
                webSearchSources: sources,
              },
            },
            progress: {
              ...prev.progress,
              progressMessages: [
                ...prev.progress.progressMessages,
                `${agent}: Found ${sources.length} sources from web search`
              ],
            },
          };
        });
      });

      // AGENT_UPDATE event (enhanced)
      eventSource.addEventListener('agent_update', (event) => {
        const data = safeJsonParse(event.data, 'agent_update');
        if (!data) return;

        const { agent, result } = data;
        const agentName = agent as 'news' | 'technical' | 'fundamental';

        setState((prev) => {
          const agentsCompleted = prev.progress.agentsCompleted + 1;
          const currentAgent = prev.agents[agentName];

          const updates: Partial<AnalysisState> = {
            // Update per-agent state
            agents: {
              ...prev.agents,
              [agentName]: {
                ...currentAgent,
                status: result.success ? 'completed' : 'failed',
                progress: 100,
                result: result,
              },
            },
            progress: {
              ...prev.progress,
              agentsCompleted,
              progressMessages: [...prev.progress.progressMessages, `${agent} agent completed`]
            },
          };

          // Update legacy agent result fields (for backward compatibility)
          if (agent === 'news') updates.newsResult = result;
          else if (agent === 'technical') updates.technicalResult = result;
          else if (agent === 'fundamental') updates.fundamentalResult = result;

          return { ...prev, ...updates };
        });
      });

      // RISK_UPDATE event
      eventSource.addEventListener('risk_update', (event) => {
        const data = safeJsonParse(event.data, 'risk_update');
        if (!data) return;

        setState((prev) => ({
          ...prev,
          riskResult: data.risk_result,
          progress: {
            ...prev.progress,
            stage: data.trade_approved ? 'decision' : 'complete',
            progressMessages: [
              ...prev.progress.progressMessages,
              data.trade_approved ? 'Risk approved' : 'Risk rejected'
            ]
          },
        }));
      });

      // DECISION event
      eventSource.addEventListener('decision', (event) => {
        const data = safeJsonParse(event.data, 'decision');
        if (!data) return;

        setState((prev) => ({
          ...prev,
          decision: data.decision,
          progress: {
            ...prev.progress,
            stage: 'report',
            progressMessages: [
              ...prev.progress.progressMessages,
              `Decision: ${data.decision.action}`
            ]
          },
        }));
      });

      // REPORT_UPDATE event
      eventSource.addEventListener('report_update', (event) => {
        const data = safeJsonParse(event.data, 'report_update');
        if (!data) return;

        setState((prev) => ({
          ...prev,
          reportResult: data.report_result,
          progress: {
            ...prev.progress,
            progressMessages: [
              ...prev.progress.progressMessages,
              data.report_result.success
                ? `Report generated: ${data.report_result.metadata.word_count} words`
                : `Report generation failed: ${data.report_result.error || 'Unknown error'}`
            ]
          },
        }));
      });

      // COMPLETE event
      eventSource.addEventListener('complete', (event) => {
        const data = safeJsonParse(event.data, 'complete');
        if (!data) return;

        setState((prev) => ({
          ...prev,
          finalResult: data.result,
          decision: data.result.decision,
          progress: {
            ...prev.progress,
            stage: 'complete',
            progressMessages: [...prev.progress.progressMessages, 'Analysis complete']
          },
        }));
        setIsAnalyzing(false);
        eventSource.close();
        onComplete?.(data.result);
      });

      // ERROR event
      eventSource.addEventListener('error', (event: MessageEvent) => {
        const data = safeJsonParse(event.data, 'error');
        if (!data) {
          setError('Unknown error occurred');
          setIsAnalyzing(false);
          eventSource.close();
          return;
        }

        const errorMessage = data.error || 'An error occurred during analysis';
        setError(errorMessage);
        setIsAnalyzing(false);
        eventSource.close();
        onError?.(errorMessage);
      });

      // EventSource connection error
      eventSource.onerror = (err) => {
        console.error('EventSource connection error:', err);
        eventSource.close();

        if (isAnalyzing) {
          handleReconnect(query);
        }
      };
    },
    [apiUrl, onStart, onComplete, onError, handleReconnect, isAnalyzing]
  );

  return {
    analyze,
    cancel,
    state,
    isAnalyzing,
    error,
  };
}
