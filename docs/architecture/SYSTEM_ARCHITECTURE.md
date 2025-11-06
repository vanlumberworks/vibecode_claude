# System Architecture

**Version**: v3 (LLM-Powered Agents + Historical Data)
**Last Updated**: November 6, 2025
**Status**: Current

## Overview

This document describes the current architecture of the Forex Agent System. The system uses **LangGraph** for agent orchestration and **Gemini 2.5 Flash** with **Google Search grounding** for intelligent analysis.

## High-Level Architecture

```
User Input: Natural Language Query
         ↓
   Query Parser (Gemini)
   → Parses: "Analyze gold" → {"pair": "XAU/USD", "asset_type": "commodity"}
         ↓
   Parallel Analysis (asyncio.gather)
   ├─ News Agent (Gemini + Google Search)
   ├─ Technical Agent (Gemini + Price APIs + Historical Data)
   └─ Fundamental Agent (Gemini + Google Search)
         ↓
   Risk Agent (Gemini)
   → Validates trade parameters and position sizing
         ↓
   [Conditional: Risk Approved?]
         ↓ Yes                    ↓ No
   Synthesis Agent (Gemini)     END (WAIT)
   → Final decision with citations
         ↓
   Output: BUY/SELL/WAIT + Reasoning + Sources
```

## Core Components

### 1. LangGraph Workflow

**File**: `graph/workflow.py`

The workflow orchestrates all agents through a state machine:

**Nodes**:
1. `query_parser` - Converts natural language to structured JSON
2. `parallel_analysis` - Runs News, Technical, Fundamental agents concurrently
3. `risk` - Validates trade parameters
4. `synthesis` - Makes final decision (only if risk approved)

**Edges**:
- Sequential: `query_parser → parallel_analysis → risk`
- Conditional: `risk → synthesis` (if approved) or `risk → END` (if rejected)

**State**: `ForexAgentState` (defined in `graph/state.py`)
- Tracks user query, parsed context, agent results, and final decision
- Immutable - nodes return updates, not modify state directly

### 2. State Management

**File**: `graph/state.py`

```python
class ForexAgentState(TypedDict):
    user_query: str                      # Raw input: "Analyze gold"
    query_context: Dict[str, Any]        # Parsed: {pair, asset_type, timeframe, ...}
    pair: str                            # Deprecated but kept for compatibility

    # Agent results
    news_result: Dict[str, Any]
    technical_result: Dict[str, Any]
    fundamental_result: Dict[str, Any]
    risk_result: Dict[str, Any]

    # Final output
    decision: Dict[str, Any]

    # Metadata
    messages: Sequence[BaseMessage]
    step_count: int
    should_continue: bool
    errors: Dict[str, str]
```

### 3. Query Parser

**File**: `graph/query_parser.py`

**Purpose**: Transform natural language into structured context

**Technology**: Gemini 2.5 Flash with low temperature (0.1) for consistent parsing

**Input Examples**:
- "Analyze gold trading" → `{"pair": "XAU/USD", "asset_type": "commodity"}`
- "Should I buy Bitcoin?" → `{"pair": "BTC/USD", "user_intent": "buy_signal"}`
- "EUR/USD long term" → `{"pair": "EUR/USD", "timeframe": "long_term"}`

**Fallback**: Regex-based parser if Gemini API fails

**Output Structure**:
```json
{
  "pair": "XAU/USD",
  "asset_type": "commodity|forex|crypto|index",
  "base_currency": "XAU",
  "quote_currency": "USD",
  "timeframe": "short_term|medium_term|long_term",
  "user_intent": "trading_signal|buy_signal|sell_signal|market_overview",
  "risk_tolerance": "conservative|moderate|aggressive",
  "additional_context": {
    "keywords": [...],
    "mentioned_indicators": [...],
    "mentioned_events": [...]
  },
  "confidence": 0.95
}
```

### 4. Parallel Analysis

**File**: `graph/parallel_nodes.py`

**Purpose**: Execute multiple agents simultaneously for 3x performance improvement

**Technology**: `asyncio.gather()` for true async parallelism

**Performance**:
- Sequential (v1): 3-6 seconds
- Parallel (v3): 1-2 seconds
- **Speedup**: 3x faster

