# Real-Time Price API Integration

## Overview

The system now supports **real-time price data** from external APIs:
- **Metal Price API** (metalpriceapi.com) - Commodities (gold, silver, platinum, palladium)
- **Forex Rate API** (forexrateapi.com) - Forex pairs and cryptocurrency

## Features

✅ **Automatic API Selection** - Detects asset type and uses appropriate API
✅ **Price Caching** - 60-second cache to avoid rate limits
✅ **Graceful Fallback** - Falls back to mock prices if APIs fail
✅ **Multiple Assets** - Supports forex, commodities, and crypto
✅ **Historical Data** - Access yesterday's rates and historical prices
✅ **OHLC Data** - Open/High/Low/Close prices for technical analysis
✅ **Enriched Price Context** - Combines current + historical + OHLC for LLM analysis

## Setup

### 1. Get Free API Keys

#### Metal Price API (for commodities)
1. Visit: https://metalpriceapi.com/
2. Sign up for free account
3. Copy your API key

**Supported Assets:**
- XAU (Gold)
- XAG (Silver)
- XPT (Platinum)
- XPD (Palladium)

#### Forex Rate API (for forex and crypto)
1. Visit: https://forexrateapi.com/
2. Sign up for free account
3. Copy your API key

**Supported Assets:**
- All major forex pairs (EUR/USD, GBP/USD, etc.)
- Cryptocurrencies (BTC, ETH, etc.)

### 2. Configure Environment

Add your API keys to `.env` file:

```bash
# Copy example
cp .env.example .env

# Edit .env and add your keys
METAL_PRICE_API_KEY=your_metal_api_key_here
FOREX_RATE_API_KEY=your_forex_api_key_here
```

### 3. Test Integration

```bash
python3 test_price_api.py
```

Expected output:
```
✅ BOTH APIs WORKING!
```

## Usage

### 1. Direct Price Fetching

```python
from agents.price_service import get_price_service

# Get price service
price_service = get_price_service()

# Fetch gold price
gold = price_service.get_price("XAU/USD")
print(f"Gold: ${gold['price']}")

# Fetch EUR/USD
eur = price_service.get_price("EUR/USD")
print(f"EUR/USD: ${eur['price']}")

# Fetch Bitcoin
btc = price_service.get_price("BTC/USD")
print(f"Bitcoin: ${btc['price']}")
```

### 2. Historical Rates (NEW!)

```python
# Get yesterday's rate
historical = price_service.get_historical_rates("EUR/USD", "yesterday")
print(f"Yesterday: ${historical['rate']}")

# Get specific date
historical = price_service.get_historical_rates("EUR/USD", "2025-01-28")
print(f"Jan 28: ${historical['rate']}")
```

### 3. OHLC Data (NEW!)

```python
# Get yesterday's OHLC
ohlc = price_service.get_ohlc("EUR/USD", "yesterday")
print(f"Open:  ${ohlc['open']}")
print(f"High:  ${ohlc['high']}")
print(f"Low:   ${ohlc['low']}")
print(f"Close: ${ohlc['close']}")

# Calculate trading range
range_pct = ((ohlc['high'] - ohlc['low']) / ohlc['low']) * 100
print(f"Range: {range_pct:.2f}%")
```

### 4. Enriched Price Data (NEW!)

```python
# Get current price + historical + OHLC in one call
enriched = price_service.get_enriched_price("EUR/USD")

print(f"Current: ${enriched['price']}")
print(f"24h Change: {enriched['historical']['price_change_pct']}%")
print(f"Yesterday's Close: ${enriched['ohlc']['close']}")
```

### 5. With Technical Agent (Enhanced!)

```python
from agents.technical_agent import TechnicalAgent
import asyncio

# Enable real prices and LLM analysis
agent = TechnicalAgent(use_real_prices=True, use_llm=True)

# Analyze with real data + historical context
result = asyncio.run(agent.analyze("XAU/USD"))

print(f"Price: ${result['data']['current_price']}")
print(f"Source: {result['data']['price_source']}")  # "real" or "mock"
print(f"Trend: {result['data']['trend']}")
print(f"Signal: {result['data']['signals']['overall']}")

# Historical context is now automatically included in LLM prompt!
# The agent receives current price, 24h change, and OHLC data
```

### With Full System

```python
from system import ForexAgentSystem

# System automatically uses real prices if APIs are configured
system = ForexAgentSystem()

# Analyze gold
result = system.analyze("Analyze gold trading")

# Check price source
tech_data = result["agent_results"]["technical"]["data"]
print(f"Price: ${tech_data['current_price']}")
print(f"Source: {tech_data['price_source']}")
```

## API Response Formats

### Metal Price API

