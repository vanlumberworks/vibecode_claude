import { motion } from 'motion/react'
import type { AgentState } from '../hooks/useForexAnalysis'

interface AgentCardProps {
  name: string
  icon: string
  agent: AgentState
}

export function AgentCard({ name, icon, agent }: AgentCardProps) {
  // Status colors
  const statusColors = {
    pending: 'bg-gray-100 text-gray-600 border-gray-200',
    running: 'bg-blue-50 text-blue-700 border-blue-200',
    completed: 'bg-green-50 text-green-700 border-green-200',
    failed: 'bg-red-50 text-red-700 border-red-200',
  }

  const statusLabels = {
    pending: 'Pending',
    running: 'Running',
    completed: 'Completed',
    failed: 'Failed',
  }

  // Format execution time
  const formatTime = (seconds: number | null) => {
    if (!seconds) return null
    return seconds < 1 ? `${(seconds * 1000).toFixed(0)}ms` : `${seconds.toFixed(2)}s`
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className={`relative rounded-lg border-2 p-4 transition-all ${statusColors[agent.status]}`}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-2xl">{icon}</span>
          <h3 className="font-semibold text-lg capitalize">{name}</h3>
        </div>
        <div className="flex items-center gap-2">
          {agent.executionTime && (
            <span className="text-xs font-mono bg-white/50 px-2 py-1 rounded">
              {formatTime(agent.executionTime)}
            </span>
          )}
          <span className={`text-xs px-2 py-1 rounded font-medium ${statusColors[agent.status]}`}>
            {statusLabels[agent.status]}
          </span>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-3">
        <div className="flex justify-between items-center mb-1">
          <span className="text-xs text-gray-600">Progress</span>
          <span className="text-xs font-semibold">{agent.progress}%</span>
        </div>
        <div className="h-2 bg-white/50 rounded-full overflow-hidden">
          <motion.div
            className={`h-full ${
              agent.status === 'completed'
                ? 'bg-green-500'
                : agent.status === 'failed'
                ? 'bg-red-500'
                : 'bg-blue-500'
            }`}
            initial={{ width: 0 }}
            animate={{ width: `${agent.progress}%` }}
            transition={{ duration: 0.3, ease: 'easeOut' }}
          />
        </div>
      </div>

      {/* Running Animation */}
      {agent.status === 'running' && (
        <div className="mb-3 flex items-center gap-2">
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
          <span className="text-xs text-gray-600">{agent.currentStep || 'Processing...'}</span>
        </div>
      )}

      {/* Intermediate Data Preview */}
      {agent.intermediateData && (
        <div className="mb-3 p-2 bg-white/70 rounded border border-gray-200">
          <h4 className="text-xs font-semibold text-gray-700 mb-1">Live Data</h4>
          <div className="text-xs space-y-1">
            {Object.entries(agent.intermediateData).slice(0, 3).map(([key, value]) => (
              <div key={key} className="flex justify-between">
                <span className="text-gray-600 capitalize">{key.replace(/_/g, ' ')}:</span>
                <span className="font-medium">
                  {typeof value === 'number'
                    ? value.toFixed(2)
                    : typeof value === 'object'
                    ? JSON.stringify(value).substring(0, 20) + '...'
                    : String(value)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Web Search Results */}
      {agent.webSearchSources.length > 0 && (
        <div className="mb-3 p-2 bg-white/70 rounded border border-gray-200">
          <h4 className="text-xs font-semibold text-gray-700 mb-1">
            🔎 Web Search ({agent.webSearchSources.length} sources)
          </h4>
          <div className="text-xs space-y-1 max-h-24 overflow-y-auto">
            {agent.webSearchSources.slice(0, 3).map((source, idx) => (
              <a
                key={idx}
                href={source.url}
                target="_blank"
                rel="noopener noreferrer"
                className="block text-blue-600 hover:text-blue-800 hover:underline truncate"
                title={source.title}
              >
                {source.title}
              </a>
            ))}
            {agent.webSearchSources.length > 3 && (
              <span className="text-gray-500">+{agent.webSearchSources.length - 3} more</span>
            )}
          </div>
        </div>
      )}

      {/* Message Log */}
      <div className="p-2 bg-white/70 rounded border border-gray-200">
        <h4 className="text-xs font-semibold text-gray-700 mb-1">Activity Log</h4>
        <div className="text-xs space-y-0.5 max-h-32 overflow-y-auto font-mono">
          {agent.messages.length === 0 ? (
            <div className="text-gray-400 italic">Waiting to start...</div>
          ) : (
            agent.messages.slice(-5).map((msg, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className="text-gray-600 leading-relaxed"
              >
                › {msg}
              </motion.div>
            ))
          )}
        </div>
      </div>

      {/* Final Result Summary */}
      {agent.result && (
        <div className="mt-3 p-2 bg-white/70 rounded border border-gray-200">
          <h4 className="text-xs font-semibold text-gray-700 mb-1">Summary</h4>
          <p className="text-xs text-gray-600">{agent.result.summary || 'No summary available'}</p>
        </div>
      )}
    </motion.div>
  )
}