**Implementation**:
```python
async def parallel_analysis_node(state, config):
    results = await asyncio.gather(
        news_node(state, config),
        technical_node(state, config),
        fundamental_node(state, config),
        return_exceptions=True  # Graceful failure handling
    )
    # Merge results into state
    return merge_results(results)
```

**Why async?**:
- Agents are I/O-bound (API calls)
- No dependencies between News, Technical, Fundamental
- Better resource utilization than ThreadPoolExecutor

### 5. Agent Implementations

#### News Agent

**File**: `agents/news_agent.py`

**Capabilities** (v3):
- ✅ Google Search for real headlines
- ✅ Sentiment analysis (bullish/bearish/neutral)
- ✅ Market impact assessment
- ✅ Source citations
- ✅ Async execution

**Data Sources**: Google Search

**Output**:
```json
{
  "headlines": [
    {"title": "...", "sentiment": "neutral", "impact": "medium"}
  ],
  "overall_sentiment": "neutral",
  "sentiment_score": 0.0,
  "market_impact": "medium",
  "sources": [{"title": "...", "url": "..."}]
}
```

#### Technical Agent

**File**: `agents/technical_agent.py`

**Capabilities** (v3):
- ✅ Real-time prices from Metal Price API / Forex Rate API
- ✅ Historical data (yesterday's rate, 24h change)
- ✅ OHLC data (Open/High/Low/Close)
- ✅ Gemini analyzes technical patterns
- ✅ Calculates support/resistance
- ✅ Trading signals with reasoning

**Data Sources**:
- Metal Price API (commodities)
- Forex Rate API (forex + crypto)
- Historical and OHLC data from same APIs

**Output**:
```json
{
  "current_price": 1.0850,
  "price_source": "real|mock",
  "trend": "uptrend|downtrend|sideways",
  "trend_strength": "strong|medium|weak",
  "support": 1.0800,
  "resistance": 1.0950,
  "indicators": {
    "rsi": 65,
    "macd": "bullish",
    "ma_position": "above_50ma"
  },
  "signals": {
    "overall": "BUY|SELL|WAIT",
    "confidence": 0.75
  },
  "historical": {
    "yesterday_rate": 1.0820,
    "price_change_pct": 0.28
  },
  "ohlc": {
    "open": 1.0820,
    "high": 1.0860,
    "low": 1.0810,
    "close": 1.0850
  }
}
```

#### Fundamental Agent

**File**: `agents/fundamental_agent.py`

**Capabilities** (v3):
- ✅ Google Search for economic data
- ✅ Analyzes GDP, inflation, interest rates
- ✅ Central bank policy monitoring
- ✅ Compares base vs quote currency
- ✅ Fundamental score calculation
- ✅ Supports forex, commodities, crypto

**Data Sources**: Google Search

**Output**:
```json
{
  "base_currency": {
    "currency": "USD",
    "gdp_growth": 2.5,
    "inflation": 3.2,
    "interest_rate": 5.25,
    "central_bank": "Fed maintaining restrictive policy..."
  },
  "quote_currency": {...},
  "comparison": {
    "gdp_growth": "base_stronger|quote_stronger|similar",
    "interest_rate": "base_stronger|quote_stronger|similar",
    "overall": "base has stronger fundamentals"
  },
  "fundamental_score": 0.65,
  "outlook": "bullish|bearish|neutral",
  "key_factors": [...]
}
```

#### Risk Agent

**File**: `agents/risk_agent.py`

**Capabilities** (v3):
- ✅ LLM-powered risk analysis
- ✅ Position sizing based on account balance
- ✅ Stop loss validation (10-100 pips)
- ✅ Risk/reward ratio check (minimum 1.5:1)
- ✅ Trade approval/rejection with reasoning

**Output**:
```json
{
  "trade_approved": true,
  "position_size": 0.20,
  "stop_loss": 1.0780,
  "take_profit": 1.0980,
  "risk_amount": 200.00,
  "risk_percent": 2.0,
  "risk_reward_ratio": 2.0,
  "reasoning": "Trade meets all risk parameters..."
}
```

#### Synthesis Agent

**File**: `graph/nodes.py::synthesis_node()`

**Capabilities**:
- ✅ Combines all agent outputs
- ✅ Google Search for real-time verification
- ✅ Structured decision: BUY/SELL/WAIT
- ✅ Confidence score
- ✅ Detailed reasoning
- ✅ Trade parameters
- ✅ Source citations

**Output**:
```json
{
  "action": "BUY|SELL|WAIT",
  "confidence": 0.82,
  "reasoning": {
    "summary": "...",
    "web_verification": "...",
    "key_factors": [...],
    "risks": [...]
  },
  "trade_parameters": {
    "entry_price": 1.0850,
    "stop_loss": 1.0780,
    "take_profit": 1.0980,
    "position_size": 0.20
  },
  "grounding_metadata": {
    "search_queries": [...],
    "sources": [{"title": "...", "url": "..."}]
  }
}
```

### 6. Price Service

**File**: `agents/price_service.py`

**Purpose**: Centralized price data fetching with caching and fallbacks

**APIs**:
- **Metal Price API** (metalpriceapi.com) - Commodities (XAU, XAG, XPT, XPD)
- **Forex Rate API** (forexrateapi.com) - Forex pairs and crypto

**Features**:
- Automatic API selection based on asset type
- 60-second price caching
- Historical rates (yesterday, specific dates)
- OHLC data (Open/High/Low/Close)
- Enriched price data (current + historical + OHLC)
- Graceful fallback to mock data

**Caching Strategy**:
- Cache duration: 60 seconds
- Reduces API calls by ~50-90%
- Improves performance (1ms vs 500ms)
- Stays within free tier limits

## Execution Flow

### 1. User Query
```python
system = ForexAgentSystem()
result = system.analyze("Analyze gold trading")
```

### 2. Query Parsing
- Input: "Analyze gold trading"
- Gemini parses to: `{"pair": "XAU/USD", "asset_type": "commodity", ...}`
- Updates state with `query_context`

### 3. Parallel Analysis
All three agents run simultaneously:

**News Agent**:
- Searches: "XAU/USD gold news", "gold commodity news"
- Finds real headlines
- Returns sentiment + sources

**Technical Agent**:
- Fetches current price: $2,641.50
- Gets historical: yesterday=$2,628.00, change=+0.5%
- Gets OHLC: Open/High/Low/Close
- Gemini analyzes patterns
- Returns signals + support/resistance

**Fundamental Agent**:
- Searches: "gold fundamental factors", "gold demand"
- Analyzes safe-haven demand, inflation hedge
- Returns fundamental score + outlook

### 4. Risk Assessment
- Receives all agent data
- Validates proposed trade parameters
- Calculates position size (based on $10,000 account, 2% risk)
- Checks stop loss and risk/reward ratio
- Returns `trade_approved: true/false`

### 5. Conditional Routing
If `trade_approved == false`:
- Workflow ends immediately
- Returns WAIT decision with rejection reason

If `trade_approved == true`:
- Proceeds to synthesis agent

### 6. Synthesis
- Receives: News + Technical + Fundamental + Risk data
- Searches Google for real-time verification
- Synthesizes all information
- Makes final decision: BUY/SELL/WAIT
- Includes confidence, reasoning, trade parameters, sources

### 7. Output
Returns structured result with:
- User query and parsed context
- All agent results
- Final decision with reasoning
- Source citations
- Metadata (steps, errors)

## Error Handling

### Agent-Level Errors
Each agent catches exceptions and returns:
```json
{
  "success": false,
  "error": "Description of error",
  "agent": "NewsAgent"
}
```

### Parallel Execution Errors
`asyncio.gather()` with `return_exceptions=True`:
- Individual agent failures don't crash entire analysis
- Failed agents return error results
- Workflow continues with available data

### API Failures
Price Service fallbacks:
1. Try real API
2. Use cached price (if available)
3. Fall back to mock data
4. Return with `price_source: "mock"` indicator

### Risk Rejection
If Risk Agent rejects:
- Workflow ends gracefully
- Returns WAIT decision
- Includes rejection reason
- No synthesis agent execution

## Performance Characteristics

### Execution Time
- Query parsing: ~500ms
- Parallel analysis: ~1-2s (all agents simultaneously)
- Risk assessment: ~500ms
- Synthesis: ~1-2s
- **Total**: ~2-4 seconds

### API Costs (per analysis)
- Query parsing: $0.001
- News Agent (Google Search): $0.015
- Technical Agent: $0.002
- Fundamental Agent (Google Search): $0.015
- Risk Agent: $0.002
- Synthesis (Google Search): $0.015
- **Total**: ~$0.050 per analysis

### Scalability
- Free tier limits: 1,000 Forex API calls/month, 100 Metal API calls/month
- With caching: ~1,000+ analyses/month within free tier
- LangGraph supports streaming for long-running analyses

## Data Flow Diagram

```
[User]
  ↓ "Analyze gold trading"
[ForexAgentSystem]
  ↓
[LangGraph Workflow]
  ↓
[Query Parser] → Gemini API
  ↓ {"pair": "XAU/USD", "asset_type": "commodity"}
[State Update]
  ↓
[Parallel Analysis Node] → asyncio.gather()
  ├─ [News Agent] → Google Search → Headlines + Sources
  ├─ [Technical Agent] → Price APIs → Price + OHLC + Gemini Analysis
  └─ [Fundamental Agent] → Google Search → Economic Data
  ↓ All results merged into state
[Risk Agent] → Gemini API → Trade Validation
  ↓ trade_approved: true
[Synthesis Agent] → Gemini + Google Search → Final Decision
  ↓
[State] → {decision: {action: "BUY", confidence: 0.82, ...}}
  ↓
[ForexAgentSystem._format_result()]
  ↓
[User] ← Structured result with decision + reasoning + sources
```

## Key Design Patterns

### 1. State Machine Pattern
- LangGraph implements workflow as state machine
- Clear transitions between nodes
- Conditional routing based on risk approval

### 2. Async I/O Pattern
- All agents use async/await for API calls
- asyncio.gather() for parallel execution
- Non-blocking I/O operations

### 3. Fallback Pattern
- Price Service: Real API → Cache → Mock data
- Query Parser: Gemini → Regex fallback
- Agents: Try analysis → Return error result

### 4. Caching Pattern
- Time-based cache (60s TTL)
- Reduces API costs
- Improves performance
- Cache invalidation on expiry

### 5. Structured Output Pattern
- All agents return consistent JSON structure
- Type-safe state passing
- Easy integration with LangGraph

## Technology Stack

### Core Framework
- **LangGraph** - Agent orchestration and state management
- **LangChain** - LLM integration utilities
- **Python 3.9+** - Programming language

### LLM & AI
- **Gemini 2.5 Flash** - LLM for all agents
- **Google Search Grounding** - Real-time data verification

### APIs
- **Metal Price API** - Commodity prices
- **Forex Rate API** - Forex and crypto prices

### Libraries
- **asyncio** - Async execution
- **pydantic** - Data validation
- **python-dotenv** - Environment management
- **requests** - HTTP client

## Deployment Considerations

### Environment Variables Required
- `GOOGLE_AI_API_KEY` (required) - Gemini API key
- `METAL_PRICE_API_KEY` (optional) - Commodity price API
- `FOREX_RATE_API_KEY` (optional) - Forex/crypto price API
- `ACCOUNT_BALANCE` (optional) - Default: 10000.0
- `MAX_RISK_PER_TRADE` (optional) - Default: 0.02 (2%)

### Production Recommendations
1. **Rate Limiting**: Implement request throttling for API calls
2. **Monitoring**: Track API costs and quotas
3. **Logging**: Comprehensive logging for debugging
4. **Caching**: Consider Redis for distributed caching
5. **Error Tracking**: Integration with Sentry or similar
6. **API Key Rotation**: Implement key rotation strategy

## Related Documentation

- [Version History](VERSION_HISTORY.md) - Evolution from v1 to v3
- [Agent Optimization](../agents/AGENT_OPTIMIZATION.md) - LLM-powered agent details
- [Price API Integration](../integration/PRICE_API.md) - Price service documentation
- [Async Implementation](../implementation/ASYNC_NEWS.md) - Async/await patterns

---

**Next**: See [Version History](VERSION_HISTORY.md) to understand how we got here.
