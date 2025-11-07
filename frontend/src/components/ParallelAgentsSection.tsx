import { motion } from 'motion/react'
import { AgentCard } from './AgentCard'
import type { AnalysisState } from '../hooks/useForexAnalysis'

interface ParallelAgentsSectionProps {
  state: AnalysisState
}

export function ParallelAgentsSection({ state }: ParallelAgentsSectionProps) {
  const { agents, progress } = state

  // Check if any agent is active or completed
  const hasActivity =
    agents.news.status !== 'pending' ||
    agents.technical.status !== 'pending' ||
    agents.fundamental.status !== 'pending'

  // Don't show section if no activity yet
  if (!hasActivity && progress.stage === 'idle') {
    return null
  }

  // Calculate overall progress
  const overallProgress = Math.round((agents.news.progress + agents.technical.progress + agents.fundamental.progress) / 3)

  // Count completed agents
  const completedCount = [agents.news, agents.technical, agents.fundamental].filter(
    (a) => a.status === 'completed'
  ).length

  // Count running agents
  const runningCount = [agents.news, agents.technical, agents.fundamental].filter(
    (a) => a.status === 'running'
  ).length

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="mb-8"
    >
      {/* Section Header */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-xl font-bold text-gray-800 flex items-center gap-2">
            <span>⚡</span>
            <span>Parallel Agent Analysis</span>
          </h2>
          <div className="flex items-center gap-3">
            {runningCount > 0 && (
              <div className="flex items-center gap-2 text-blue-600">
                <div className="flex gap-1">
                  <motion.div
                    className="w-2 h-2 bg-blue-500 rounded-full"
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ duration: 1, repeat: Infinity, delay: 0 }}
                  />
                  <motion.div
                    className="w-2 h-2 bg-blue-500 rounded-full"
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ duration: 1, repeat: Infinity, delay: 0.2 }}
                  />
                  <motion.div
                    className="w-2 h-2 bg-blue-500 rounded-full"
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ duration: 1, repeat: Infinity, delay: 0.4 }}
                  />
                </div>
                <span className="text-sm font-medium">{runningCount} Running</span>
              </div>
            )}
            <span className="text-sm font-semibold text-gray-700">
              {completedCount} / 3 Completed
            </span>
          </div>
        </div>

        {/* Overall Progress Bar */}
        <div className="mb-2">
          <div className="flex justify-between items-center mb-1">
            <span className="text-xs text-gray-600">Overall Progress</span>
            <span className="text-xs font-semibold">{overallProgress}%</span>
          </div>
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500"
              initial={{ width: 0 }}
              animate={{ width: `${overallProgress}%` }}
              transition={{ duration: 0.5, ease: 'easeOut' }}
            />
          </div>
        </div>

        <p className="text-sm text-gray-600">
          All three agents (News, Technical, Fundamental) are running simultaneously for maximum speed.
        </p>
      </div>

      {/* Agent Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <AgentCard name="news" icon="📰" agent={agents.news} />
        <AgentCard name="technical" icon="📊" agent={agents.technical} />
        <AgentCard name="fundamental" icon="💼" agent={agents.fundamental} />
      </div>

      {/* Performance Insight */}
      {completedCount === 3 && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg"
        >
          <div className="flex items-start gap-2">
            <span className="text-green-600 text-xl">✓</span>
            <div>
              <h4 className="font-semibold text-green-800 text-sm mb-1">
                Parallel Execution Complete
              </h4>
              <p className="text-xs text-green-700">
                All agents finished in parallel. Total execution time:{' '}
                {Math.max(
                  agents.news.executionTime || 0,
                  agents.technical.executionTime || 0,
                  agents.fundamental.executionTime || 0
                ).toFixed(2)}
                s (vs. ~
                {(
                  (agents.news.executionTime || 0) +
                  (agents.technical.executionTime || 0) +
                  (agents.fundamental.executionTime || 0)
                ).toFixed(2)}
                s if sequential) -
                <strong className="ml-1">
                  {(
                    ((agents.news.executionTime || 0) +
                      (agents.technical.executionTime || 0) +
                      (agents.fundamental.executionTime || 0)) /
                    Math.max(
                      agents.news.executionTime || 1,
                      agents.technical.executionTime || 1,
                      agents.fundamental.executionTime || 1
                    )
                  ).toFixed(1)}
                  x faster!
                </strong>
              </p>
            </div>
          </div>
        </motion.div>
      )}
    </motion.div>
  )
}
