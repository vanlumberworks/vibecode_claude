# Streaming API Documentation

This document describes the real-time streaming API for the Forex Agent System, built with FastAPI and Server-Sent Events (SSE).

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [API Endpoints](#api-endpoints)
- [Event Types](#event-types)
- [Client Examples](#client-examples)
- [Error Handling](#error-handling)
- [Deployment](#deployment)

## Overview

The Streaming API provides real-time updates as the LangGraph workflow executes, allowing clients to:

- Monitor analysis progress in real-time
- Display intermediate results as agents complete
- Provide better UX with progressive updates
- Handle long-running analyses gracefully

### Key Features

- **Server-Sent Events (SSE)**: Standard HTTP-based streaming protocol
- **Real-time Updates**: Get notified as each agent completes
- **Structured Events**: Well-defined event types for easy parsing
- **Backward Compatible**: Non-streaming endpoint still available
- **Production Ready**: Built with FastAPI, async/await, proper error handling

## Architecture

### Components

```
┌─────────────┐
│   Client    │
│  (Browser,  │
│   Python,   │
│   etc.)     │
└──────┬──────┘
       │ HTTP/SSE
       ▼
┌─────────────────────────────────────┐
│        FastAPI Server               │
│  ┌─────────────────────────────┐   │
│  │   Streaming Adapter          │   │
│  │  - Wraps ForexAgentSystem   │   │
│  │  - Emits real-time events   │   │
│  └────────────┬─────────────────┘   │
│               │                      │
│               ▼                      │
│  ┌─────────────────────────────┐   │
│  │   LangGraph Workflow         │   │
│  │  - Query Parser              │   │
│  │  - Parallel Agents           │   │
│  │  - Risk Assessment           │   │
│  │  - Synthesis                 │   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘
```

### Streaming Flow

1. **Client** sends request to `/analyze/stream`
2. **FastAPI** creates SSE connection
3. **StreamingAdapter** wraps ForexAgentSystem
4. **LangGraph** executes workflow, streaming state updates
5. **Adapter** detects state changes and emits events
6. **FastAPI** sends events to client via SSE
7. Client processes events in real-time

## Getting Started

### Installation

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Configure environment:

```bash
cp .env.example .env
# Edit .env and add your GOOGLE_AI_API_KEY
```

3. Start the server:

```bash
# Option 1: Run directly
python backend/server.py

# Option 2: Use uvicorn
uvicorn backend.server:app --reload

# Option 3: Custom host/port
uvicorn backend.server:app --host 0.0.0.0 --port 8080
```

4. Verify it's running:

```bash
curl http://localhost:8000/health
```

### Quick Test

```bash
# Terminal 1: Start server
python backend/server.py

# Terminal 2: Run example client
python examples/streaming_client.py "Analyze gold trading"

# Terminal 3: Run comprehensive tests
python test_streaming_api.py
```

## API Endpoints

### Health Check

**GET /health**

Check if the API is running and configured properly.

**Response:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "api_configured": true
}
```

### System Info

**GET /info**

Get detailed system information including configuration and workflow structure.

**Response:**
```json
{
  "system": {
    "account_balance": 10000.0,
    "max_risk_per_trade": 0.02,
    "api_configured": true
  },
  "workflow": {
    "nodes": ["query_parser", "parallel_analysis", "risk", "synthesis"],
    "edges": [...],
    "num_nodes": 4,
    "num_edges": 5
  }
}
```

### Non-Streaming Analysis

**POST /analyze**

Run a complete analysis and return the final result (no streaming).

**Request:**
```json
{
  "query": "Analyze gold trading",
  "account_balance": 10000.0,  // optional
  "max_risk_per_trade": 0.02   // optional
}
```

**Response:**
```json
{
  "user_query": "Analyze gold trading",
  "query_context": {
    "pair": "XAU/USD",
    "asset_type": "commodity",
    ...
  },
  "decision": {
    "action": "BUY",
    "confidence": 0.75,
    "reasoning": {...},
    "trade_parameters": {...}
  },
  "agent_results": {...},
  "metadata": {...}
}
```

### Streaming Analysis (SSE)

**POST /analyze/stream**

**GET /analyze/stream?query=...**

Run analysis with real-time streaming updates.

**Request (POST):**
```json
{
  "query": "Should I buy EUR/USD?",
  "account_balance": 10000.0,
  "max_risk_per_trade": 0.02
}
```

**Request (GET):**
```
GET /analyze/stream?query=Analyze+gold+trading
```

**Response:** Server-Sent Events stream (see [Event Types](#event-types))

## Event Types

The streaming API emits the following event types:

### 1. Start Event

Emitted when analysis begins.

```
event: start
data: {
  "query": "Analyze gold trading",
  "timestamp": "2025-01-15T10:30:00.000Z"
}
```

### 2. Query Parsed Event

Emitted after natural language query is parsed into structured context.

```
event: query_parsed
data: {
  "step": 1,
  "query_context": {
    "pair": "XAU/USD",
    "asset_type": "commodity",
    "base_currency": "XAU",
    "quote_currency": "USD",
    "timeframe": "intraday",
    "user_intent": "trading_signal",
    "risk_tolerance": "moderate"
  },
  "pair": "XAU/USD",
  "timestamp": "2025-01-15T10:30:01.234Z"
}
```

### 3. Agent Update Event

Emitted when each agent (News, Technical, Fundamental) completes.

```
event: agent_update
data: {
  "step": 2,
  "agent": "news",
  "result": {
    "success": true,
    "data": {
      "sentiment": "bullish",
      "score": 0.7,
      ...
    },
    "summary": "News sentiment is bullish"
  },
  "timestamp": "2025-01-15T10:30:02.456Z"
}
```

**Agent Types:**
- `news` - News/sentiment analysis
- `technical` - Technical indicators
- `fundamental` - Economic fundamentals

### 4. Risk Update Event

Emitted after risk assessment completes.

```
event: risk_update
data: {
  "step": 3,
  "risk_result": {
    "success": true,
    "data": {
      "trade_approved": true,
      "position_size": 0.5,
      "risk_amount": 200.0,
      ...
    }
  },
  "trade_approved": true,
  "timestamp": "2025-01-15T10:30:03.789Z"
}
```

**Note:** If `trade_approved: false`, the workflow ends and no synthesis occurs.

### 5. Decision Event

Emitted when final trading decision is made.

```
event: decision
data: {
  "step": 4,
  "decision": {
    "action": "BUY",
    "confidence": 0.75,
    "reasoning": {
      "summary": "Strong bullish signals across all indicators",
      "key_factors": [
        "Positive news sentiment",
        "Technical indicators show uptrend",
        "Strong fundamentals"
      ]
    },
    "trade_parameters": {
      "entry_price": "2050.00",
      "stop_loss": "2040.00",
      "take_profit": "2070.00",
      "position_size": 0.5
    }
  },
  "timestamp": "2025-01-15T10:30:05.123Z"
}
```

**Actions:**
- `BUY` - Go long
- `SELL` - Go short
- `WAIT` - No trade recommended

### 6. Complete Event

Emitted when analysis is fully complete.

```
event: complete
data: {
  "result": {
    "user_query": "Analyze gold trading",
    "query_context": {...},
    "decision": {...},
    "agent_results": {...},
    "metadata": {...}
  },
  "timestamp": "2025-01-15T10:30:05.456Z"
}
```

### 7. Error Event

Emitted if an error occurs during analysis.

```
event: error
data: {
  "error": "API key not configured",
  "error_type": "ValueError",
  "timestamp": "2025-01-15T10:30:00.789Z"
}
```

## Client Examples

### Python (sseclient-py)

```python
from sseclient import SSEClient
import json

url = "http://localhost:8000/analyze/stream?query=Analyze gold"
messages = SSEClient(url)

for msg in messages:
    if not msg.data:
        continue

    event_type = msg.event
    data = json.loads(msg.data)

    if event_type == "decision":
        decision = data.get("decision", {})
        print(f"Action: {decision['action']}")
        print(f"Confidence: {decision['confidence']}")

    elif event_type == "complete":
        print("Analysis complete!")
        break

    elif event_type == "error":
        print(f"Error: {data['error']}")
        break
```

### JavaScript (EventSource)

```javascript
const query = "Analyze gold trading";
const url = `http://localhost:8000/analyze/stream?query=${encodeURIComponent(query)}`;

const eventSource = new EventSource(url);

eventSource.addEventListener('start', (event) => {
  const data = JSON.parse(event.data);
  console.log('Analysis started:', data.query);
});

eventSource.addEventListener('query_parsed', (event) => {
  const data = JSON.parse(event.data);
  console.log('Analyzing:', data.pair);
});

eventSource.addEventListener('agent_update', (event) => {
  const data = JSON.parse(event.data);
  console.log(`${data.agent} agent completed`);
});

eventSource.addEventListener('decision', (event) => {
  const data = JSON.parse(event.data);
  console.log('Decision:', data.decision.action);
  console.log('Confidence:', data.decision.confidence);
});

eventSource.addEventListener('complete', (event) => {
  const data = JSON.parse(event.data);
  console.log('Analysis complete!');
  eventSource.close();
});

eventSource.addEventListener('error', (event) => {
  console.error('Error:', event);
  eventSource.close();
});

eventSource.onerror = (error) => {
  console.error('Connection error:', error);
  eventSource.close();
};
```

### cURL

```bash
# Stream to console
curl -N http://localhost:8000/analyze/stream?query=Analyze+gold

# Save to file
curl -N http://localhost:8000/analyze/stream?query=EUR/USD > analysis.txt
```

### Python (requests with streaming)

```python
import requests
import json

url = "http://localhost:8000/analyze/stream"
params = {"query": "Analyze gold"}

response = requests.get(url, params=params, stream=True)

for line in response.iter_lines():
    if not line:
        continue

    line = line.decode('utf-8')

    if line.startswith('event:'):
        event_type = line.split(':', 1)[1].strip()
    elif line.startswith('data:'):
        data = json.loads(line.split(':', 1)[1].strip())
        print(f"{event_type}: {data}")
```

## Error Handling

### API Errors

The API returns standard HTTP error codes:

- `400 Bad Request` - Invalid query or parameters
- `500 Internal Server Error` - Server-side error
- `503 Service Unavailable` - API not configured (missing API key)

### Streaming Errors

Errors during streaming are sent as `error` events:

```
event: error
data: {
  "error": "Google AI API key not configured",
  "error_type": "ValueError"
}
```

**Client should:**
1. Listen for `error` events
2. Close the EventSource connection
3. Display error to user
4. Optionally retry with exponential backoff

### Connection Errors

If the connection drops:

```javascript
eventSource.onerror = (error) => {
  console.error('Connection error:', error);

  // Retry with exponential backoff
  setTimeout(() => {
    connectWithRetry();
  }, retryDelay);
};
```

## Deployment

### Production Considerations

1. **CORS Configuration**: Update `allow_origins` in `backend/server.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

2. **HTTPS**: Use a reverse proxy (nginx, Caddy) for SSL termination

3. **Environment Variables**: Set in production:
```bash
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=false
GOOGLE_AI_API_KEY=your_production_key
```

4. **Process Management**: Use systemd, supervisor, or Docker

5. **Rate Limiting**: Implement rate limiting for production:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/analyze/stream")
@limiter.limit("10/minute")
async def analyze_stream(request: AnalysisRequest):
    ...
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "backend.server:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t forex-agent-api .
docker run -p 8000:8000 -e GOOGLE_AI_API_KEY=your_key forex-agent-api
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: forex-agent-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: forex-agent-api
  template:
    metadata:
      labels:
        app: forex-agent-api
    spec:
      containers:
      - name: api
        image: forex-agent-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: GOOGLE_AI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: google-ai-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
```

## Performance Considerations

### Latency

Typical analysis timeline:
- Query parsing: ~1s
- Parallel agents: ~2s (all 3 run simultaneously)
- Risk assessment: ~1s
- Synthesis: ~3-5s (LLM + Google Search)
- **Total: ~7-9 seconds**

### Throughput

Single instance can handle:
- ~10 concurrent streaming connections
- ~100 requests/minute (rate limited)

For higher throughput:
- Use multiple instances behind a load balancer
- Implement caching for repeated queries
- Use Redis for session management

### Costs

Per analysis (approximate):
- Query Parser: $0.001
- Agents: FREE (mock data)
- Risk Assessment: $0.002
- Synthesis: $0.080 (includes Google Search)
- **Total: ~$0.083 per analysis**

100 analyses/day = $8.30/day = $249/month

## Troubleshooting

### Server won't start

```bash
# Check if port is in use
lsof -i :8000

# Try different port
uvicorn backend.server:app --port 8080
```

### API key errors

```bash
# Verify environment
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('GOOGLE_AI_API_KEY'))"
```

### No events received

1. Check server logs for errors
2. Verify CORS configuration
3. Test with curl: `curl -N http://localhost:8000/analyze/stream?query=test`
4. Check browser console for EventSource errors

### Slow responses

1. Check API quotas
2. Verify network latency to Google AI
3. Monitor server resources (CPU, memory)
4. Consider caching repeated queries

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SSE Specification](https://html.spec.whatwg.org/multipage/server-sent-events.html)
- [LangGraph Streaming Docs](https://langchain-ai.github.io/langgraph/concepts/#streaming)
- [EventSource API (MDN)](https://developer.mozilla.org/en-US/docs/Web/API/EventSource)

## Support

For issues or questions:
- Check the main [README.md](../README.md)
- Review [CLAUDE.md](../CLAUDE.md) for project context
- File an issue on GitHub
