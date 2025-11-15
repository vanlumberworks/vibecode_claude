import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { Toaster, toast } from 'sonner'
import { useForexAnalysis } from './hooks/useForexAnalysis'
import { ChatInterface } from './components/ChatInterface'
import { ReasoningTimeline } from './components/ReasoningTimeline'
import { ComprehensiveReport } from './components/ComprehensiveReport'
import { Card, CardContent } from './components/ui/card'

type ViewMode = 'chat' | 'timeline' | 'report'

function App() {
  const [viewMode, setViewMode] = useState<ViewMode>('chat')
  const [currentQuery, setCurrentQuery] = useState('')

  const { analyze, state, isAnalyzing, error } = useForexAnalysis({
    apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  })

  // Automatically switch views based on analysis state
  useEffect(() => {
    if (isAnalyzing || state.progress.progressMessages.length > 0) {
      setViewMode('timeline')
    } else if (state.finalResult && !isAnalyzing) {
      // Add a small delay before showing the report
      const timer = setTimeout(() => {
        setViewMode('report')
      }, 300)
      return () => clearTimeout(timer)
    }
  }, [isAnalyzing, state.finalResult, state.progress.progressMessages.length])

  // Show toast notification when report is ready
  useEffect(() => {
    if (state.reportResult?.success && !isAnalyzing) {
      toast.success('Analysis Complete!', {
        description: 'Your comprehensive report is ready to view',
        duration: 5000,
      })
    }
  }, [state.reportResult?.success, isAnalyzing])

  const handleAnalyze = (query: string) => {
    setCurrentQuery(query)
    setViewMode('timeline')
    analyze(query)
  }

  const handleNewAnalysis = () => {
    setViewMode('chat')
    setCurrentQuery('')
  }

  const handleViewReport = () => {
    setViewMode('report')
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Toast Notifications */}
      <Toaster position="top-right" />

      {/* Error Toast */}
      <AnimatePresence>
        {error && (
          <motion.div
            className="fixed top-8 right-8 z-50 max-w-md"
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 50 }}
            transition={{ duration: 0.3 }}
          >
            <Card className="border-destructive">
              <CardContent className="p-6">
                <div className="flex items-start gap-3">
                  <span className="text-2xl">⚠️</span>
                  <div className="flex-1">
                    <h3 className="font-semibold text-destructive mb-1">
                      Analysis Error
                    </h3>
                    <p className="text-sm text-muted-foreground">
                      {error}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* View Switcher with Transitions */}
      <AnimatePresence mode="wait">
        {viewMode === 'chat' && (
          <motion.div
            key="chat"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            <ChatInterface onSubmit={handleAnalyze} isAnalyzing={isAnalyzing} />
          </motion.div>
        )}

        {viewMode === 'timeline' && (
          <motion.div
            key="timeline"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            <ReasoningTimeline
              state={state}
              isAnalyzing={isAnalyzing}
              query={currentQuery}
              onViewReport={handleViewReport}
            />
          </motion.div>
        )}

        {viewMode === 'report' && (
          <motion.div
            key="report"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            <ComprehensiveReport
              state={state}
              onNewAnalysis={handleNewAnalysis}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default App
