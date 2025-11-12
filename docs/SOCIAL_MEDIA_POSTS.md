# Social Media Post Formatter

Generate professional, platform-optimized social media posts from trading analysis results.

## Overview

The social media formatter converts trading analysis results into ready-to-post content for:
- **Twitter/X** (280 char limit, concise signals)
- **Telegram** (markdown support, detailed analysis)
- **Facebook** (educational tone, broader audience)

All posts include:
- ✅ Professional FX trader voice
- ✅ Automatic disclaimers
- ✅ Platform-specific formatting
- ✅ Conditional trade parameters (only for signals)

## Quick Start

```python
from system import ForexAgentSystem
from utils.social_formatter import format_for_twitter, format_for_telegram, format_for_facebook

# 1. Run analysis
system = ForexAgentSystem()
result = system.analyze("EUR/USD")

# 2. Generate posts
twitter_post = format_for_twitter(result)
telegram_post = format_for_telegram(result)
facebook_post = format_for_facebook(result)

# 3. Share on your platforms
print(twitter_post)
```

## API Reference

### `format_for_twitter(result, include_trade_params=True, custom_hashtags=None)`

Generates a Twitter/X post (max 280 characters).

**Parameters:**
- `result` (dict): Analysis result from `ForexAgentSystem.analyze()`
- `include_trade_params` (bool): Include entry/stop/target prices (default: True)
- `custom_hashtags` (list): Custom hashtags (default: ["#Forex", "#Trading", "#PAIR"])

**Returns:** String (≤280 chars)

**Example:**
```python
twitter_post = format_for_twitter(
    result,
    include_trade_params=True,
    custom_hashtags=["#EURUSD", "#ForexSignals", "#DayTrading"]
)
```

**Output:**
```
🟢 EUR/USD BUY @ 1.085
🎯 Target: 1.095 | 🛡️ Stop: 1.08
Strong bullish momentum with ECB rate hike expectations.

⚠️ NFA | DYOR
#EURUSD #ForexSignals #DayTrading
```

---

### `format_for_telegram(result, include_trade_params=True, channel_name=None)`

Generates a Telegram post with markdown formatting.

**Parameters:**
- `result` (dict): Analysis result
- `include_trade_params` (bool): Include detailed trade parameters (default: True)
- `channel_name` (str): Optional channel name for branding

**Returns:** Markdown-formatted string

**Example:**
```python
telegram_post = format_for_telegram(
    result,
    include_trade_params=True,
    channel_name="FX Signals Pro"
)
```

**Output:**
```markdown
📡 **FX Signals Pro**

🟢 **EUR/USD - BUY Signal**

**Trade Parameters:**
• Entry: `1.085`
• Target: `1.095`
• Stop Loss: `1.08`
• Risk/Reward: `2.0`
• Confidence: `High`

**Analysis:**
Strong bullish momentum with ECB rate hike expectations.

**Sources:**
1. [ECB Policy Update](https://example.com/ecb)

---
⚠️ **Disclaimer:** This is not financial advice...
```

---

### `format_for_facebook(result, include_trade_params=True, educational_context=True)`

Generates a Facebook post with educational context.

**Parameters:**
- `result` (dict): Analysis result
- `include_trade_params` (bool): Include trade setup details (default: True)
- `educational_context` (bool): Add "What does this mean?" section (default: True)

**Returns:** Formatted string

**Example:**
```python
facebook_post = format_for_facebook(
    result,
    include_trade_params=True,
    educational_context=True
)
```

---

### `format_all_platforms(result, include_trade_params=True, custom_options=None)`

Generate posts for all platforms at once.

**Parameters:**
- `result` (dict): Analysis result
- `include_trade_params` (bool): Include trade parameters
- `custom_options` (dict): Platform-specific options
  - `twitter_hashtags`: List of hashtags
  - `telegram_channel`: Channel name
  - `facebook_educational`: Include educational context

**Returns:** Dictionary with keys: `'twitter'`, `'telegram'`, `'facebook'`

