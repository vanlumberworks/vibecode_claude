# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v3] - 2025-11-05 - LLM-Powered Agents + Historical Data

### Added
- **LLM-Powered Agents**: All agents now use Gemini 2.5 Flash for intelligent analysis
- **Google Search Grounding**: News, Fundamental, and Synthesis agents use real-time data
- **Historical Price Data**: Technical agent now includes:
  - Yesterday's closing price
  - 24-hour price change percentage
  - OHLC data (Open/High/Low/Close)
- **Enriched Price Context**: Combined current + historical + OHLC for better analysis
- **Risk Agent LLM**: Risk validation now uses Gemini for nuanced decision-making
- **Real Economic Data**: Fundamental agent fetches GDP, inflation, interest rates via Google Search
- **Source Citations**: All agents provide source URLs for transparency

### Changed
- **News Agent**: Async execution with Google Search (previously mock data)
- **Technical Agent**: LLM analyzes price patterns (previously rule-based)
- **Fundamental Agent**: Real economic data via Google Search (previously mock)
- **Price Service**: Added `get_historical_rates()` and `get_ohlc()` methods
- **Agent Results**: All agents return structured JSON with `success`, `data`, `summary` fields

### Improved
- **Transparency**: Source citations for all data
- **Accuracy**: Real-time data instead of mock data
- **Reasoning**: LLMs provide detailed explanations for decisions
- **Context**: Historical data gives agents better decision-making context

### Cost Impact
- Increased from ~$0.010/analysis to ~$0.050/analysis
- Still very affordable for production use

### Documentation
- Added `docs/agents/AGENT_OPTIMIZATION.md` - LLM-powered agent details
- Added `docs/integration/PRICE_API.md` - Price API integration guide
- Added `docs/integration/API_AUTH_RESULTS.md` - API authentication research
- Added `docs/implementation/ASYNC_NEWS.md` - Async implementation details

---

## [v2] - 2025-11-04 - Natural Language + Parallel Execution

### Added
- **Natural Language Input**: Query parser converts text to structured context
  - "Analyze gold trading" → `{"pair": "XAU/USD", "asset_type": "commodity"}`
  - "Should I buy Bitcoin?" → `{"pair": "BTC/USD", "user_intent": "buy_signal"}`
- **Query Parser Node**: Gemini-powered natural language understanding
- **Parallel Analysis Node**: News, Technical, Fundamental agents run simultaneously
- **Enriched Context**: Agents receive rich context (asset_type, timeframe, intent)
- **Query Context State**: New state field for parsed query information

### Changed
- **Agent Execution**: Parallel (asyncio.gather) instead of sequential
- **Performance**: 3x faster (6s → 2s)
- **Input Format**: Flexible natural language instead of exact pair format only
- **ThreadPoolExecutor**: Replaced with async/await for better performance

### Improved
- **User Experience**: Natural language queries feel more intuitive
- **Speed**: Parallel execution dramatically faster
- **Context Awareness**: Agents have better understanding of user intent
- **Backward Compatible**: Old `analyze("EUR/USD")` calls still work

### Documentation
- Updated `docs/backend/ARCHITECTURE.md` with v1→v2 comparison
- Added natural language examples throughout docs

---

## [v1] - 2025-11-03 - Initial LangGraph + Gemini Implementation

### Added
- **LangGraph Orchestration**: Multi-agent workflow with state management
- **5 Specialized Agents**:
  1. News Agent - Market sentiment analysis (mock data)
  2. Technical Agent - Technical indicators (mock data)
  3. Fundamental Agent - Economic fundamentals (mock data)
  4. Risk Agent - Position sizing and validation
  5. Synthesis Agent - Final decision with Google Search grounding
- **Sequential Workflow**: News → Technical → Fundamental → Risk → Synthesis
- **Conditional Routing**: Skip synthesis if risk rejected
- **Synthesis with Google Search**: Real-time verification of mock agent data
- **Gemini Integration**: Synthesis agent uses Gemini 2.5 Flash
- **State Management**: `ForexAgentState` tracks all agent results
- **Error Handling**: Graceful failures for individual agents
- **Configuration**: Environment-based settings (.env file)

### Features
- Analyze forex pairs (e.g., EUR/USD)
- Mock data for News, Technical, Fundamental agents
- Real Google Search for Synthesis verification
- Position sizing based on account balance
- Risk/reward validation
- Stop loss validation (10-100 pips)
- Structured JSON output with reasoning

### Documentation
- Created `README.md` - Project overview and quick start
- Created `docs/setup/SETUP.md` - Installation guide
- Created initial architecture documentation