**Request:**
```
GET https://api.metalpriceapi.com/v1/latest
  ?api_key=YOUR_KEY
  &base=USD
  &currencies=XAU
```

**Response:**
```json
{
  "success": true,
  "base": "USD",
  "timestamp": 1762300799,
  "rates": {
    "XAU": 0.0002502133
  }
}
```

**Note:** Rate is USD per troy ounce, inverted to get XAU/USD price.

### Forex Rate API

**Request:**
```
GET https://api.forexrateapi.com/v1/latest
  ?api_key=YOUR_KEY
  &base=EUR
  &currencies=USD
```

**Response:**
```json
{
  "success": true,
  "base": "EUR",
  "timestamp": 1762300799,
  "rates": {
    "USD": 1.0850
  }
}
```

## Price Service Details

### Caching

Prices are cached for **60 seconds** to:
- Avoid hitting API rate limits
- Improve performance
- Reduce API costs

```python
# First call - hits API (~500ms)
price1 = price_service.get_price("XAU/USD")

# Second call - from cache (~1ms)
price2 = price_service.get_price("XAU/USD")

# Cache info
info = price_service.get_cache_info()
print(info["cached_pairs"])  # ['XAU/USD']
```

### Error Handling

The system gracefully handles:
- ❌ API down/timeout → Falls back to mock prices
- ❌ Invalid API key → Falls back to mock prices
- ❌ Rate limit exceeded → Uses cached price or mock
- ❌ Asset not supported → Falls back to mock prices

```python
# Even if APIs fail, system continues working
result = system.analyze("Analyze gold trading")
# Uses mock prices if real prices unavailable
```

## Free Tier Limits

### Metal Price API
- **Free Tier:** 100 requests/month
- **Rate Limit:** 1 request/second
- **Upgrade:** $9.99/month for 10,000 requests

### Forex Rate API
- **Free Tier:** 1,000 requests/month
- **Rate Limit:** 10 requests/minute
- **Upgrade:** $12/month for 100,000 requests

**💡 Tip:** With 60-second caching, you can analyze ~100 pairs/hour on free tier!

## Performance

| Operation | Time | Notes |
|-----------|------|-------|
| First fetch (uncached) | ~500ms | API request |
| Cached fetch | ~1ms | From memory |
| Cache duration | 60s | Configurable |
| Fallback to mock | 0ms | Instant |

## Troubleshooting

### Issue: API Keys Not Working

**Symptoms:**
```
⚠️  Metal Price API request failed: 403 Client Error: Forbidden
```

**Solutions:**
1. Check API key is correct in `.env`
2. Verify API key hasn't expired
3. Check free tier limits
4. Get new API keys from provider

### Issue: No .env File

**Symptoms:**
```
⚠️  Failed to get real price, using mock data
```

**Solution:**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

### Issue: Rate Limit Exceeded

**Symptoms:**
```
⚠️  Forex Rate API error: Rate limit exceeded
```

**Solutions:**
1. Wait 1 minute (rate limit resets)
2. Increase cache duration in `price_service.py`
3. Upgrade to paid tier
4. System automatically falls back to mock prices

## Examples

See `examples/real_prices.py` for comprehensive examples:

```bash
python3 examples/real_prices.py
```

Includes:
1. Direct price fetching
2. Technical agent with real prices
3. Real vs mock comparison
4. Full system integration
5. Cache performance demo
6. Multi-asset analysis

## Development

### Disable Real Prices

For testing without API keys:

```python
# Disable in technical agent
agent = TechnicalAgent(use_real_prices=False)

# Or set environment variable
os.environ["USE_MOCK_PRICES"] = "true"
```

### Add New API

To add support for another price API:

1. Create new method in `PriceService`
2. Update `get_price()` routing logic
3. Add API key to `.env.example`
4. Update documentation

### Custom Cache Duration

Edit `price_service.py`:

```python
class PriceService:
    CACHE_DURATION = 300  # 5 minutes instead of 60 seconds
```

## Cost Estimation

**Example: 100 analyses per day**

With caching (60s):
- Unique pairs per hour: ~60
- API calls per day: ~1,440
- Monthly API calls: ~43,200

**Free tier sufficient!** (100,000 requests/month combined)

Without caching:
- API calls per day: 300 (3 agents × 100 analyses)
- Monthly API calls: 9,000

Still within free tier limits.

## Security

**⚠️ IMPORTANT:**
- Never commit `.env` file to git
- Keep API keys secret
- Rotate keys if compromised
- Use environment variables in production

## Support

- Metal Price API: https://metalpriceapi.com/documentation
- Forex Rate API: https://forexrateapi.com/documentation

---

**Ready to use real market data!** 📊💹
