"""Report Agent - Generates comprehensive PDF-ready HTML reports using LLM."""

import os
import json
from typing import Dict, Any
from datetime import datetime


class ReportAgent:
    """
    Generates comprehensive trading analysis reports in PDF-ready HTML format.

    Uses Gemini 2.5 Flash to create narrative sections with professional formatting.

    Report Sections:
    - Executive Summary: High-level overview and key decision
    - Market Analysis: News sentiment and fundamental factors
    - Technical Analysis: Indicators, patterns, and signals
    - Risk Assessment: Position sizing and risk management
    - Trading Signals: Clear action items with parameters
    - References & Citations: Sources from grounding metadata
    - Disclaimer: Standard trading risk disclaimer

    Architecture:
    1. Collect all data from state (synthesis, agent results)
    2. Use Gemini to generate narrative HTML for each section
    3. Assemble final HTML with styling
    4. Return structured response with HTML content
    """

    def __init__(self):
        """Initialize Report Agent."""
        self.name = "ReportAgent"

    async def generate_report(
        self,
        decision: Dict[str, Any],
        query_context: Dict[str, Any],
        pair: str,
        news_result: Dict[str, Any] = None,
        technical_result: Dict[str, Any] = None,
        fundamental_result: Dict[str, Any] = None,
        risk_result: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Generate comprehensive HTML report from all analysis results.

        Args:
            decision: Final trading decision from synthesis node
            query_context: Parsed query context
            pair: Currency pair
            news_result: News agent analysis
            technical_result: Technical agent analysis
            fundamental_result: Fundamental agent analysis
            risk_result: Risk agent analysis

        Returns:
            Dict with success status, HTML content, and metadata
        """
        try:
            # Get API key
            api_key = os.getenv("GOOGLE_AI_API_KEY")
            if not api_key:
                return {
                    "success": False,
                    "agent": self.name,
                    "error": "GOOGLE_AI_API_KEY not configured",
                    "html": None,
                }

            from google import genai
            from google.genai import types

            # Initialize Gemini
            client = genai.Client(api_key=api_key)

            # Build comprehensive prompt
            prompt = self._build_report_prompt(
                decision=decision,
                query_context=query_context,
                pair=pair,
                news_result=news_result,
                technical_result=technical_result,
                fundamental_result=fundamental_result,
                risk_result=risk_result,
            )

            # Configure Gemini (no search needed, we have all data)
            config = types.GenerateContentConfig(
                temperature=0.4,  # Slightly creative for narrative
                response_mime_type="application/json",
                thinking_config=types.ThinkingConfig(thinking_budget=0),
            )

            # Generate report content
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt],
                config=config
            )

            # Parse LLM response
            report_content = json.loads(response.text)

            # Generate HTML from content
            html = self._generate_html(
                report_content=report_content,
                decision=decision,
                pair=pair,
                query_context=query_context,
            )

            return {
                "success": True,
                "agent": self.name,
                "html": html,
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "pair": pair,
                    "action": decision.get("action", "UNKNOWN"),
                    "sections": list(report_content.keys()),
                    "word_count": len(html.split()),
                },
            }

        except Exception as e:
            print(f"  ⚠️  Report Agent error: {str(e)}")
            return {
                "success": False,
                "agent": self.name,
                "error": str(e),
                "html": None,
            }

    def _build_report_prompt(
        self,
        decision: Dict[str, Any],
        query_context: Dict[str, Any],
        pair: str,
        news_result: Dict[str, Any],
        technical_result: Dict[str, Any],
        fundamental_result: Dict[str, Any],
        risk_result: Dict[str, Any],
    ) -> str:
        """Build comprehensive prompt for report generation."""

        # Extract data with safe defaults
        action = decision.get("action", "WAIT")
        confidence = decision.get("confidence", 0.0)
        reasoning = decision.get("reasoning", {})
        trade_params = decision.get("trade_parameters", {})
        grounding = decision.get("grounding_metadata", {})

        # Agent results
        news_data = news_result.get("data", {}) if news_result else {}
        tech_data = technical_result.get("data", {}) if technical_result else {}
        fund_data = fundamental_result.get("data", {}) if fundamental_result else {}
        risk_data = risk_result.get("data", {}) if risk_result else {}

        # Format sources for citation
        sources = grounding.get("sources", [])
        sources_text = "\n".join([f"- {s.get('title', 'Unknown')}: {s.get('url', 'N/A')}" for s in sources])

        return f"""You are an expert financial report writer. Generate a comprehensive trading analysis report.

REPORT CONTEXT:
- Pair: {pair}
- Query: {query_context.get('user_intent', 'Trading analysis')}
- Asset Type: {query_context.get('asset_type', 'forex')}
- Timeframe: {query_context.get('timeframe', 'Not specified')}
- User Risk Tolerance: {query_context.get('risk_tolerance', 'medium')}

FINAL DECISION:
- Action: {action}
- Confidence: {confidence * 100:.1f}%
- Entry Price: {trade_params.get('entry_price', 'N/A')}
- Stop Loss: {trade_params.get('stop_loss', 'N/A')}
- Take Profit: {trade_params.get('take_profit', 'N/A')}
- Position Size: {trade_params.get('position_size', 'N/A')}

DECISION REASONING:
- Summary: {reasoning.get('summary', 'No summary provided')}
- Web Verification: {reasoning.get('web_verification', 'N/A')}
- Key Factors: {', '.join(reasoning.get('key_factors', []))}
- Risks: {', '.join(reasoning.get('risks', []))}

NEWS ANALYSIS:
- Overall Sentiment: {news_data.get('overall_sentiment', 'neutral')}
- Recent Headlines: {', '.join([h.get('headline', '') for h in news_data.get('headlines', [])][:3])}
- Summary: {news_result.get('summary', 'No news analysis available') if news_result else 'N/A'}

TECHNICAL ANALYSIS:
- RSI: {tech_data.get('rsi', 'N/A')}
- MACD: {tech_data.get('macd', {}).get('histogram', 'N/A')}
- Moving Averages: {tech_data.get('moving_averages', {})}
- Overall Signal: {tech_data.get('signals', {}).get('overall', 'neutral')}
- Summary: {technical_result.get('summary', 'No technical analysis available') if technical_result else 'N/A'}

FUNDAMENTAL ANALYSIS:
- Economic Outlook: {fund_data.get('outlook', 'neutral')}
- Interest Rates: {fund_data.get('interest_rates', {})}
- GDP Growth: {fund_data.get('gdp_growth', 'N/A')}
- Inflation: {fund_data.get('inflation', 'N/A')}
- Summary: {fundamental_result.get('summary', 'No fundamental analysis available') if fundamental_result else 'N/A'}

RISK ASSESSMENT:
- Trade Approved: {risk_data.get('trade_approved', False)}
- Risk in Pips: {risk_data.get('risk_in_pips', 'N/A')}
- Dollar Risk: ${risk_data.get('dollar_risk', 'N/A')}
- Risk/Reward Ratio: {risk_data.get('risk_reward_ratio', 'N/A')}
- Position Size: {risk_data.get('position_size', 'N/A')} lots
- Risk Factors: {', '.join(risk_data.get('risk_factors', []))}
- Summary: {risk_result.get('summary', 'No risk analysis available') if risk_result else 'N/A'}

SOURCES & CITATIONS:
{sources_text if sources_text else 'No external sources cited'}

TASK: Generate comprehensive report content in JSON format with these sections:

1. **executive_summary** (2-3 paragraphs, ~150-200 words)
   - Lead with the final decision ({action}) and confidence level
   - Summarize the key rationale and supporting factors
   - Highlight the most critical information an investor needs to know
   - Professional tone, clear and decisive

2. **market_analysis** (3-4 paragraphs, ~200-250 words)
   - Synthesize news sentiment and fundamental factors
   - Explain current market conditions affecting {pair}
   - Discuss economic indicators and their implications
   - Connect news events to price action
   - Use specific data points from the analysis

3. **technical_analysis** (3-4 paragraphs, ~200-250 words)
   - Describe technical indicators (RSI, MACD, moving averages)
   - Explain what these indicators suggest about price direction
   - Identify key support/resistance levels
   - Discuss chart patterns or trends
   - Relate technical signals to the trading decision

4. **risk_assessment** (2-3 paragraphs, ~150-200 words)
   - Detail the risk management approach
   - Explain position sizing rationale
   - Discuss stop loss and take profit levels
   - Highlight key risk factors and mitigation strategies
   - Address any warnings or concerns

5. **trading_signals** (Structured list)
   - Clear, actionable trading recommendations
   - Specific entry, stop loss, and take profit levels
   - Position size and risk parameters
   - Timing considerations
   - Alternative scenarios (if applicable)

6. **key_takeaways** (4-6 bullet points)
   - Most important insights from the analysis
   - Critical factors influencing the decision
   - Main risks to monitor
   - Success criteria for the trade

OUTPUT FORMAT (JSON):
{{
  "executive_summary": "<p>The analysis recommends a <strong>{action}</strong> position on {pair} with a confidence level of {confidence * 100:.0f}%. This decision is based on...</p><p>Key supporting factors include...</p><p>The recommended trade parameters are...</p>",

  "market_analysis": "<p>Current market conditions for {pair} show...</p><p>News sentiment analysis reveals...</p><p>Fundamental factors indicate...</p><p>Economic indicators suggest...</p>",

  "technical_analysis": "<p>Technical indicators present a compelling case for...</p><p>The Relative Strength Index (RSI) at...</p><p>MACD analysis shows...</p><p>Moving averages indicate...</p>",

  "risk_assessment": "<p>Risk management for this trade involves...</p><p>Position sizing has been calculated at...</p><p>Key risk factors to monitor include...</p>",

  "trading_signals": {{
    "action": "{action}",
    "entry_price": {trade_params.get('entry_price', 'null')},
    "stop_loss": {trade_params.get('stop_loss', 'null')},
    "take_profit": {trade_params.get('take_profit', 'null')},
    "position_size": {trade_params.get('position_size', 'null')},
    "risk_reward_ratio": {risk_data.get('risk_reward_ratio', 'null')},
    "confidence": {confidence},
    "timing": "Enter immediately / Wait for confirmation / Scale in gradually",
    "alternative_scenario": "If price reaches X, consider Y"
  }},

  "key_takeaways": [
    "First key insight about the analysis",
    "Second critical factor",
    "Third important consideration",
    "Fourth risk or opportunity",
    "Fifth monitoring point"
  ]
}}

CRITICAL REQUIREMENTS:
- Write in professional, objective financial analysis style
- Use specific data points and numbers from the analysis
- Be clear and decisive, avoid hedge language
- Format as valid HTML paragraphs with <p>, <strong>, <em> tags
- Keep paragraphs focused (3-5 sentences each)
- Use present tense for current conditions, past tense for historical data
- If data is missing or marked as "mock data", acknowledge uncertainty but still provide analysis
- Ensure all JSON values are properly escaped strings

Generate the report content now:"""

    def _generate_html(
        self,
        report_content: Dict[str, Any],
        decision: Dict[str, Any],
        pair: str,
        query_context: Dict[str, Any],
    ) -> str:
        """Generate complete PDF-ready HTML from report content."""

        # Extract data
        action = decision.get("action", "WAIT")
        confidence = decision.get("confidence", 0.0)
        trade_params = decision.get("trade_parameters", {})
        grounding = decision.get("grounding_metadata", {})

        # Color coding for action
        action_colors = {
            "BUY": "#10b981",   # Green
            "SELL": "#ef4444",  # Red
            "WAIT": "#f59e0b",  # Amber
        }
        action_color = action_colors.get(action, "#6b7280")

        # Format timestamp
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

        # Extract sections from LLM response
        exec_summary = report_content.get("executive_summary", "<p>No summary available</p>")
        market_analysis = report_content.get("market_analysis", "<p>No market analysis available</p>")
        technical_analysis = report_content.get("technical_analysis", "<p>No technical analysis available</p>")
        risk_assessment = report_content.get("risk_assessment", "<p>No risk assessment available</p>")
        trading_signals = report_content.get("trading_signals", {})
        key_takeaways = report_content.get("key_takeaways", [])

        # Format sources
        sources = grounding.get("sources", [])
        sources_html = ""
        if sources:
            sources_html = "<ul>"
            for source in sources:
                title = source.get("title", "Unknown Source")
                url = source.get("url", "#")
                sources_html += f'<li><a href="{url}" target="_blank">{title}</a></li>'
            sources_html += "</ul>"
        else:
            sources_html = "<p>No external sources cited in this analysis.</p>"

        # Format key takeaways
        takeaways_html = "<ul>"
        for takeaway in key_takeaways:
            takeaways_html += f"<li>{takeaway}</li>"
        takeaways_html += "</ul>"

        # Build HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trading Analysis Report - {pair}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #1f2937;
            background: #ffffff;
            padding: 40px;
            max-width: 1000px;
            margin: 0 auto;
        }}

        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 3px solid #e5e7eb;
        }}

        .header h1 {{
            font-size: 32px;
            color: #111827;
            margin-bottom: 10px;
        }}

        .header .subtitle {{
            font-size: 18px;
            color: #6b7280;
            margin-bottom: 15px;
        }}

        .header .timestamp {{
            font-size: 14px;
            color: #9ca3af;
        }}

        .decision-badge {{
            display: inline-block;
            padding: 12px 24px;
            font-size: 24px;
            font-weight: bold;
            color: white;
            background-color: {action_color};
            border-radius: 8px;
            margin: 20px 0;
        }}

        .confidence {{
            font-size: 16px;
            color: #6b7280;
            margin-top: 10px;
        }}

        .section {{
            margin-bottom: 35px;
            page-break-inside: avoid;
        }}

        .section h2 {{
            font-size: 24px;
            color: #111827;
            margin-bottom: 15px;
            padding-bottom: 8px;
            border-bottom: 2px solid #e5e7eb;
        }}

        .section p {{
            margin-bottom: 12px;
            text-align: justify;
        }}

        .section ul {{
            margin-left: 25px;
            margin-bottom: 12px;
        }}

        .section li {{
            margin-bottom: 8px;
        }}

        strong {{
            color: #111827;
            font-weight: 600;
        }}

        em {{
            font-style: italic;
            color: #4b5563;
        }}

        .trade-params {{
            background: #f9fafb;
            border-left: 4px solid {action_color};
            padding: 20px;
            margin: 20px 0;
            border-radius: 4px;
        }}

        .trade-params table {{
            width: 100%;
            border-collapse: collapse;
        }}

        .trade-params td {{
            padding: 10px;
            border-bottom: 1px solid #e5e7eb;
        }}

        .trade-params td:first-child {{
            font-weight: 600;
            color: #4b5563;
            width: 40%;
        }}

        .trade-params td:last-child {{
            color: #111827;
        }}

        .disclaimer {{
            background: #fef3c7;
            border: 1px solid #fbbf24;
            padding: 20px;
            margin-top: 40px;
            border-radius: 4px;
            font-size: 14px;
            color: #78350f;
        }}

        .disclaimer h3 {{
            color: #92400e;
            margin-bottom: 10px;
            font-size: 16px;
        }}

        a {{
            color: #2563eb;
            text-decoration: none;
        }}

        a:hover {{
            text-decoration: underline;
        }}

        @media print {{
            body {{
                padding: 20px;
            }}
            .section {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Trading Analysis Report</h1>
        <div class="subtitle">{pair} - {query_context.get('asset_type', 'Forex').upper()}</div>
        <div class="decision-badge">{action}</div>
        <div class="confidence">Confidence Level: {confidence * 100:.1f}%</div>
        <div class="timestamp">Generated: {timestamp}</div>
    </div>

    <div class="section">
        <h2>Executive Summary</h2>
        {exec_summary}
    </div>

    <div class="section">
        <h2>Trading Signals</h2>
        <div class="trade-params">
            <table>
                <tr>
                    <td>Recommended Action</td>
                    <td><strong style="color: {action_color};">{trading_signals.get('action', action)}</strong></td>
                </tr>
                <tr>
                    <td>Entry Price</td>
                    <td>{trading_signals.get('entry_price', trade_params.get('entry_price', 'N/A'))}</td>
                </tr>
                <tr>
                    <td>Stop Loss</td>
                    <td>{trading_signals.get('stop_loss', trade_params.get('stop_loss', 'N/A'))}</td>
                </tr>
                <tr>
                    <td>Take Profit</td>
                    <td>{trading_signals.get('take_profit', trade_params.get('take_profit', 'N/A'))}</td>
                </tr>
                <tr>
                    <td>Position Size</td>
                    <td>{trading_signals.get('position_size', trade_params.get('position_size', 'N/A'))} lots</td>
                </tr>
                <tr>
                    <td>Risk/Reward Ratio</td>
                    <td>{trading_signals.get('risk_reward_ratio', 'N/A')}</td>
                </tr>
                <tr>
                    <td>Timing</td>
                    <td>{trading_signals.get('timing', 'Enter at market price')}</td>
                </tr>
            </table>
        </div>
        {f"<p><strong>Alternative Scenario:</strong> {trading_signals.get('alternative_scenario')}</p>" if trading_signals.get('alternative_scenario') else ""}
    </div>

    <div class="section">
        <h2>Market Analysis</h2>
        {market_analysis}
    </div>

    <div class="section">
        <h2>Technical Analysis</h2>
        {technical_analysis}
    </div>

    <div class="section">
        <h2>Risk Assessment</h2>
        {risk_assessment}
    </div>

    <div class="section">
        <h2>Key Takeaways</h2>
        {takeaways_html}
    </div>

    <div class="section">
        <h2>References & Citations</h2>
        {sources_html}
    </div>

    <div class="disclaimer">
        <h3>⚠️ Risk Disclaimer</h3>
        <p><strong>Trading foreign exchange, commodities, and cryptocurrencies on margin carries a high level of risk and may not be suitable for all investors.</strong> The high degree of leverage can work against you as well as for you. Before deciding to trade, you should carefully consider your investment objectives, level of experience, and risk appetite.</p>
        <p>The possibility exists that you could sustain a loss of some or all of your initial investment and therefore you should not invest money that you cannot afford to lose. You should be aware of all the risks associated with trading and seek advice from an independent financial advisor if you have any doubts.</p>
        <p><strong>This report is for informational purposes only and does not constitute financial advice.</strong> Past performance is not indicative of future results. All analysis is generated by AI systems and may contain errors or inaccuracies. Always conduct your own research and consult with qualified professionals before making any investment decisions.</p>
    </div>

    <div style="text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #e5e7eb; color: #9ca3af; font-size: 12px;">
        <p>Generated by LangGraph + Gemini 2.5 Flash Multi-Agent Trading Analysis System</p>
        <p>Report ID: {datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{pair.replace('/', '')}</p>
    </div>
</body>
</html>"""

        return html
