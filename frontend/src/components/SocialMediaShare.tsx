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
import { Copy, Loader2 } from 'lucide-react'
import { toast } from 'sonner'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from './ui/dialog'
import { Button } from './ui/button'
import { Badge } from './ui/badge'
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
  const [isOpen, setIsOpen] = useState(false)

  const platformConfig = {
    twitter: {
      name: 'Twitter',
      icon: '𝕏',
    },
    telegram: {
      name: 'Telegram',
      icon: '✈️',
    },
    facebook: {
      name: 'Facebook',
      icon: 'f',
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
      setIsOpen(true)

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
    setIsOpen(false)
    setSelectedPlatform(null)
    setFormattedPost('')
  }

  return (
    <>
      {/* Share Buttons */}
      <div className="space-y-3">
        <p className="text-sm text-muted-foreground">
          Share on:
        </p>
        <div className="grid grid-cols-3 gap-2">
          {(Object.keys(platformConfig) as Platform[]).map((platform) => {
            const config = platformConfig[platform]
            return (
              <Button
                key={platform}
                variant="outline"
                onClick={() => formatPost(platform)}
                disabled={isLoading}
                className="flex items-center justify-center gap-2"
                size="sm"
              >
                <span className="text-lg">{config.icon}</span>
                <span className="text-xs">{config.name}</span>
              </Button>
            )
          })}
        </div>
      </div>

      {/* Preview Dialog */}
      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-3">
              <span className="text-2xl">
                {selectedPlatform && platformConfig[selectedPlatform].icon}
              </span>
              <span>{selectedPlatform && platformConfig[selectedPlatform].name} Post</span>
            </DialogTitle>
            {selectedPlatform === 'twitter' && (
              <DialogDescription>
                {charCount}/280 characters
              </DialogDescription>
            )}
          </DialogHeader>

          {/* Signal Badge */}
          {isSignal && (
            <Badge variant="secondary" className="w-fit">
              <span className="mr-2">📊</span>
              Trading Signal
            </Badge>
          )}

          {/* Post Preview */}
          <div className="p-4 rounded-lg bg-muted border">
            <pre className="whitespace-pre-wrap font-mono text-sm">
              {formattedPost}
            </pre>
          </div>

          {/* Actions */}
          <div className="flex gap-3">
            <Button
              onClick={copyToClipboard}
              className="flex-1"
            >
              <Copy className="w-4 h-4 mr-2" />
              Copy to Clipboard
            </Button>
            <Button
              variant="outline"
              onClick={closeModal}
            >
              Close
            </Button>
          </div>

          {/* Helper Text */}
          <p className="text-xs text-muted-foreground text-center">
            Review the post above, then copy and paste it to{' '}
            {selectedPlatform && platformConfig[selectedPlatform].name}
          </p>
        </DialogContent>
      </Dialog>

      {/* Loading Overlay */}
      {isLoading && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm">
          <div className="flex items-center gap-3 p-6 rounded-lg border bg-card">
            <Loader2 className="w-6 h-6 animate-spin" />
            <span className="text-sm font-medium">Formatting post...</span>
          </div>
        </div>
      )}
    </>
  )
}
