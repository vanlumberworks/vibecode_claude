"""News Agent - Analyzes market news and sentiment using Google Search."""

import os
import json
import time
from typing import Dict, Any
from datetime import datetime
from utils.logger import get_logger, log_error

logger = get_logger(__name__)


class NewsAgent:
    """
    Analyzes news and market sentiment for a currency pair using Google Search.

    Now powered by:
    - Gemini 2.5 Flash with Google Search grounding
    - Real-time news headlines from the web
    - Actual sentiment analysis based on current events
    - Source citations for all news items

    Previously: Used mock/template headlines
    Now: Uses real Google Search results!
    """

    def __init__(self):
        self.name = "NewsAgent"

    async def analyze(self, pair: str, config: dict = None) -> Dict[str, Any]:
        """
        Analyze news for the given currency pair using Google Search.

        Args:
            pair: Currency pair (e.g., "EUR/USD", "XAU/USD")
            config: Optional runtime configuration for streaming

        Returns:
            Dict with analysis results including real headlines and sources
        """
        from langgraph.config import get_stream_writer

        logger.info(f"📰 [NewsAgent] Starting analysis for {pair}")
        start_time = time.time()

        try:
            # Get stream writer for progress updates
            writer = get_stream_writer()

            from google import genai
            from google.genai import types

            # Emit progress: API initialization (10% progress)
            writer({"agent_progress": {
                "agent": "news",
                "step": "initializing_api",
                "message": "Initializing Gemini API",
                "progress_percentage": 10,
                "execution_start_time": datetime.utcnow().isoformat() + "Z"
            }})

            # Get API key
            api_key = os.getenv("GOOGLE_AI_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_AI_API_KEY not found in environment")

            # Initialize Gemini client
            client = genai.Client(api_key=api_key)

            # Extract currencies for better search
            base, quote = self._parse_pair(pair)

            # Emit progress: Building prompt (25% progress)
            writer({"agent_progress": {
                "agent": "news",
                "step": "building_prompt",
                "message": f"Building search prompt for {pair}",
                "progress_percentage": 25
            }})

            # Build search-powered analysis prompt
            prompt = self._build_news_prompt(pair, base, quote)

            # Configure Google Search grounding
            grounding_tool = types.Tool(google_search=types.GoogleSearch())

            config_gemini = types.GenerateContentConfig(
                temperature=0.2,  # Low temperature for factual news analysis
                # NOTE: Cannot use response_mime_type with tools
                tools=[grounding_tool],
                thinking_config=types.ThinkingConfig(thinking_budget=0),  # Speed over thinking
            )

            # Emit progress: Starting Google Search (40% progress)
            writer({"agent_progress": {
                "agent": "news",
                "step": "google_search",
                "message": f"Searching web for {pair} news and sentiment",
                "progress_percentage": 40
            }})

            # Generate analysis with Google Search
            logger.debug(f"📰 [NewsAgent] Calling Gemini API with Google Search for {pair}")
            response = client.models.generate_content(model="gemini-2.5-flash", contents=[prompt], config=config_gemini)
            logger.debug(f"📰 [NewsAgent] Received response from Gemini (length: {len(response.text)} chars)")

            # Extract grounding metadata FIRST (for web search event)
            sources = []
            search_queries = []
            if response.candidates[0].grounding_metadata:
                metadata = response.candidates[0].grounding_metadata
                search_queries = metadata.web_search_queries or []
                if metadata.grounding_chunks:
                    sources = [{"title": c.web.title, "url": c.web.uri} for c in metadata.grounding_chunks]

                # Emit web_search event with grounding results (60% progress)
                writer({"web_search": {
                    "agent": "news",
                    "queries": search_queries,
                    "sources": sources,
                    "source_count": len(sources)
                }})
                writer({"agent_progress": {
                    "agent": "news",
                    "step": "search_complete",
                    "message": f"Found {len(sources)} sources from web search",
                    "progress_percentage": 60
                }})

            # Emit progress: Processing results (75% progress)
            writer({"agent_progress": {
                "agent": "news",
                "step": "processing_results",
                "message": "Processing search results and analyzing sentiment",
                "progress_percentage": 75
            }})


            # Parse response (extract JSON from potential markdown code blocks)
            response_text = response.text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]  # Remove ```json
            elif response_text.startswith("```"):
                response_text = response_text[3:]  # Remove ```

            if response_text.endswith("```"):
                response_text = response_text[:-3]  # Remove trailing ```

            analysis = json.loads(response_text.strip())

            # Emit intermediate data as soon as we parse it (90% progress)
            sentiment_score = analysis.get("sentiment_score", 0.0)
            sentiment = analysis.get("sentiment", "neutral")
            headlines_count = len(analysis.get("headlines", []))

            writer({"agent_progress": {
                "agent": "news",
                "step": "analysis_complete",
                "message": f"Sentiment: {sentiment} ({sentiment_score:+.2f}), Headlines: {headlines_count}",
                "progress_percentage": 90,
                "intermediate_data": {
                    "sentiment": sentiment,
                    "sentiment_score": sentiment_score,
                    "headlines_count": headlines_count,
                    "impact": analysis.get("impact", "medium")
                }
            }})

            elapsed = time.time() - start_time
            execution_end_time = datetime.utcnow().isoformat() + "Z"
            logger.info(f"✅ [NewsAgent] Analysis complete in {elapsed:.2f}s - Headlines: {headlines_count}, Sentiment: {sentiment}, Sources: {len(sources)}")

            # Emit final completion (100% progress)
            writer({"agent_progress": {
                "agent": "news",
                "step": "complete",
                "message": f"News analysis complete in {elapsed:.2f}s",
                "progress_percentage": 100,
                "execution_end_time": execution_end_time,
                "execution_time": elapsed
            }})

            # Build result with grounding metadata
            return {
                "success": True,
                "agent": self.name,
                "data": {
                    "pair": pair,
                    "headlines": analysis.get("headlines", []),
                    "sentiment_score": sentiment_score,
                    "sentiment": sentiment,
                    "impact": analysis.get("impact", "medium"),
                    "news_count": headlines_count,
                    "analysis_timestamp": datetime.utcnow().isoformat(),
                    "summary": analysis.get("summary", "No summary available"),
                    "key_events": analysis.get("key_events", []),
                    # Grounding metadata
                    "search_queries": search_queries,
                    "sources": sources,
                    "data_source": "google_search",  # Indicates real data
                    # Execution timing
                    "execution_time": elapsed,
                    "execution_start_time": start_time,
                    "execution_end_time": execution_end_time
                },
            }

        except Exception as e:
            elapsed = time.time() - start_time
            log_error(logger, e, "NewsAgent.analyze")
            logger.error(f"❌ [NewsAgent] Failed after {elapsed:.2f}s for {pair}")

            return {
                "success": False,
                "agent": self.name,
                "error": str(e),
                "data": {},
            }

    def _parse_pair(self, pair: str) -> tuple:
        """Parse trading pair into base and quote currencies."""
        if "/" in pair:
            base, quote = pair.split("/")
        else:
            # Assume format like "EURUSD"
            base = pair[:3]
            quote = pair[3:]
        return base.upper(), quote.upper()

    def _build_news_prompt(self, pair: str, base: str, quote: str) -> str:
        """Build the news analysis prompt for Gemini with Google Search."""
        return f"""You are a forex news analyst with real-time access to Google Search.

TASK: Analyze current news and market sentiment for {pair} ({base}/{quote})

Use Google Search to find:
1. Recent news headlines (last 24-48 hours) about:
   - "{pair} forex news"
   - "{base} currency news"
   - "{quote} currency news"
   - "{base} central bank"
   - "{base} economy"

2. Major events affecting the currencies:
   - Central bank decisions
   - Economic data releases
   - Geopolitical events
   - Market sentiment shifts

ANALYSIS REQUIREMENTS:

1. **Headlines** (3-5 most relevant)
   - Extract ACTUAL recent headlines from search results
   - Include publication date/time if available
   - Focus on market-moving news

2. **Sentiment Analysis**
   - Analyze overall market sentiment from headlines
   - Score: -1.0 (very bearish) to +1.0 (very bullish)
   - Consider: tone, events, analyst opinions

3. **Impact Assessment**
   - high: Major events (rate decisions, GDP, crises)
   - medium: Notable events (inflation data, forecasts)
   - low: Minor events (routine statements)

4. **Key Events**
   - List 2-3 most important recent events
   - Include dates and brief descriptions

OUTPUT FORMAT (JSON):
{{
  "headlines": [
    {{
      "title": "Actual headline from search results",
      "date": "2025-11-05" (if available, else "recent"),
      "sentiment": "bullish|bearish|neutral",
      "source": "Publication name if available"
    }}
  ],
  "sentiment_score": 0.0 to 1.0 or -1.0 to 0.0,
  "sentiment": "bullish|bearish|neutral",
  "impact": "high|medium|low",
  "key_events": [
    "Event 1: Description",
    "Event 2: Description"
  ],
  "summary": "Brief summary of market sentiment and why (1-2 sentences)"
}}

CRITICAL:
- Use ONLY information from Google Search results
- Do NOT make up headlines or events
- If no recent news found, indicate in summary
- Be objective and fact-based
- Sentiment must reflect actual market conditions

Analyze now: {pair}
"""
