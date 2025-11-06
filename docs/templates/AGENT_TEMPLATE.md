# [Agent Name] Agent

**Version Added**: v[X]
**Last Updated**: [Date]
**Status**: [In Development | Complete | Deprecated]
**File**: `agents/[agent_name].py`

## Overview

[Brief description of what this agent does and why it exists]

## Purpose

[Detailed explanation of the agent's role in the system]

## Technology Stack

- **LLM**: [Gemini 2.5 Flash | Other]
- **Data Sources**: [APIs, Services, etc.]
- **Execution**: [Sync | Async]
- **Dependencies**: [List key dependencies]

## Input

### Parameters

```python
pair: str                           # Trading pair (e.g., "EUR/USD")
query_context: Dict[str, Any]       # Optional context from query parser
# [Add other parameters]
```

### Example

```python
pair = "EUR/USD"
query_context = {
    "asset_type": "forex",
    "timeframe": "short_term",
    "user_intent": "trading_signal"
}
```

## Output

### Structure

```json
{
  "success": true,
  "agent": "[AgentName]",
  "data": {
    // Agent-specific data fields
  },
  "summary": "Human-readable summary of analysis"
}
```

### Error Response

```json
{
  "success": false,
  "agent": "[AgentName]",
  "error": "Description of what went wrong"
}
```

### Example Output

```json
{
  "success": true,
  "agent": "[AgentName]",
  "data": {
    // Actual example output
  },
  "summary": "Example summary..."
}
```

## Implementation

### Class Definition

```python
class [AgentName]Agent:
    """
    [Description of agent]

    Attributes:
        [List key attributes]
    """

    def __init__(self, **kwargs):
        """
        Initialize [AgentName] agent.

        Args:
            [List arguments]
        """
        pass

    async def analyze(self, pair: str, query_context: dict = None) -> dict:
        """
        [Description of analyze method]

        Args:
            pair: Trading pair to analyze
            query_context: Optional context from query parser

        Returns:
            Dict with agent results
        """
        try:
            # Implementation
            return {
                "success": True,
                "agent": "[AgentName]",
                "data": {},
                "summary": ""
            }
        except Exception as e:
            return {
                "success": False,
                "agent": "[AgentName]",
                "error": str(e)
            }
```

## Features

- ✅ [Feature 1]
- ✅ [Feature 2]
- ⏳ [Planned feature]
- ❌ [Not supported]

## Data Sources

### Primary Sources
1. **[Source Name]**
   - URL: [API URL]
   - Purpose: [What data it provides]
   - Rate Limits: [Limits]
   - Cost: [Free tier / Pricing]

### Fallback Strategy
1. Try primary source
2. Use cached data (if available)
3. [Fallback option]
4. Return error result

## Algorithm/Logic

[Describe the key algorithm or decision-making logic]

### Step-by-Step Process

1. **[Step 1 Name]**
   - [Description]
   - [Input required]
   - [Output produced]

2. **[Step 2 Name]**
   - [Description]

3. **[Final Step]**
   - [Description]

## Integration with LangGraph

### State Updates

```python
# What this agent reads from state
pair = state["pair"]
query_context = state.get("query_context")

# What this agent writes to state
return {
    "[agent_name]_result": agent_result
}
```

### Node Function

```python
async def [agent_name]_node(state, config):
    """
    LangGraph node for [AgentName] agent.

    Args:
        state: Current ForexAgentState
        config: LangGraph configuration

    Returns:
        State updates from agent
    """
    agent = [AgentName]Agent()
    result = await agent.analyze(state["pair"], state.get("query_context"))

    return {"[agent_name]_result": result}
```

### Workflow Integration

```python
# In graph/workflow.py

# Add node
workflow.add_node("[agent_name]", [agent_name]_node)

# Add edges
workflow.add_edge("[previous_node]", "[agent_name]")
workflow.add_edge("[agent_name]", "[next_node]")
```

## Usage

### Standalone Usage

```python
from agents.[agent_name] import [AgentName]Agent
import asyncio

# Initialize agent
agent = [AgentName]Agent(
    # configuration parameters
)

# Run analysis
result = await agent.analyze("EUR/USD")

# Check results
if result["success"]:
    print(result["data"])
else:
    print(f"Error: {result['error']}")
```

### Within System

```python
from system import ForexAgentSystem

system = ForexAgentSystem()
result = system.analyze("Analyze EUR/USD")

# Access agent result
[agent_name]_data = result["agent_results"]["[agent_name]"]["data"]
print([agent_name]_data)
```

## Testing

### Unit Tests

```bash
# Test agent standalone
python test_[agent_name].py
```

### Test Cases

```python
import pytest
from agents.[agent_name] import [AgentName]Agent

@pytest.mark.asyncio
async def test_[agent_name]_success():
    """Test successful analysis."""
    agent = [AgentName]Agent()
    result = await agent.analyze("EUR/USD")

    assert result["success"] == True
    assert "data" in result
    assert "summary" in result

@pytest.mark.asyncio
async def test_[agent_name]_error_handling():
    """Test error handling."""
    agent = [AgentName]Agent()
    result = await agent.analyze("INVALID/PAIR")

    # Should return error result, not raise exception
    assert result["success"] == False
    assert "error" in result
```

## Performance

### Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| Execution Time | [X]ms | [Conditions] |
| API Calls | [X] | Per analysis |
| Cache Hit Rate | [X]% | [When applicable] |
| Cost per Analysis | $[X] | [Breakdown] |

### Optimization Tips

1. **[Optimization 1]**
   - [Description]
   - [Impact]

2. **[Optimization 2]**
   - [Description]

## Error Handling

### Common Errors

1. **[Error Type]**
   - **Cause**: [Why it happens]
   - **Solution**: [How to fix]
   - **Fallback**: [What agent does]

2. **[Error Type]**
   - **Cause**: [Why it happens]
   - **Solution**: [How to fix]

### Error Categories

- **Network Errors**: [How handled]
- **API Errors**: [How handled]
- **Data Validation Errors**: [How handled]
- **Rate Limit Errors**: [How handled]

## Configuration

### Environment Variables

```bash
# Required
[VAR_NAME]=[description]

# Optional
[VAR_NAME]=[description]  # Default: [value]
```

### Agent Parameters

```python
agent = [AgentName]Agent(
    param1="value1",     # [Description]
    param2=True,         # [Description]
)
```

## Cost Analysis

### API Costs

- **[API Name]**: $[X] per [unit]
- **Gemini LLM**: $[X] per analysis
- **Google Search**: $[X] per search (if applicable)

**Total**: ~$[X] per analysis

### Cost Optimization

- [Strategy 1]
- [Strategy 2]

## Limitations

### Current Limitations

1. **[Limitation 1]**
   - [Description]
   - [Workaround if any]

2. **[Limitation 2]**
   - [Description]

### Future Enhancements

- [ ] [Enhancement 1]
- [ ] [Enhancement 2]
- [ ] [Enhancement 3]

## Dependencies

### Python Packages

```python
# Core
google-genai>=0.1.0      # [Purpose]
asyncio                   # [Purpose]

# Optional
[package]                 # [Purpose]
```

### External Services

- **[Service Name]**: [Purpose and signup link]

## Examples

### Example 1: [Description]

```python
# [Code example]
```

**Output**:
```json
{
  // Expected output
}
```

### Example 2: [Description]

```python
# [Code example]
```

## Troubleshooting

### Issue: [Problem Description]

**Symptoms**:
```
[Error message or behavior]
```

**Solution**:
```bash
# Steps to fix
```

### Issue: [Problem Description]

**Symptoms**: [Description]

**Solution**: [Description]

## Related Documentation

- [Link to related agent docs]
- [Link to integration docs]
- [Link to system architecture]

## Changelog

### v[X] - [Date]
- [Change 1]
- [Change 2]

### v[X-1] - [Date]
- Initial implementation

## Support

For questions or issues:
1. Check [troubleshooting section](#troubleshooting)
2. Review [related documentation](#related-documentation)
3. Open GitHub issue

---

**Maintained by**: [Team/Person]
**Created**: [Date]
**Last Review**: [Date]