**Example:**
```python
posts = format_all_platforms(
    result,
    include_trade_params=True,
    custom_options={
        'twitter_hashtags': ["#Bitcoin", "#BTC", "#Crypto"],
        'telegram_channel': "Crypto Whale Signals",
        'facebook_educational': True
    }
)

print(posts['twitter'])
print(posts['telegram'])
print(posts['facebook'])
```

---

### `is_trading_signal(result)`

Helper function to detect if result contains an actionable trading signal.

**Returns:** `True` if decision is BUY/SELL and has entry/stop/target, otherwise `False`

**Example:**
```python
if is_trading_signal(result):
    # Show trade parameters
    post = format_for_twitter(result, include_trade_params=True)
else:
    # Informational only
    post = format_for_twitter(result, include_trade_params=False)
```

## Usage Patterns

### Pattern 1: Trading Signals (from frontend)

When user clicks "Analyze" and gets a BUY/SELL signal:

```python
# Backend API
result = system.analyze(user_query)

# Frontend receives result, user clicks "Share to Twitter"
if is_trading_signal(result):
    preview = format_for_twitter(result, include_trade_params=True)
else:
    preview = format_for_twitter(result, include_trade_params=False)

# Show preview to user
# User confirms → post to Twitter API
```

### Pattern 2: Informational Posts

When user wants to share market analysis without specific trade params:

```python
result = system.analyze("What's happening with gold?")

# Generate informational post (no trade params)
twitter_post = format_for_twitter(
    result,
    include_trade_params=False,
    custom_hashtags=["#Gold", "#MarketAnalysis"]
)
```

### Pattern 3: Batch Generation

Generate all formats for user to choose:

```python
result = system.analyze("EUR/USD")

# Generate all formats
posts = format_all_platforms(result)

# Store in database for user to access later
save_to_db({
    'analysis_id': result['id'],
    'twitter_post': posts['twitter'],
    'telegram_post': posts['telegram'],
    'facebook_post': posts['facebook']
})
```

## Platform-Specific Features

### Twitter/X
- **Character limit:** Strictly enforced 280 chars
- **Emoji indicators:** 🟢 BUY | 🔴 SELL | 📊 Analysis
- **Concise format:** Essential info only
- **Hashtags:** Automatically generated or custom
- **Disclaimer:** "⚠️ NFA | DYOR" (Not Financial Advice | Do Your Own Research)

### Telegram
- **Markdown support:** Bold, inline code, links
- **Structure:** Header → Parameters → Analysis → Sources → Disclaimer
- **Citations:** Includes up to 3 source links if available
- **Channel branding:** Optional channel name in header
- **Comprehensive disclaimer:** Full risk warning

### Facebook
- **Tone:** Professional but accessible
- **Educational context:** "What does this mean?" section
- **Detailed disclaimer:** Extended legal disclaimer
- **Hashtags:** #ForexTrading #MarketAnalysis #TradingEducation
- **Length:** ~300-500 words (longer form acceptable)

## Result Object Format

The formatter expects this structure from `system.analyze()`:

```python
{
    'pair': 'EUR/USD',                    # Required
    'decision': 'BUY' | 'SELL' | 'WAIT',  # Required
    'reasoning': 'Analysis text...',      # Required

    # Optional (for trading signals)
    'entry_price': 1.0850,
    'stop_loss': 1.0800,
    'target_price': 1.0950,
    'risk_reward_ratio': 2.0,
    'confidence': 'High' | 'Medium' | 'Low',

    # Optional (for sources)
    'citations': [
        {'title': 'Source Title', 'url': 'https://...'},
        ...
    ]
}
```

## Best Practices

### ✅ DO
- **Preview before posting:** Show formatted post to user first
- **Respect user intent:** Use `include_trade_params=False` for informational content
- **Customize hashtags:** Tailor to your audience
- **Store results:** Cache formatted posts to avoid re-processing
- **Check signal validity:** Use `is_trading_signal()` before showing trade params

