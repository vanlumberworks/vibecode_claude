/**
 * SocialMediaShare Component
 *
 * Provides UI for sharing trading analysis on social media platforms.
 * Features:
 * - Preview formatted posts before sharing
 * - Copy to clipboard functionality
 * - Support for Twitter, Telegram, and Facebook
 * - Conditional trade parameters (only for BUY/SELL signals)
 */

import { useState } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { toast } from 'sonner'
import type { AnalysisResult } from '../types/forex-api'

interface SocialMediaShareProps {
  result: AnalysisResult
  apiUrl?: string
}

type Platform = 'twitter' | 'telegram' | 'facebook'

interface FormattedPost {
  post: string
  charCount: number
  isSignal: boolean
}

export function SocialMediaShare({ result, apiUrl = 'http://localhost:8000' }: SocialMediaShareProps) {
  const [selectedPlatform, setSelectedPlatform] = useState<Platform | null>(null)
  const [formattedPost, setFormattedPost] = useState<string>('')
  const [isLoading, setIsLoading] = useState(false)
  const [charCount, setCharCount] = useState(0)
  const [isSignal, setIsSignal] = useState(false)

  const platformConfig = {
    twitter: {
      name: 'Twitter',
      icon: '𝕏',
      color: 'from-blue-500 to-blue-600',
      bgColor: 'bg-blue-500/10',
      borderColor: 'border-blue-500/30',
      glowColor: 'shadow-blue-500/20',
    },
    telegram: {
      name: 'Telegram',
      icon: '✈️',
      color: 'from-cyan-500 to-blue-500',
      bgColor: 'bg-cyan-500/10',
      borderColor: 'border-cyan-500/30',
      glowColor: 'shadow-cyan-500/20',
    },
    facebook: {
      name: 'Facebook',
      icon: 'f',
      color: 'from-blue-600 to-indigo-600',
      bgColor: 'bg-indigo-500/10',
      borderColor: 'border-indigo-500/30',
      glowColor: 'shadow-indigo-500/20',
    },
  }

  const formatPost = async (platform: Platform) => {
    setIsLoading(true)
    setSelectedPlatform(platform)

    try {
      const response = await fetch(`${apiUrl}/api/format-social`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          result: result,
          platform: platform,
          include_trade_params: true,
        }),
      })

      if (!response.ok) {
        throw new Error(`Failed to format post: ${response.statusText}`)
      }

      const data: FormattedPost = await response.json()
      setFormattedPost(data.post)
      setCharCount(data.charCount)
      setIsSignal(data.isSignal)

      toast.success('Post formatted!', {
        description: `Ready to share on ${platformConfig[platform].name}`,
      })
    } catch (error) {
      console.error('Error formatting post:', error)
      toast.error('Failed to format post', {
        description: error instanceof Error ? error.message : 'Unknown error',
      })
    } finally {
      setIsLoading(false)
    }
  }

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(formattedPost)
      toast.success('Copied to clipboard!', {
        description: 'You can now paste it anywhere',
      })
    } catch (error) {
      toast.error('Failed to copy', {
        description: 'Please copy the text manually',
      })
    }
  }

  const closeModal = () => {
    setSelectedPlatform(null)
    setFormattedPost('')
  }

  return (
    <div className="space-y-4">
      {/* Share Buttons */}
      <div className="flex items-center gap-2">
        <span className="text-sm text-[hsl(var(--text-secondary))] font-medium">
          Share on:
        </span>
        <div className="flex gap-2">
          {(Object.keys(platformConfig) as Platform[]).map((platform) => {
            const config = platformConfig[platform]
            return (
              <button
                key={platform}
                onClick={() => formatPost(platform)}
                disabled={isLoading}
                className={`
                  px-4 py-2 rounded-lg border
                  ${config.bgColor} ${config.borderColor}
                  hover:${config.glowColor} hover:shadow-lg
                  transition-all duration-200
                  disabled:opacity-50 disabled:cursor-not-allowed
                  flex items-center gap-2
                  text-sm font-medium
                `}
              >
                <span className="text-lg">{config.icon}</span>
                <span>{config.name}</span>
              </button>
            )
          })}
        </div>
      </div>

      {/* Preview Modal */}
      <AnimatePresence>
        {selectedPlatform && formattedPost && (
          <motion.div
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={closeModal}
          >
            <motion.div
              className="glass rounded-2xl p-6 max-w-2xl w-full border-2 border-[hsl(var(--gold)/0.3)] glow-gold"
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.9, y: 20 }}
              onClick={(e) => e.stopPropagation()}
            >
              {/* Header */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <span className="text-3xl">
                    {platformConfig[selectedPlatform].icon}
                  </span>
                  <div>
                    <h3 className="text-xl font-bold">
                      {platformConfig[selectedPlatform].name} Post
                    </h3>
                    {selectedPlatform === 'twitter' && (
                      <p className="text-sm text-[hsl(var(--text-secondary))]">
                        {charCount}/280 characters
                      </p>
                    )}
                  </div>
                </div>
                <button
                  onClick={closeModal}
                  className="text-2xl hover:text-[hsl(var(--gold))] transition-colors"
                >
                  ×
                </button>
              </div>

              {/* Signal Badge */}
              {isSignal && (
                <div className="mb-4 inline-flex items-center gap-2 px-3 py-1 rounded-lg bg-[hsl(var(--gold)/0.1)] border border-[hsl(var(--gold)/0.3)]">
                  <span className="text-[hsl(var(--gold))]">📊</span>
                  <span className="text-sm font-medium text-[hsl(var(--gold))]">
                    Trading Signal
                  </span>
                </div>
              )}

              {/* Post Preview */}
              <div className="mb-6 p-4 rounded-lg bg-black/30 border border-white/10">
                <pre className="whitespace-pre-wrap font-mono text-sm text-[hsl(var(--text-primary))]">
                  {formattedPost}
                </pre>
              </div>

              {/* Actions */}
              <div className="flex gap-3">
                <button
                  onClick={copyToClipboard}
                  className="flex-1 px-4 py-3 rounded-lg bg-gradient-to-r from-[hsl(var(--gold))] to-[hsl(var(--gold-bright))] text-black font-semibold hover:shadow-lg hover:shadow-[hsl(var(--gold)/0.3)] transition-all duration-200"
                >
                  📋 Copy to Clipboard
                </button>
                <button
                  onClick={closeModal}
                  className="px-4 py-3 rounded-lg border border-white/10 hover:border-white/20 transition-colors"
                >
                  Close
                </button>
              </div>

              {/* Helper Text */}
              <p className="mt-4 text-xs text-[hsl(var(--text-secondary))] text-center">
                Review the post above, then copy and paste it to{' '}
                {platformConfig[selectedPlatform].name}
              </p>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Loading Overlay */}
      {isLoading && (
        <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/50 backdrop-blur-sm">
          <div className="glass rounded-xl p-6 border border-[hsl(var(--gold)/0.3)]">
            <div className="flex items-center gap-3">
              <div className="animate-spin rounded-full h-6 w-6 border-2 border-[hsl(var(--gold))] border-t-transparent"></div>
              <span className="text-sm font-medium">Formatting post...</span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
