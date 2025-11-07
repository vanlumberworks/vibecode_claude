import { useState } from 'react'

function App() {
  const [query, setQuery] = useState('')

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <header className="text-center mb-8">
            <h1 className="text-5xl font-bold text-white mb-2">
              🌍 Forex Agent System
            </h1>
            <p className="text-white/90 text-lg">
              Real-time Multi-Agent Trading Analysis with LangGraph
            </p>
          </header>

          {/* Main Chat Interface */}
          <div className="bg-white rounded-2xl shadow-2xl overflow-hidden">
            <div className="p-6">
              <h2 className="text-2xl font-semibold mb-4 text-gray-800">
                Analysis Chat
              </h2>

              {/* Placeholder for chat messages */}
              <div className="bg-gray-50 rounded-lg p-4 mb-4 min-h-[400px]">
                <p className="text-gray-500 text-center mt-32">
                  Enter a query below to start analysis...
                </p>
              </div>

              {/* Input Form */}
              <div className="flex gap-2">
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Enter query (e.g., 'Analyze gold trading', 'EUR/USD')"
                  className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
                <button
                  onClick={() => console.log('Analyze:', query)}
                  className="px-6 py-3 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition-colors"
                >
                  Analyze
                </button>
              </div>
            </div>
          </div>

          {/* Info Footer */}
          <div className="mt-6 text-center text-white/80 text-sm">
            <p>
              Backend API: <code className="bg-white/20 px-2 py-1 rounded">http://localhost:8000</code>
            </p>
            <p className="mt-2">
              Ready to stream real-time analysis from LangGraph + Gemini
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
