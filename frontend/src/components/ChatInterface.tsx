import { useState } from 'react'
import { motion } from 'motion/react'

interface ChatInterfaceProps {
  onSubmit: (query: string) => void
  isAnalyzing: boolean
}

const SUGGESTED_PROMPTS = [
  {
    icon: '💱',
    title: 'EUR/USD Analysis',
    query: 'Analyze EUR/USD trading opportunity',
    category: 'Forex'
  },
  {
    icon: '🥇',
    title: 'Gold Trading',
    query: 'Should I buy gold right now?',
    category: 'Commodity'
  },
  {
    icon: '₿',
    title: 'Bitcoin Setup',
    query: 'What\'s the technical setup for Bitcoin?',
    category: 'Crypto'
  },
  {
    icon: '🛢️',
    title: 'Oil Markets',
    query: 'Analyze crude oil trading outlook',
    category: 'Commodity'
  },
  {
    icon: '💷',
    title: 'GBP/JPY',
    query: 'GBP/JPY swing trade analysis',
    category: 'Forex'
  },
  {
    icon: '⚡',
    title: 'Quick Scalp',
    query: 'EUR/GBP scalping opportunity',
    category: 'Forex'
  }
]

export function ChatInterface({ onSubmit, isAnalyzing }: ChatInterfaceProps) {
  const [query, setQuery] = useState('')
  const [isFocused, setIsFocused] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim() && !isAnalyzing) {
      onSubmit(query.trim())
    }
  }

  const handleSuggestedPrompt = (promptQuery: string) => {
    if (!isAnalyzing) {
      setQuery(promptQuery)
      onSubmit(promptQuery)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden bg-black">
      {/* Animated Grid Background */}
      <div className="absolute inset-0 animated-grid opacity-30" />

      {/* Scanline Effect */}
      <div className="absolute inset-0 scanline pointer-events-none opacity-50" />

      {/* Main Content */}
      <div className="relative z-10 w-full max-w-4xl px-6">
        {/* Header */}
        <motion.div
          className="text-center mb-12"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <h1 className="text-7xl font-bold mb-4 text-glow-gold">
            <span className="bg-gradient-to-r from-[#f59e0b] via-[#fbbf24] to-[#f59e0b] bg-clip-text text-transparent">
              FOREX TERMINAL
            </span>
          </h1>
          <p className="text-xl text-[hsl(var(--text-secondary))] font-mono">
            AI-Powered Multi-Agent Trading Analysis System
          </p>
        </motion.div>

        {/* Search Box */}
        <motion.form
          onSubmit={handleSubmit}
          className="mb-12"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          <div
            className={`glass rounded-2xl p-2 transition-all duration-300 ${
              isFocused ? 'glow-gold' : ''
            }`}
          >
            <div className="flex items-center gap-3 px-4 py-3">
              <span className="text-2xl">🔍</span>
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onFocus={() => setIsFocused(true)}
                onBlur={() => setIsFocused(false)}
                placeholder="Enter trading query... (e.g., 'Analyze EUR/USD', 'Should I buy Bitcoin?')"
                className="flex-1 bg-transparent border-none outline-none text-lg placeholder:text-[hsl(var(--text-muted))] font-light"
                disabled={isAnalyzing}
              />
              <button
                type="submit"
                disabled={!query.trim() || isAnalyzing}
                className={`px-6 py-2.5 rounded-xl font-medium transition-all duration-300 ${
                  query.trim() && !isAnalyzing
                    ? 'bg-gradient-to-r from-[#f59e0b] to-[#fbbf24] text-[hsl(var(--bg-primary))] hover:glow-gold'
                    : 'bg-[hsl(var(--bg-tertiary))] text-[hsl(var(--text-muted))] cursor-not-allowed'
                }`}
              >
                {isAnalyzing ? (
                  <span className="flex items-center gap-2">
                    <span className="inline-block w-4 h-4 border-2 border-t-transparent border-white rounded-full animate-spin" />
                    Analyzing
                  </span>
                ) : (
                  'Analyze'
                )}
              </button>
            </div>
          </div>
        </motion.form>

        {/* Suggested Prompts */}
        {!isAnalyzing && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            <div className="text-center mb-6">
              <p className="text-sm text-[hsl(var(--text-secondary))] font-mono uppercase tracking-wider">
                Try these popular queries
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {SUGGESTED_PROMPTS.map((prompt, index) => (
                <motion.button
                  key={index}
                  onClick={() => handleSuggestedPrompt(prompt.query)}
                  className="glass rounded-xl p-5 text-left hover:glow-gold transition-all duration-300 group"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: 0.5 + index * 0.1 }}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <div className="flex items-start gap-3">
                    <div className="text-3xl">{prompt.icon}</div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-semibold text-[hsl(var(--text-primary))] group-hover:text-[#f59e0b] transition-colors">
                          {prompt.title}
                        </h3>
                        <span className="text-xs px-2 py-0.5 rounded-full bg-[hsl(var(--bg-tertiary))] text-[hsl(var(--text-secondary))] font-mono">
                          {prompt.category}
                        </span>
                      </div>
                      <p className="text-sm text-[hsl(var(--text-secondary))] font-light">
                        {prompt.query}
                      </p>
                    </div>
                  </div>
                </motion.button>
              ))}
            </div>
          </motion.div>
        )}

        {/* Footer Info */}
        <motion.div
          className="mt-16 text-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 1 }}
        >
          <div className="inline-flex items-center gap-2 glass px-4 py-2 rounded-full">
            <div className="w-2 h-2 rounded-full bg-[#10b981] animate-pulse" />
            <span className="text-sm text-[hsl(var(--text-secondary))] font-mono">
              API Connected • LangGraph + Gemini 2.5 Flash
            </span>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