---

## Version Comparison

| Feature | v1 | v2 | v3 |
|---------|----|----|---- |
| **Input Format** | Exact pair only | Natural language | Natural language |
| **Agent Execution** | Sequential | Parallel (async) | Parallel (async) |
| **News Data** | Mock | Mock | Real (Google Search) |
| **Technical Data** | Mock | Mock | Real + Historical |
| **Fundamental Data** | Mock | Mock | Real (Google Search) |
| **Risk Analysis** | Rule-based | Rule-based | LLM-powered |
| **Synthesis** | Google Search | Google Search | Google Search |
| **Execution Time** | 3-6s | 1-2s | 1-2s |
| **Cost per Analysis** | $0.010 | $0.010 | $0.050 |
| **Context Awareness** | Low | High | Very High |
| **Data Quality** | Mock | Mock | Real |

---

## Upcoming Features (v4 Roadmap)

### Planned
- [ ] **Real-time News API**: Replace Google Search with dedicated news API
- [ ] **Calculated Technical Indicators**: Actual RSI, MACD calculations from price data
- [ ] **Multi-timeframe Analysis**: Short-term, medium-term, long-term views
- [ ] **Backtesting Framework**: Test strategies on historical data
- [ ] **Portfolio Management Agent**: Track multiple positions
- [ ] **Streaming Results**: Show agent results as they complete
- [ ] **User Preferences**: Remember user settings and risk tolerance
- [ ] **Performance Tracking**: Track decision accuracy over time

### Under Consideration
- [ ] **WebSocket Price Updates**: Real-time price streaming
- [ ] **Sentiment Analysis API**: Dedicated sentiment data source
- [ ] **Technical Indicator Library**: TA-Lib integration
- [ ] **Database Integration**: Store analysis history
- [ ] **Web UI**: Browser-based interface
- [ ] **Mobile App**: iOS/Android support
- [ ] **Broker Integration**: Execute trades automatically (with approval)

---

## Breaking Changes

### v2 → v3
- ✅ **No breaking changes** - Fully backward compatible
- All v2 code continues to work in v3
- New features automatically enabled when API keys configured

### v1 → v2
- ✅ **No breaking changes** - Fully backward compatible
- Old exact-pair format (`"EUR/USD"`) still works
- New natural language format available as addition

---

## Migration Guides

### Upgrading to v3 from v2

No code changes required! Just update dependencies and optionally add API keys:

```bash
# 1. Update dependencies
pip install -r requirements.txt --upgrade

# 2. (Optional) Add price API keys to .env for real data
METAL_PRICE_API_KEY=your_key_here
FOREX_RATE_API_KEY=your_key_here

# 3. Done! System automatically uses real data when keys present
```

### Upgrading to v2 from v1

No code changes required! Just update dependencies:

```bash
pip install -r requirements.txt --upgrade
```

Your existing code continues to work:
```python
# v1 code - still works in v2
system.analyze("EUR/USD")

# v2 feature - now available
system.analyze("Analyze gold trading")
```

---

## Maintenance Notes

### Documentation Organization (Nov 6, 2025)

Reorganized docs/ folder for better product context:

**New Structure**:
```
docs/
├── README.md                  # Navigation hub
├── architecture/              # System-wide architecture
├── agents/                    # Agent documentation
├── integration/               # External integrations
├── implementation/            # Implementation details
├── setup/                     # Installation guides
└── templates/                 # Documentation templates
```

**Moved Files**:
- `ARCHITECTURE.md` → `architecture/VERSION_HISTORY.md`
- Created new `architecture/SYSTEM_ARCHITECTURE.md` for current system
- `ASYNC_NEWS.md` → `implementation/ASYNC_NEWS.md`
- `API_AUTH_RESULTS.md` → `integration/API_AUTH_RESULTS.md`

**Added**:
- `docs/README.md` - Central navigation
- `docs/agents/README.md` - Agent overview
- `docs/architecture/SYSTEM_ARCHITECTURE.md` - Current architecture
- `docs/templates/AGENT_TEMPLATE.md` - Template for new agents
- `docs/templates/FEATURE_TEMPLATE.md` - Template for new features
- `CLAUDE.md` - Guidance for Claude Code

---

## Contributors

- **Core Development**: Van Lumberworks
- **Product Owner**: Van Lumberworks
- **Documentation**: Van Lumberworks

---

## Support

For questions or issues:
1. Check [documentation](docs/README.md)
2. Review this changelog
3. Open GitHub issue

---

**Last Updated**: November 6, 2025
**Current Version**: v3
