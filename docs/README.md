# Documentation Index

**Current Version**: v3 (LLM-Powered Agents + Historical Data)
**Last Updated**: November 6, 2025

## Quick Navigation

### Getting Started
- [Setup Guide](setup/SETUP.md) - Installation and configuration
- [Architecture Overview](architecture/SYSTEM_ARCHITECTURE.md) - System design and workflow
- [Quick Start Examples](../examples/) - Code examples to get started

### Core Concepts

#### System Architecture
- [System Architecture](architecture/SYSTEM_ARCHITECTURE.md) - LangGraph workflow, state management, and agent orchestration
- [Version Evolution](architecture/VERSION_HISTORY.md) - v1 → v2 → v3 changes

#### Agent Documentation
- [Agent Overview](agents/README.md) - All agents and their capabilities
- [LLM-Powered Agents](agents/AGENT_OPTIMIZATION.md) - Current v3 implementation with Gemini + Google Search

#### Integration Guides
- [Price API Integration](integration/PRICE_API.md) - Real-time price data from external APIs
- [API Authentication](integration/API_AUTH_RESULTS.md) - Authentication methods and troubleshooting

#### Implementation Details
- [Async Implementation](implementation/ASYNC_NEWS.md) - Async/await pattern and parallel execution

## Documentation Structure

```
docs/
├── README.md                          # This file - navigation hub
│
├── setup/                             # Installation and configuration
│   └── SETUP.md                      # Setup guide
│
├── architecture/                      # System-wide architecture
│   ├── SYSTEM_ARCHITECTURE.md        # Current architecture (moved from backend/)
│   └── VERSION_HISTORY.md            # v1 → v2 → v3 evolution
│
├── agents/                           # Agent-specific documentation
│   ├── README.md                     # Agent overview
│   └── AGENT_OPTIMIZATION.md         # LLM-powered agent implementation
│
├── integration/                      # External integrations
│   ├── PRICE_API.md                 # Price API integration
│   └── API_AUTH_RESULTS.md          # API authentication research
│
├── implementation/                   # Implementation details
│   └── ASYNC_NEWS.md                # Async/await implementation
│
└── templates/                        # Documentation templates
    ├── AGENT_TEMPLATE.md            # Template for new agents
    └── FEATURE_TEMPLATE.md          # Template for new features
```

## Current System Version: v3

### What's in v3?
- ✅ LLM-powered agents (News, Technical, Fundamental)
- ✅ Google Search grounding for real-time data
- ✅ Historical price data (OHLC, 24h change)
- ✅ Async/await parallel execution
- ✅ Natural language query parsing
- ✅ Real economic data and news headlines

### Previous Versions
- **v2**: Natural language input + parallel execution (replaced ThreadPoolExecutor with asyncio)
- **v1**: Sequential execution + exact pair format only

See [Version History](architecture/VERSION_HISTORY.md) for detailed evolution.

## Key Concepts

### LangGraph Workflow
1. **Query Parser** - Natural language → structured context
2. **Parallel Analysis** - News, Technical, Fundamental agents run simultaneously
3. **Risk Assessment** - Validates trade parameters
4. **Synthesis** - Gemini + Google Search for final decision

### Agent Types
- **News Agent**: Real headlines via Google Search + sentiment analysis
- **Technical Agent**: Price data + historical OHLC + technical indicators
- **Fundamental Agent**: Economic data (GDP, inflation, interest rates)
- **Risk Agent**: Position sizing and trade validation
- **Synthesis Agent**: Final decision with citations

### Data Sources
- **Google Search**: Real-time news and economic data
- **Metal Price API**: Commodity prices (gold, silver, platinum, palladium)
- **Forex Rate API**: Forex pairs and cryptocurrency prices
- **Gemini 2.5 Flash**: LLM analysis and reasoning

## Development Workflow

### For New Features
1. Review [System Architecture](architecture/SYSTEM_ARCHITECTURE.md)
2. Use [Feature Template](templates/FEATURE_TEMPLATE.md) to document
3. Update relevant agent docs
4. Update this README if structure changes

### For New Agents
1. Review [Agent Overview](agents/README.md)
2. Use [Agent Template](templates/AGENT_TEMPLATE.md) to document
3. Update [Agent Optimization](agents/AGENT_OPTIMIZATION.md) if using LLM
4. Update this README navigation

### For Integrations
1. Create doc in `integration/` folder
2. Document authentication method
3. Document error handling and fallbacks
4. Add to this README navigation

## Documentation Standards

### File Naming
- Use `SCREAMING_SNAKE_CASE.md` for major docs
- Use `README.md` for folder indices
- Use descriptive names (not `DOC1.md`, `DOC2.md`)

### Document Structure
All major documentation should include:
1. **Overview** - What this document covers
2. **Last Updated** - Date stamp
3. **Current Status** - Is this current or archived?
4. **Content** - The actual documentation
5. **Related Docs** - Links to related documentation

### Version Tracking
- Always specify which version features were added
- Use ✅ for implemented features
- Use ⏳ for planned features
- Use ❌ for deprecated features

### Code Examples
- Include working code examples
- Show both input and expected output
- Include error cases and fallbacks

## Maintenance

### Monthly Review Checklist
- [ ] Verify all links work
- [ ] Check for outdated version references
- [ ] Update "Last Updated" dates
- [ ] Archive obsolete documentation
- [ ] Update version numbers if new release

### Before Each Release
- [ ] Update VERSION_HISTORY.md
- [ ] Update this README with new features
- [ ] Verify all examples still work
- [ ] Update CLAUDE.md if architecture changed

## Common Tasks

### I want to...
- **Understand the system**: Start with [System Architecture](architecture/SYSTEM_ARCHITECTURE.md)
- **Set up the project**: See [Setup Guide](setup/SETUP.md)
- **Add a new agent**: Check [Agent Template](templates/AGENT_TEMPLATE.md)
- **Integrate an API**: Review [Price API Integration](integration/PRICE_API.md) as example
- **Understand version changes**: Read [Version History](architecture/VERSION_HISTORY.md)
- **Use real price data**: See [Price API](integration/PRICE_API.md)
- **Debug API issues**: Check [API Auth](integration/API_AUTH_RESULTS.md)

## Contributing to Documentation

When adding new documentation:

1. **Choose the right folder**:
   - System-wide changes → `architecture/`
   - Agent-specific → `agents/`
   - External APIs → `integration/`
   - Code patterns → `implementation/`

2. **Use templates**: Start with a template from `templates/`

3. **Update this README**: Add navigation links

4. **Cross-reference**: Link to related docs

5. **Version tag**: Specify which version the feature is in

## Questions?

- Check [CLAUDE.md](../CLAUDE.md) for development guidance
- Review [README.md](../README.md) for project overview
- See examples in [examples/](../examples/)

---

**Documentation maintained by**: Product Owner
**Last major reorganization**: November 6, 2025
