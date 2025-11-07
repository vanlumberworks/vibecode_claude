# Frontend Integration Guide: Streaming Agent System

Complete guide for integrating the LangGraph multi-agent forex analysis system with a Vite.js + JavaScript frontend.

## Table of Contents
1. [Overview](#overview)
2. [API Endpoints](#api-endpoints)
3. [Event Types](#event-types)
4. [JavaScript Integration](#javascript-integration)
5. [React/Vue Component Examples](#react-vue-examples)
6. [UI/UX Best Practices](#ui-ux-best-practices)
7. [Error Handling](#error-handling)
8. [Complete Example](#complete-example)

---

## Overview

The backend streams real-time updates using **Server-Sent Events (SSE)**. Each stage of the analysis emits events that your frontend can capture and display to users.

### Architecture
```
User Query → Backend API → LangGraph Workflow → SSE Stream → Frontend
                                    ↓
                    Query Parser → Parallel Agents → Risk → Synthesis
                         ↓              ↓              ↓        ↓
                    Progress Events  Progress Events  etc...  Final Decision
```

---

## API Endpoints

### Base URL
```
http://localhost:8000
```

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "api_configured": true
}
```

### Streaming Analysis (Primary Endpoint)
```http
POST /analyze/stream
Content-Type: application/json

{
  "query": "Analyze EUR/USD",
  "account_balance": 10000.0,     // optional
  "max_risk_per_trade": 0.02      // optional
}
```

**Alternative (GET for testing):**
```http
GET /analyze/stream?query=Analyze+EUR/USD
```

---

## Event Types

The SSE stream emits the following event types:

### 1. `start` - Analysis Started
Emitted immediately when the analysis begins.

```javascript
{
  type: "start",
  data: {
    query: "Analyze EUR/USD",
    timestamp: "2025-11-07T04:08:29.635201Z"
  }
}
```

### 2. `agent_progress` - Real-time Progress Updates
Emitted throughout the workflow to show what's happening.

```javascript
{
  type: "agent_progress",
  data: {
    agent_progress: {
      agent: "query_parser" | "news" | "technical" | "fundamental" | "synthesis",
      step: string,           // e.g., "parsing", "google_search", "fetching_price"
      message: string,        // Human-readable message
      data?: object          // Optional additional data (e.g., price info)
    }
  }
}
```

**Examples by Agent:**

**Query Parser:**
```javascript
{ agent: "query_parser", step: "parsing", message: "Parsing query: 'Analyze EUR/USD'" }
```

**News Agent:**
```javascript
{ agent: "news", step: "initializing_api", message: "Initializing Gemini API" }
{ agent: "news", step: "building_prompt", message: "Building search prompt for EUR/USD" }
{ agent: "news", step: "google_search", message: "Searching web for EUR/USD news and sentiment" }
{ agent: "news", step: "processing_results", message: "Processing search results and analyzing sentiment" }
```

**Technical Agent:**
```javascript
{ agent: "technical", step: "fetching_price", message: "Fetching real-time price for EUR/USD" }
{ agent: "technical", step: "price_fetched", message: "Price fetched: $1.14952", data: { price: 1.14952, source: "real" } }
{ agent: "technical", step: "llm_analysis", message: "Analyzing technical patterns with Gemini LLM" }
```

**Fundamental Agent:**
```javascript
{ agent: "fundamental", step: "initializing", message: "Starting fundamental analysis for EUR/USD" }
{ agent: "fundamental", step: "google_search", message: "Searching for economic data and fundamentals" }
```

**Synthesis Agent:**
```javascript
{ agent: "synthesis", step: "collecting_data", message: "Collecting all agent results" }
{ agent: "synthesis", step: "building_synthesis", message: "Building comprehensive analysis" }
{ agent: "synthesis", step: "google_search", message: "Searching web for real-time market verification" }
{ agent: "synthesis", step: "processing_decision", message: "Processing final trading decision" }
```

### 3. `agent_start` - Agent Started
Emitted when an agent begins execution.

```javascript
{
  type: "agent_start",
  data: {
    agent_start: {
      agent: "news" | "technical" | "fundamental",
      pair: "EUR/USD",
      status: "starting"
    }
  }
}
```

### 4. `query_parsed` - Query Parsing Complete
Emitted after the natural language query is parsed into structured context.

```javascript
{
  type: "query_parsed",
  data: {
    step: 1,
    query_context: {
      pair: "EUR/USD",
      asset_type: "forex",
      base_currency: "EUR",
      quote_currency: "USD",
      timeframe: "short_term",
      user_intent: "trading_signal",
      risk_tolerance: "moderate",
      additional_context: {
        keywords: ["EUR/USD"],
        mentioned_indicators: [],
        mentioned_events: [],
        price_levels: []
      },
      confidence: 0.95
    },
    pair: "EUR/USD",
    timestamp: "2025-11-07T04:08:33.466216Z"
  }
}
```

### 5. `agent_update` - Agent Completed
Emitted when an individual agent completes its analysis.

```javascript
{
  type: "agent_update",
  data: {
    step: 2,
    agent: "news" | "technical" | "fundamental",
    result: {
      success: true,
      agent: "NewsAgent",
      data: {
        // Agent-specific results (see below)
      }
    },
    timestamp: "2025-11-07T04:09:06.566033Z"
  }
}
```

**News Agent Result:**
```javascript
{
  pair: "EUR/USD",
  headlines: [
    {
      title: "EUR/USD extends rebound as US Dollar retreats",
      date: "2025-11-06",
      sentiment: "bullish",
      source: "FXstreet"
    },
    // ... more headlines
  ],
  sentiment_score: 0.1,        // -1.0 (bearish) to +1.0 (bullish)
  sentiment: "neutral",         // "bullish", "bearish", or "neutral"
  impact: "high",              // "high", "medium", or "low"
  news_count: 5,
  summary: "Market sentiment is currently neutral...",
  key_events: [
    "US Dollar Retreats on Jobs Data Concerns (November 6, 2025)",
    // ... more events
  ],
  search_queries: ["EUR/USD forex news last 48 hours", ...],
  sources: [
    { title: "FXstreet", url: "https://..." },
    // ... more sources
  ]
}
```

**Technical Agent Result:**
```javascript
{
  pair: "EUR/USD",
  current_price: 1.14952,
  price_source: "real",        // "real" or "mock"
  trend: "uptrend",            // "uptrend", "downtrend", "sideways"
  trend_strength: "medium",    // "strong", "medium", "weak"
  support: 1.147,
  resistance: 1.154,
  indicators: {
    rsi: 44.12,
    macd: "bullish",
    ma_position: "below_50ma",
    momentum: "decreasing"
  },
  signals: {
    buy: "weak",               // "strong", "moderate", "weak", "none"
    sell: "weak",
    overall: "HOLD",           // "BUY", "SELL", "HOLD"
    confidence: 0.5
  },
  stop_loss: 1.145,
  take_profit: 1.156,
  key_levels: [
    "1.1470 - Recent support",
    "1.1495 - Current price",
    // ... more levels
  ],
  analysis: "EUR/USD is currently exhibiting...",
  summary: "EUR/USD is in a consolidative phase..."
}
```

**Fundamental Agent Result:**
```javascript
{
  pair: "EUR/USD",
  base_currency: {
    currency: "EUR",
    gdp_growth: "0.4% q/q",
    inflation: "2.0%",
    interest_rate: "3.00%",
    unemployment: "6.3%",
    // ... more economic data
  },
  quote_currency: {
    currency: "USD",
    gdp_growth: "2.8%",
    // ... more economic data
  },
  fundamental_score: -0.2,    // -1.0 to +1.0
  outlook: "neutral",          // "bullish", "bearish", "neutral"
  key_factors: [
    "Interest rate differential favors USD",
    // ... more factors
  ],
  analysis: "The fundamental analysis presents...",
  summary: "The EUR/USD pair is influenced by..."
}
```

### 6. `risk_update` - Risk Assessment Complete
Emitted after risk calculations are completed.

```javascript
{
  type: "risk_update",
  data: {
    step: 3,
    risk_result: {
      success: true,
      data: {
        pair: "EUR/USD",
        direction: "BUY",
        entry_price: 1.14952,
        stop_loss: 1.145,
        take_profit: 1.156,
        risk_in_pips: 44.52,
        position_size: 0.45,
        dollar_risk: 200.0,
        risk_percentage: 2.0,
        risk_reward_ratio: 1.47,
        trade_approved: false,
        rejection_reason: "Poor risk/reward ratio: 1.47 is below minimum of 1.5",
        summary: "Trade REJECTED: Poor risk/reward ratio..."
      }
    },
    trade_approved: false,
    timestamp: "2025-11-07T04:09:07.123456Z"
  }
}
```

### 7. `decision` - Final Trading Decision
Emitted when synthesis completes (only if risk approved).

```javascript
{
  type: "decision",
  data: {
    step: 4,
    decision: {
      action: "BUY" | "SELL" | "WAIT",
      confidence: 0.75,         // 0.0 to 1.0
      reasoning: {
        summary: "One paragraph summary...",
        web_verification: "Real-time data confirmed...",
        key_factors: [
          "Factor 1",
          "Factor 2",
          // ...
        ],
        risks: ["Risk 1", "Risk 2"]
      },
      trade_parameters: {
        entry_price: 1.14952,
        stop_loss: 1.145,
        take_profit: 1.156,
        position_size: 0.45
      },
      grounding_metadata: {
        search_queries: ["EUR/USD latest news", ...],
        sources: [
          { title: "Source", url: "https://..." }
        ]
      }
    },
    timestamp: "2025-11-07T04:09:10.123456Z"
  }
}
```

### 8. `complete` - Analysis Complete
Final event with full aggregated results.

```javascript
{
  type: "complete",
  data: {
    result: {
      query_context: { /* parsed query */ },
      news_result: { /* full news data */ },
      technical_result: { /* full technical data */ },
      fundamental_result: { /* full fundamental data */ },
      risk_result: { /* full risk data */ },
      decision: { /* final decision */ },
      metadata: {
        total_time_seconds: 15.3,
        step_count: 4
      }
    },
    timestamp: "2025-11-07T04:09:10.500000Z"
  }
}
```

### 9. `error` - Error Occurred
Emitted if an error occurs during analysis.

```javascript
{
  type: "error",
  data: {
    error: "Error message here",
    error_type: "ValueError",
    timestamp: "2025-11-07T04:09:10.123456Z"
  }
}
```

---

## JavaScript Integration

### Basic EventSource Implementation

```javascript
// utils/forexApi.js

const API_BASE_URL = 'http://localhost:8000';

/**
 * Start a streaming analysis
 * @param {string} query - Trading query (e.g., "Analyze EUR/USD")
 * @param {Object} callbacks - Event handlers
 * @param {Object} options - Optional parameters
 */
export function startStreamingAnalysis(query, callbacks, options = {}) {
  const {
    onStart,
    onAgentProgress,
    onAgentStart,
    onQueryParsed,
    onAgentUpdate,
    onRiskUpdate,
    onDecision,
    onComplete,
    onError
  } = callbacks;

  // Build request body
  const body = {
    query,
    ...(options.accountBalance && { account_balance: options.accountBalance }),
    ...(options.maxRiskPerTrade && { max_risk_per_trade: options.maxRiskPerTrade })
  };

  // Create EventSource connection
  // Note: For POST data, we need to use fetch with streaming
  // EventSource only supports GET

  // Option 1: Use GET for simple queries
  if (!options.accountBalance && !options.maxRiskPerTrade) {
    const url = `${API_BASE_URL}/analyze/stream?query=${encodeURIComponent(query)}`;
    const eventSource = new EventSource(url);

    // Register event listeners
    eventSource.addEventListener('start', (e) => {
      const data = JSON.parse(e.data);
      onStart?.(data);
    });

    eventSource.addEventListener('agent_progress', (e) => {
      const data = JSON.parse(e.data);
      onAgentProgress?.(data.agent_progress);
    });

    eventSource.addEventListener('agent_start', (e) => {
      const data = JSON.parse(e.data);
      onAgentStart?.(data.agent_start);
    });

    eventSource.addEventListener('query_parsed', (e) => {
      const data = JSON.parse(e.data);
      onQueryParsed?.(data);
    });

    eventSource.addEventListener('agent_update', (e) => {
      const data = JSON.parse(e.data);
      onAgentUpdate?.(data);
    });

    eventSource.addEventListener('risk_update', (e) => {
      const data = JSON.parse(e.data);
      onRiskUpdate?.(data);
    });

    eventSource.addEventListener('decision', (e) => {
      const data = JSON.parse(e.data);
      onDecision?.(data);
    });

    eventSource.addEventListener('complete', (e) => {
      const data = JSON.parse(e.data);
      onComplete?.(data);
      eventSource.close();
    });

    eventSource.addEventListener('error', (e) => {
      const data = e.data ? JSON.parse(e.data) : { error: 'Connection error' };
      onError?.(data);
      eventSource.close();
    });

    eventSource.onerror = (err) => {
      console.error('EventSource error:', err);
      onError?.({ error: 'Stream connection failed' });
      eventSource.close();
    };

    return eventSource;
  }

  // Option 2: Use fetch for POST with custom parameters
  else {
    return startStreamingAnalysisWithFetch(query, callbacks, options);
  }
}

/**
 * Start streaming analysis using fetch API (supports POST)
 */
async function startStreamingAnalysisWithFetch(query, callbacks, options) {
  const {
    onStart,
    onAgentProgress,
    onAgentStart,
    onQueryParsed,
    onAgentUpdate,
    onRiskUpdate,
    onDecision,
    onComplete,
    onError
  } = callbacks;

  try {
    const response = await fetch(`${API_BASE_URL}/analyze/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        account_balance: options.accountBalance,
        max_risk_per_trade: options.maxRiskPerTrade
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();

      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      // Process complete SSE messages
      const lines = buffer.split('\n\n');
      buffer = lines.pop(); // Keep incomplete message in buffer

      for (const line of lines) {
        if (!line.trim()) continue;

        const [eventLine, dataLine] = line.split('\n');

        if (!eventLine.startsWith('event:') || !dataLine.startsWith('data:')) {
          continue;
        }

        const eventType = eventLine.substring(7).trim();
        const eventData = JSON.parse(dataLine.substring(6));

        // Route to appropriate callback
        switch (eventType) {
          case 'start':
            onStart?.(eventData);
            break;
          case 'agent_progress':
            onAgentProgress?.(eventData.agent_progress);
            break;
          case 'agent_start':
            onAgentStart?.(eventData.agent_start);
            break;
          case 'query_parsed':
            onQueryParsed?.(eventData);
            break;
          case 'agent_update':
            onAgentUpdate?.(eventData);
            break;
          case 'risk_update':
            onRiskUpdate?.(eventData);
            break;
          case 'decision':
            onDecision?.(eventData);
            break;
          case 'complete':
            onComplete?.(eventData);
            break;
          case 'error':
            onError?.(eventData);
            break;
        }
      }
    }
  } catch (error) {
    console.error('Fetch streaming error:', error);
    onError?.({ error: error.message });
  }

  // Return a simple controller
  return {
    close: () => {
      // In fetch streaming, there's no explicit close method
      // The stream will close naturally when done
    }
  };
}

/**
 * Check API health
 */
export async function checkHealth() {
  const response = await fetch(`${API_BASE_URL}/health`);
  return await response.json();
}

/**
 * Get system info
 */
export async function getSystemInfo() {
  const response = await fetch(`${API_BASE_URL}/info`);
  return await response.json();
}
```

---

## React/Vue Component Examples

### React Component

```jsx
// components/ForexAnalysis.jsx
import React, { useState } from 'react';
import { startStreamingAnalysis } from '../utils/forexApi';

export default function ForexAnalysis() {
  const [query, setQuery] = useState('Analyze EUR/USD');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [progress, setProgress] = useState([]);
  const [results, setResults] = useState({
    queryContext: null,
    news: null,
    technical: null,
    fundamental: null,
    risk: null,
    decision: null
  });
  const [error, setError] = useState(null);

  const handleStartAnalysis = () => {
    setIsAnalyzing(true);
    setProgress([]);
    setResults({
      queryContext: null,
      news: null,
      technical: null,
      fundamental: null,
      risk: null,
      decision: null
    });
    setError(null);

    const eventSource = startStreamingAnalysis(
      query,
      {
        onStart: (data) => {
          setProgress(prev => [...prev, {
            type: 'system',
            message: 'Analysis started',
            timestamp: data.timestamp
          }]);
        },

        onAgentProgress: (progressData) => {
          setProgress(prev => [...prev, {
            type: 'progress',
            agent: progressData.agent,
            step: progressData.step,
            message: progressData.message,
            data: progressData.data,
            timestamp: new Date().toISOString()
          }]);
        },

        onAgentStart: (startData) => {
          setProgress(prev => [...prev, {
            type: 'agent_start',
            agent: startData.agent,
            message: `${startData.agent} agent started`,
            timestamp: new Date().toISOString()
          }]);
        },

        onQueryParsed: (data) => {
          setResults(prev => ({ ...prev, queryContext: data.query_context }));
          setProgress(prev => [...prev, {
            type: 'milestone',
            message: `Query parsed: ${data.pair}`,
            timestamp: data.timestamp
          }]);
        },

        onAgentUpdate: (data) => {
          const agentName = data.agent;
          setResults(prev => ({ ...prev, [agentName]: data.result }));
          setProgress(prev => [...prev, {
            type: 'milestone',
            message: `${agentName} agent completed`,
            timestamp: data.timestamp
          }]);
        },

        onRiskUpdate: (data) => {
          setResults(prev => ({ ...prev, risk: data.risk_result }));
          const approved = data.trade_approved;
          setProgress(prev => [...prev, {
            type: 'milestone',
            message: approved ? 'Risk approved ✓' : 'Risk rejected ✗',
            timestamp: data.timestamp
          }]);
        },

        onDecision: (data) => {
          setResults(prev => ({ ...prev, decision: data.decision }));
          setProgress(prev => [...prev, {
            type: 'milestone',
            message: `Final decision: ${data.decision.action}`,
            timestamp: data.timestamp
          }]);
        },

        onComplete: (data) => {
          setIsAnalyzing(false);
          setProgress(prev => [...prev, {
            type: 'system',
            message: 'Analysis complete',
            timestamp: data.timestamp
          }]);
        },

        onError: (errorData) => {
          setIsAnalyzing(false);
          setError(errorData.error);
          setProgress(prev => [...prev, {
            type: 'error',
            message: `Error: ${errorData.error}`,
            timestamp: errorData.timestamp || new Date().toISOString()
          }]);
        }
      }
    );

    // Cleanup on unmount
    return () => {
      if (eventSource) {
        eventSource.close();
      }
    };
  };

  return (
    <div className="forex-analysis">
      <div className="input-section">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter trading query..."
          disabled={isAnalyzing}
        />
        <button
          onClick={handleStartAnalysis}
          disabled={isAnalyzing}
        >
          {isAnalyzing ? 'Analyzing...' : 'Start Analysis'}
        </button>
      </div>

      {error && (
        <div className="error-banner">
          <strong>Error:</strong> {error}
        </div>
      )}

      <div className="progress-section">
        <h3>Progress</h3>
        <div className="progress-log">
          {progress.map((item, idx) => (
            <ProgressItem key={idx} item={item} />
          ))}
        </div>
      </div>

      {results.queryContext && (
        <div className="results-section">
          <h3>Results</h3>

          <QueryContextCard data={results.queryContext} />

          {results.news && <NewsCard data={results.news} />}

          {results.technical && <TechnicalCard data={results.technical} />}

          {results.fundamental && <FundamentalCard data={results.fundamental} />}

          {results.risk && <RiskCard data={results.risk} />}

          {results.decision && <DecisionCard data={results.decision} />}
        </div>
      )}
    </div>
  );
}

function ProgressItem({ item }) {
  const getIcon = () => {
    switch (item.type) {
      case 'progress':
        return '⏳';
      case 'agent_start':
        return '🚀';
      case 'milestone':
        return '✓';
      case 'error':
        return '❌';
      default:
        return 'ℹ️';
    }
  };

  const getAgentIcon = () => {
    switch (item.agent) {
      case 'query_parser':
        return '🔍';
      case 'news':
        return '📰';
      case 'technical':
        return '📊';
      case 'fundamental':
        return '💼';
      case 'synthesis':
        return '🤖';
      default:
        return '';
    }
  };

  return (
    <div className={`progress-item ${item.type}`}>
      <span className="icon">{getIcon()} {getAgentIcon()}</span>
      <span className="message">{item.message}</span>
      {item.data && (
        <span className="data">
          {item.data.price && ` ($${item.data.price})`}
        </span>
      )}
    </div>
  );
}

// Result card components...
function QueryContextCard({ data }) {
  return (
    <div className="card query-context-card">
      <h4>📝 Query Context</h4>
      <div className="card-content">
        <div className="field">
          <strong>Pair:</strong> {data.pair}
        </div>
        <div className="field">
          <strong>Asset Type:</strong> {data.asset_type}
        </div>
        <div className="field">
          <strong>Timeframe:</strong> {data.timeframe}
        </div>
        <div className="field">
          <strong>Intent:</strong> {data.user_intent}
        </div>
      </div>
    </div>
  );
}

function NewsCard({ data }) {
  if (!data.data) return null;
  const newsData = data.data;

  return (
    <div className="card news-card">
      <h4>📰 News Analysis</h4>
      <div className="card-content">
        <div className="sentiment-badge" data-sentiment={newsData.sentiment}>
          {newsData.sentiment.toUpperCase()}
        </div>
        <p><strong>Impact:</strong> {newsData.impact}</p>
        <p>{newsData.summary}</p>

        <h5>Recent Headlines:</h5>
        <ul>
          {newsData.headlines?.slice(0, 3).map((headline, idx) => (
            <li key={idx}>
              <strong>{headline.title}</strong>
              <br />
              <small>{headline.source} - {headline.date}</small>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

function TechnicalCard({ data }) {
  if (!data.data) return null;
  const techData = data.data;

  return (
    <div className="card technical-card">
      <h4>📊 Technical Analysis</h4>
      <div className="card-content">
        <div className="price-info">
          <strong>Current Price:</strong> ${techData.current_price}
          <span className={`source-badge ${techData.price_source}`}>
            {techData.price_source}
          </span>
        </div>

        <div className="signal-badge" data-signal={techData.signals?.overall}>
          {techData.signals?.overall}
        </div>

        <p><strong>Trend:</strong> {techData.trend} ({techData.trend_strength})</p>
        <p><strong>Support:</strong> ${techData.support}</p>
        <p><strong>Resistance:</strong> ${techData.resistance}</p>

        <p>{techData.summary}</p>
      </div>
    </div>
  );
}

function FundamentalCard({ data }) {
  if (!data.data) return null;
  const fundData = data.data;

  return (
    <div className="card fundamental-card">
      <h4>💼 Fundamental Analysis</h4>
      <div className="card-content">
        <div className="outlook-badge" data-outlook={fundData.outlook}>
          {fundData.outlook.toUpperCase()}
        </div>

        <p>{fundData.summary}</p>

        <h5>Key Factors:</h5>
        <ul>
          {fundData.key_factors?.slice(0, 3).map((factor, idx) => (
            <li key={idx}>{factor}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}

function RiskCard({ data }) {
  if (!data.data) return null;
  const riskData = data.data;

  return (
    <div className={`card risk-card ${riskData.trade_approved ? 'approved' : 'rejected'}`}>
      <h4>⚖️ Risk Assessment</h4>
      <div className="card-content">
        <div className={`approval-badge ${riskData.trade_approved ? 'approved' : 'rejected'}`}>
          {riskData.trade_approved ? '✓ APPROVED' : '✗ REJECTED'}
        </div>

        {!riskData.trade_approved && (
          <p className="rejection-reason">
            <strong>Reason:</strong> {riskData.rejection_reason}
          </p>
        )}

        <p><strong>Position Size:</strong> {riskData.position_size} lots</p>
        <p><strong>Risk:</strong> ${riskData.dollar_risk} ({riskData.risk_percentage}%)</p>
        {riskData.risk_reward_ratio && (
          <p><strong>R:R Ratio:</strong> {riskData.risk_reward_ratio}:1</p>
        )}
      </div>
    </div>
  );
}

function DecisionCard({ data }) {
  return (
    <div className={`card decision-card ${data.action.toLowerCase()}`}>
      <h4>🎯 Final Decision</h4>
      <div className="card-content">
        <div className={`action-badge ${data.action.toLowerCase()}`}>
          {data.action}
        </div>

        <p><strong>Confidence:</strong> {(data.confidence * 100).toFixed(0)}%</p>

        <p>{data.reasoning?.summary}</p>

        {data.trade_parameters && (
          <div className="trade-params">
            <h5>Trade Parameters:</h5>
            <p><strong>Entry:</strong> ${data.trade_parameters.entry_price}</p>
            <p><strong>Stop Loss:</strong> ${data.trade_parameters.stop_loss}</p>
            <p><strong>Take Profit:</strong> ${data.trade_parameters.take_profit}</p>
          </div>
        )}
      </div>
    </div>
  );
}
```

### Vue Component

```vue
<!-- components/ForexAnalysis.vue -->
<template>
  <div class="forex-analysis">
    <div class="input-section">
      <input
        v-model="query"
        type="text"
        placeholder="Enter trading query..."
        :disabled="isAnalyzing"
      />
      <button @click="startAnalysis" :disabled="isAnalyzing">
        {{ isAnalyzing ? 'Analyzing...' : 'Start Analysis' }}
      </button>
    </div>

    <div v-if="error" class="error-banner">
      <strong>Error:</strong> {{ error }}
    </div>

    <div class="progress-section">
      <h3>Progress</h3>
      <div class="progress-log">
        <ProgressItem
          v-for="(item, idx) in progress"
          :key="idx"
          :item="item"
        />
      </div>
    </div>

    <div v-if="results.queryContext" class="results-section">
      <h3>Results</h3>
      <QueryContextCard :data="results.queryContext" />
      <NewsCard v-if="results.news" :data="results.news" />
      <TechnicalCard v-if="results.technical" :data="results.technical" />
      <FundamentalCard v-if="results.fundamental" :data="results.fundamental" />
      <RiskCard v-if="results.risk" :data="results.risk" />
      <DecisionCard v-if="results.decision" :data="results.decision" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { startStreamingAnalysis } from '../utils/forexApi';

const query = ref('Analyze EUR/USD');
const isAnalyzing = ref(false);
const progress = ref([]);
const results = ref({
  queryContext: null,
  news: null,
  technical: null,
  fundamental: null,
  risk: null,
  decision: null
});
const error = ref(null);

let eventSource = null;

const startAnalysis = () => {
  isAnalyzing.value = true;
  progress.value = [];
  results.value = {
    queryContext: null,
    news: null,
    technical: null,
    fundamental: null,
    risk: null,
    decision: null
  };
  error.value = null;

  eventSource = startStreamingAnalysis(
    query.value,
    {
      onStart: (data) => {
        progress.value.push({
          type: 'system',
          message: 'Analysis started',
          timestamp: data.timestamp
        });
      },

      onAgentProgress: (progressData) => {
        progress.value.push({
          type: 'progress',
          agent: progressData.agent,
          step: progressData.step,
          message: progressData.message,
          data: progressData.data,
          timestamp: new Date().toISOString()
        });
      },

      onAgentStart: (startData) => {
        progress.value.push({
          type: 'agent_start',
          agent: startData.agent,
          message: `${startData.agent} agent started`,
          timestamp: new Date().toISOString()
        });
      },

      onQueryParsed: (data) => {
        results.value.queryContext = data.query_context;
        progress.value.push({
          type: 'milestone',
          message: `Query parsed: ${data.pair}`,
          timestamp: data.timestamp
        });
      },

      onAgentUpdate: (data) => {
        const agentName = data.agent;
        results.value[agentName] = data.result;
        progress.value.push({
          type: 'milestone',
          message: `${agentName} agent completed`,
          timestamp: data.timestamp
        });
      },

      onRiskUpdate: (data) => {
        results.value.risk = data.risk_result;
        const approved = data.trade_approved;
        progress.value.push({
          type: 'milestone',
          message: approved ? 'Risk approved ✓' : 'Risk rejected ✗',
          timestamp: data.timestamp
        });
      },

      onDecision: (data) => {
        results.value.decision = data.decision;
        progress.value.push({
          type: 'milestone',
          message: `Final decision: ${data.decision.action}`,
          timestamp: data.timestamp
        });
      },

      onComplete: (data) => {
        isAnalyzing.value = false;
        progress.value.push({
          type: 'system',
          message: 'Analysis complete',
          timestamp: data.timestamp
        });
      },

      onError: (errorData) => {
        isAnalyzing.value = false;
        error.value = errorData.error;
        progress.value.push({
          type: 'error',
          message: `Error: ${errorData.error}`,
          timestamp: errorData.timestamp || new Date().toISOString()
        });
      }
    }
  );
};
</script>

<style scoped>
/* Add your styles here */
</style>
```

---

## UI/UX Best Practices

### 1. Progress Indicators

Show different states for each agent:

```jsx
<div className="agent-status">
  {['news', 'technical', 'fundamental'].map(agent => (
    <div key={agent} className={`agent-pill ${getAgentStatus(agent)}`}>
      {getAgentIcon(agent)} {agent}
      {getAgentStatus(agent) === 'running' && <Spinner />}
      {getAgentStatus(agent) === 'complete' && '✓'}
    </div>
  ))}
</div>
```

### 2. Real-time Price Updates

```jsx
{progress.some(p => p.step === 'price_fetched') && (
  <div className="price-ticker">
    <strong>{currentPair}:</strong> ${currentPrice}
    {priceSource === 'real' && <span className="live-badge">LIVE</span>}
  </div>
)}
```

### 3. Google Search Indicator

```jsx
{progress.some(p => p.step === 'google_search') && (
  <div className="search-indicator">
    <SearchIcon className="spinning" />
    Searching web for real-time data...
  </div>
)}
```

### 4. Agent Timeline

```jsx
<div className="timeline">
  {progress.map((item, idx) => (
    <div key={idx} className="timeline-item">
      <div className="timestamp">{formatTime(item.timestamp)}</div>
      <div className="event">
        <span className="icon">{getIcon(item)}</span>
        <span className="message">{item.message}</span>
      </div>
    </div>
  ))}
</div>
```

### 5. Loading Skeletons

While waiting for agent results, show skeleton loaders:

```jsx
{isAnalyzing && !results.technical && (
  <div className="card skeleton">
    <div className="skeleton-title"></div>
    <div className="skeleton-line"></div>
    <div className="skeleton-line"></div>
    <div className="skeleton-line short"></div>
  </div>
)}
```

---

## Error Handling

### Connection Errors

```javascript
const handleConnectionError = (error) => {
  console.error('Connection error:', error);

  // Check if it's a network error
  if (!navigator.onLine) {
    showError('No internet connection. Please check your network.');
    return;
  }

  // Check if backend is down
  checkHealth()
    .then(() => {
      showError('Stream connection failed. Please try again.');
    })
    .catch(() => {
      showError('Backend server is not responding. Please try later.');
    });
};
```

### Retry Logic

```javascript
const startAnalysisWithRetry = async (maxRetries = 3) => {
  let attempt = 0;

  while (attempt < maxRetries) {
    try {
      await startStreamingAnalysis(query, callbacks);
      break; // Success
    } catch (error) {
      attempt++;
      if (attempt >= maxRetries) {
        throw error;
      }
      // Wait before retry (exponential backoff)
      await new Promise(resolve => setTimeout(resolve, 1000 * Math.pow(2, attempt)));
    }
  }
};
```

### Timeout Handling

```javascript
const startAnalysisWithTimeout = (query, callbacks, timeout = 60000) => {
  let timeoutId;
  let eventSource;

  const timeoutPromise = new Promise((_, reject) => {
    timeoutId = setTimeout(() => {
      if (eventSource) {
        eventSource.close();
      }
      reject(new Error('Analysis timeout'));
    }, timeout);
  });

  eventSource = startStreamingAnalysis(query, {
    ...callbacks,
    onComplete: (data) => {
      clearTimeout(timeoutId);
      callbacks.onComplete?.(data);
    },
    onError: (error) => {
      clearTimeout(timeoutId);
      callbacks.onError?.(error);
    }
  });

  return { eventSource, timeoutPromise };
};
```

---

## Complete Example

### Full Vite.js + React App

```javascript
// src/App.jsx
import React from 'react';
import ForexAnalysis from './components/ForexAnalysis';
import './App.css';

function App() {
  return (
    <div className="app">
      <header>
        <h1>🌍 Forex Agent System</h1>
        <p>AI-Powered Trading Analysis with Real-Time Streaming</p>
      </header>

      <main>
        <ForexAnalysis />
      </main>

      <footer>
        <p>Powered by LangGraph + Gemini 2.5 Flash + Google Search</p>
      </footer>
    </div>
  );
}

export default App;
```

```css
/* src/App.css */
.app {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

header {
  text-align: center;
  margin-bottom: 40px;
}

.forex-analysis {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.input-section {
  display: flex;
  gap: 10px;
}

.input-section input {
  flex: 1;
  padding: 12px;
  font-size: 16px;
  border: 2px solid #ddd;
  border-radius: 8px;
}

.input-section button {
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.input-section button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.input-section button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-banner {
  padding: 16px;
  background: #fee;
  border-left: 4px solid #e33;
  border-radius: 4px;
  color: #c00;
}

.progress-section {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 12px;
}

.progress-log {
  max-height: 400px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.progress-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: white;
  border-radius: 8px;
  border-left: 4px solid #ddd;
  transition: all 0.2s;
}

.progress-item.progress {
  border-color: #3b82f6;
  animation: pulse 2s infinite;
}

.progress-item.agent_start {
  border-color: #10b981;
}

.progress-item.milestone {
  border-color: #8b5cf6;
  font-weight: 600;
}

.progress-item.error {
  border-color: #ef4444;
  background: #fee;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.results-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: all 0.3s;
}

.card:hover {
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
  transform: translateY(-2px);
}

.card h4 {
  margin-top: 0;
  margin-bottom: 16px;
  font-size: 18px;
  color: #333;
}

.sentiment-badge, .signal-badge, .outlook-badge, .approval-badge, .action-badge {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
}

.sentiment-badge[data-sentiment="bullish"],
.signal-badge[data-signal="BUY"],
.outlook-badge[data-outlook="bullish"],
.action-badge.buy {
  background: #d1fae5;
  color: #065f46;
}

.sentiment-badge[data-sentiment="bearish"],
.signal-badge[data-signal="SELL"],
.outlook-badge[data-outlook="bearish"],
.action-badge.sell {
  background: #fee2e2;
  color: #991b1b;
}

.sentiment-badge[data-sentiment="neutral"],
.signal-badge[data-signal="HOLD"],
.outlook-badge[data-outlook="neutral"],
.action-badge.wait {
  background: #e5e7eb;
  color: #374151;
}

.approval-badge.approved {
  background: #d1fae5;
  color: #065f46;
}

.approval-badge.rejected {
  background: #fee2e2;
  color: #991b1b;
}

.source-badge {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  margin-left: 8px;
}

.source-badge.real {
  background: #10b981;
  color: white;
}

.source-badge.mock {
  background: #f59e0b;
  color: white;
}
```

---

## Testing

### Test Script

```javascript
// test/streamTest.js
import { startStreamingAnalysis } from '../src/utils/forexApi';

async function testStream() {
  console.log('Starting stream test...');

  const events = [];
  let startTime = Date.now();

  const eventSource = startStreamingAnalysis(
    'Analyze EUR/USD',
    {
      onStart: (data) => {
        console.log('✓ START event received');
        events.push({ type: 'start', data });
      },
      onAgentProgress: (data) => {
        console.log(`✓ PROGRESS event: ${data.agent} - ${data.step}`);
        events.push({ type: 'progress', data });
      },
      onAgentStart: (data) => {
        console.log(`✓ AGENT START: ${data.agent}`);
        events.push({ type: 'agent_start', data });
      },
      onQueryParsed: (data) => {
        console.log(`✓ QUERY PARSED: ${data.pair}`);
        events.push({ type: 'query_parsed', data });
      },
      onAgentUpdate: (data) => {
        console.log(`✓ AGENT UPDATE: ${data.agent}`);
        events.push({ type: 'agent_update', data });
      },
      onRiskUpdate: (data) => {
        console.log(`✓ RISK UPDATE: ${data.trade_approved ? 'APPROVED' : 'REJECTED'}`);
        events.push({ type: 'risk_update', data });
      },
      onDecision: (data) => {
        console.log(`✓ DECISION: ${data.decision.action}`);
        events.push({ type: 'decision', data });
      },
      onComplete: (data) => {
        const elapsed = Date.now() - startTime;
        console.log(`✓ COMPLETE (${elapsed}ms)`);
        console.log(`Total events received: ${events.length}`);
        events.push({ type: 'complete', data });

        // Validate
        console.log('\nValidation:');
        console.log(`- Start event: ${events.some(e => e.type === 'start') ? '✓' : '✗'}`);
        console.log(`- Progress events: ${events.filter(e => e.type === 'progress').length}`);
        console.log(`- Agent updates: ${events.filter(e => e.type === 'agent_update').length}`);
        console.log(`- Complete event: ${events.some(e => e.type === 'complete') ? '✓' : '✗'}`);
      },
      onError: (error) => {
        console.error('✗ ERROR:', error);
        events.push({ type: 'error', data: error });
      }
    }
  );
}

testStream();
```

---

## Conclusion

This integration guide provides everything needed to implement the streaming agent system in a Vite.js frontend:

1. ✅ Complete event type documentation
2. ✅ JavaScript EventSource implementation
3. ✅ Fetch API streaming alternative (for POST requests)
4. ✅ React and Vue component examples
5. ✅ UI/UX best practices
6. ✅ Error handling strategies
7. ✅ Complete working example
8. ✅ Testing scripts

The frontend will receive real-time updates for:
- Query parsing
- Agent start events
- Progress updates (API calls, LLM processing, web searches)
- Price fetching from external APIs
- Google Search operations
- Agent completion with full results
- Risk assessment
- Final trading decision

All data is structured and ready to display in your UI!
