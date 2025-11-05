"""Technical Agent - Performs technical analysis."""

from typing import Dict, Any
from datetime import datetime
import random


class TechnicalAgent:
    """
    Performs technical analysis on currency pairs.

    Now integrated with real-time price APIs:
    - Metal Price API for commodities (XAU, XAG, etc.)
    - Forex Rate API for forex and crypto pairs

    Falls back to mock data if API fails.
    """

    def __init__(self, use_real_prices: bool = True):
        self.name = "TechnicalAgent"
        self.use_real_prices = use_real_prices

    def analyze(self, pair: str) -> Dict[str, Any]:
        """
        Perform technical analysis for the given currency pair.

        Args:
            pair: Currency pair (e.g., "EUR/USD", "XAU/USD", "BTC/USD")

        Returns:
            Dict with technical analysis results
        """
        try:
            # Get current price (real or mock)
            current_price, price_source = self._get_price(pair)

            # Calculate indicators (mock values)
            indicators = self._calculate_indicators(current_price)

            # Determine trend
            trend = self._determine_trend(indicators)

            # Calculate support/resistance
            support, resistance = self._calculate_levels(current_price)

            # Generate signals
            signals = self._generate_signals(indicators, trend)

            return {
                "success": True,
                "agent": self.name,
                "data": {
                    "pair": pair,
                    "current_price": current_price,
                    "price_source": price_source,  # "real" or "mock"
                    "indicators": indicators,
                    "trend": trend,
                    "support": support,
                    "resistance": resistance,
                    "signals": signals,
                    "stop_loss": self._calculate_stop_loss(current_price, support),
                    "take_profit": self._calculate_take_profit(current_price, resistance),
                    "analysis_timestamp": datetime.utcnow().isoformat(),
                    "summary": self._generate_summary(trend, signals),
                },
            }

        except Exception as e:
            return {
                "success": False,
                "agent": self.name,
                "error": str(e),
                "data": {},
            }

    def _get_price(self, pair: str) -> tuple:
        """
        Get current price for the pair.

        Returns:
            (price: float, source: str)
        """
        if self.use_real_prices:
            # Try to get real price
            from agents.price_service import get_price_service

            price_service = get_price_service()
            price_data = price_service.get_price(pair)

            if price_data:
                print(f"     💰 Real price: ${price_data['price']} from {price_data['source']}")
                return price_data["price"], "real"
            else:
                print(f"     ⚠️  Failed to get real price, using mock data")

        # Fallback to mock price
        mock_price = self._get_mock_price(pair)
        return mock_price, "mock"

    def _get_mock_price(self, pair: str) -> float:
        """Get mock current price based on pair."""
        # Realistic price ranges for common pairs
        price_ranges = {
            "EUR/USD": (1.05, 1.12),
            "GBP/USD": (1.20, 1.30),
            "USD/JPY": (140.0, 152.0),
            "AUD/USD": (0.62, 0.68),
        }

        range_vals = price_ranges.get(pair, (1.0, 1.5))
        return round(random.uniform(range_vals[0], range_vals[1]), 5)

    def _calculate_indicators(self, price: float) -> Dict[str, float]:
        """Calculate technical indicators (mock)."""
        return {
            "rsi": round(random.uniform(30, 70), 2),  # Relative Strength Index
            "macd": round(random.uniform(-0.01, 0.01), 4),  # MACD
            "moving_avg_50": round(price * random.uniform(0.98, 1.02), 5),
            "moving_avg_200": round(price * random.uniform(0.95, 1.05), 5),
            "bollinger_upper": round(price * 1.02, 5),
            "bollinger_lower": round(price * 0.98, 5),
        }

    def _determine_trend(self, indicators: Dict[str, float]) -> str:
        """Determine the current trend."""
        rsi = indicators["rsi"]
        macd = indicators["macd"]

        # Simple trend logic
        bullish_signals = 0
        bearish_signals = 0

        if rsi > 50:
            bullish_signals += 1
        elif rsi < 50:
            bearish_signals += 1

        if macd > 0:
            bullish_signals += 1
        elif macd < 0:
            bearish_signals += 1

        if bullish_signals > bearish_signals:
            return "uptrend"
        elif bearish_signals > bullish_signals:
            return "downtrend"
        else:
            return "sideways"

    def _calculate_levels(self, price: float) -> tuple:
        """Calculate support and resistance levels."""
        support = round(price * 0.98, 5)
        resistance = round(price * 1.02, 5)
        return support, resistance

    def _generate_signals(self, indicators: Dict[str, float], trend: str) -> Dict[str, str]:
        """Generate trading signals."""
        rsi = indicators["rsi"]

        buy_signal = "neutral"
        sell_signal = "neutral"

        # RSI-based signals
        if rsi < 30:
            buy_signal = "strong"
        elif rsi < 40:
            buy_signal = "moderate"

        if rsi > 70:
            sell_signal = "strong"
        elif rsi > 60:
            sell_signal = "moderate"

        # Trend confirmation
        if trend == "uptrend":
            if buy_signal in ["strong", "moderate"]:
                buy_signal = "strong"
        elif trend == "downtrend":
            if sell_signal in ["strong", "moderate"]:
                sell_signal = "strong"

        return {
            "buy": buy_signal,
            "sell": sell_signal,
            "overall": self._overall_signal(buy_signal, sell_signal),
        }

    def _overall_signal(self, buy: str, sell: str) -> str:
        """Determine overall signal."""
        signal_strength = {"strong": 3, "moderate": 2, "weak": 1, "neutral": 0}

        buy_strength = signal_strength.get(buy, 0)
        sell_strength = signal_strength.get(sell, 0)

        if buy_strength > sell_strength:
            return "BUY"
        elif sell_strength > buy_strength:
            return "SELL"
        else:
            return "HOLD"

    def _calculate_stop_loss(self, price: float, support: float) -> float:
        """Calculate stop loss level."""
        return round(support * 0.995, 5)

    def _calculate_take_profit(self, price: float, resistance: float) -> float:
        """Calculate take profit level."""
        return round(resistance * 1.005, 5)

    def _generate_summary(self, trend: str, signals: Dict[str, str]) -> str:
        """Generate technical analysis summary."""
        overall = signals["overall"]
        return f"Technical analysis shows {trend} with {overall} signal. " f"Buy signal: {signals['buy']}, Sell signal: {signals['sell']}."