### ❌ DON'T
- **Don't remove disclaimers:** They're automatically included and legally important
- **Don't modify formatting logic:** Platform limits are strictly enforced
- **Don't post without user confirmation:** Always show preview
- **Don't share API keys:** Posting to platforms requires user's own API credentials

## Frontend Integration Example

```javascript
// React component example
const ShareToSocial = ({ analysisResult }) => {
  const [twitterPost, setTwitterPost] = useState('');
  const [showPreview, setShowPreview] = useState(false);

  const handleShareToTwitter = async () => {
    // Call backend API to format post
    const response = await fetch('/api/format-social', {
      method: 'POST',
      body: JSON.stringify({
        platform: 'twitter',
        result: analysisResult,
        options: {
          include_trade_params: true,
          custom_hashtags: ['#EURUSD', '#ForexSignals']
        }
      })
    });

    const { formatted_post } = await response.json();
    setTwitterPost(formatted_post);
    setShowPreview(true);
  };

  return (
    <div>
      <button onClick={handleShareToTwitter}>Share to Twitter</button>

      {showPreview && (
        <div className="preview">
          <h3>Preview:</h3>
          <pre>{twitterPost}</pre>
          <button onClick={() => postToTwitterAPI(twitterPost)}>
            Confirm & Post
          </button>
        </div>
      )}
    </div>
  );
};
```

## Backend API Example

```python
from flask import Flask, request, jsonify
from system import ForexAgentSystem
from utils.social_formatter import format_for_twitter, format_for_telegram, format_for_facebook

app = Flask(__name__)

@app.route('/api/format-social', methods=['POST'])
def format_social_post():
    data = request.json
    platform = data['platform']
    result = data['result']
    options = data.get('options', {})

    if platform == 'twitter':
        post = format_for_twitter(
            result,
            include_trade_params=options.get('include_trade_params', True),
            custom_hashtags=options.get('custom_hashtags')
        )
    elif platform == 'telegram':
        post = format_for_telegram(
            result,
            include_trade_params=options.get('include_trade_params', True),
            channel_name=options.get('channel_name')
        )
    elif platform == 'facebook':
        post = format_for_facebook(
            result,
            include_trade_params=options.get('include_trade_params', True),
            educational_context=options.get('educational_context', True)
        )
    else:
        return jsonify({'error': 'Invalid platform'}), 400

    return jsonify({'formatted_post': post})
```

## Testing

Run the test suite:

```bash
python test_social_formatter.py
```

Run examples:

```bash
python examples/social_media_posts.py
```

## Character Limits Reference

| Platform | Hard Limit | Typical Length | Notes |
|----------|-----------|----------------|-------|
| Twitter  | 280 chars | 150-200 chars  | Strictly enforced |
| Telegram | None      | 500-800 chars  | Can be longer |
| Facebook | None      | 300-500 words  | Longer form OK |

## Compliance & Legal

All formatters automatically include appropriate disclaimers:

- **Twitter:** "⚠️ NFA | DYOR"
- **Telegram:** Full disclaimer paragraph
- **Facebook:** Extended legal disclaimer

**Important:** These disclaimers do NOT constitute legal advice. Consult with a licensed attorney regarding your specific regulatory requirements for financial content distribution.

## Troubleshooting

### Post too long for Twitter
- Shorten reasoning text automatically handled
- Consider using informational mode without trade params
- Use custom hashtags (fewer/shorter)

### Missing citations in Telegram
- Citations only included if present in result
- Synthesis agent must provide them
- Max 3 citations shown

### Markdown not rendering in Telegram
- Ensure using Telegram MarkdownV2 parser
- Test with Telegram Bot API
- Alternative: Use HTML mode

## Future Enhancements

Potential additions:
- LinkedIn post formatting (professional network)
- Discord embed formatting
- Reddit post formatting
- Image generation (chart overlays)
- Multi-language support
- A/B testing variants

## Support

Questions? Check:
- Example file: `examples/social_media_posts.py`
- Tests: `test_social_formatter.py`
- Main docs: `README.md`
