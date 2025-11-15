"""FastAPI server with SSE streaming for Forex Agent System."""

import os
import json
import asyncio
import time
from typing import Optional
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from backend.streaming_adapter import StreamingForexSystem
from utils.logger import get_logger
from utils.social_formatter import (
    format_for_twitter,
    format_for_telegram,
    format_for_facebook,
    format_all_platforms,
    is_trading_signal
)

logger = get_logger(__name__)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Forex Agent System API",
    description="Real-time streaming API for multi-agent forex/commodity trading analysis",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "http://localhost:3003",  # Local development (alternate port)
        "http://localhost:5173",  # Vite dev server
        "https://forex-agent-frontend-production.up.railway.app",  # Railway production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global system instance (initialized on first request)
_system: Optional[StreamingForexSystem] = None


def get_system() -> StreamingForexSystem:
    """Get or initialize the streaming system."""
    global _system
    if _system is None:
        _system = StreamingForexSystem()
    return _system


# Request/Response models
class AnalysisRequest(BaseModel):
    """Request model for analysis."""
    query: str
    account_balance: Optional[float] = None
    max_risk_per_trade: Optional[float] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    api_configured: bool


class SocialFormatRequest(BaseModel):
    """Request model for social media formatting."""
    result: dict  # Analysis result from /analyze endpoint
    platform: Optional[str] = "all"  # 'twitter', 'telegram', 'facebook', or 'all'
    include_trade_params: Optional[bool] = True
    custom_options: Optional[dict] = None


class SocialFormatResponse(BaseModel):
    """Response model for social media formatting."""
    platform: str
    post: Optional[str] = None
    posts: Optional[dict] = None  # For 'all' platform
    char_count: Optional[int] = None
    is_signal: bool
    error: Optional[str] = None


# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check(request: Request):
    """
    Health check endpoint.

    Returns system status and configuration info.
    """
    client_ip = request.client.host
    logger.debug(f"🏥 [HEALTH] Health check from {client_ip}")

    try:
        system = get_system()
        info = system.get_info()

        logger.debug(f"🏥 [HEALTH] System healthy, API configured: {info['system']['api_configured']}")

        return HealthResponse(
            status="healthy",
            version="2.0.0",
            api_configured=info["system"]["api_configured"]
        )
    except Exception as e:
        logger.error(f"❌ [HEALTH] Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


# System info endpoint
@app.get("/info")
async def get_info():
    """
    Get detailed system information.

    Returns:
        - Account configuration
        - Workflow structure
        - API status
    """
    try:
        system = get_system()
        return system.get_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Non-streaming analysis endpoint (for compatibility)
@app.post("/analyze")
async def analyze(request: AnalysisRequest):
    """
    Analyze a trading query (non-streaming).

    This endpoint returns the complete analysis result after all agents finish.
    For real-time updates, use the /analyze/stream endpoint.

    Args:
        request: Analysis request with query and optional parameters

    Returns:
        Complete analysis result with decision and agent outputs
    """
    try:
        # Create system with custom parameters if provided
        if request.account_balance or request.max_risk_per_trade:
            system = StreamingForexSystem(
                account_balance=request.account_balance,
                max_risk_per_trade=request.max_risk_per_trade
            )
        else:
            system = get_system()

        # Run analysis (non-streaming)
        result = system.system.analyze(request.query, verbose=False)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Streaming analysis endpoint (SSE)
@app.post("/analyze/stream")
async def analyze_stream(analysis_request: AnalysisRequest, client_request: Request):
    """
    Analyze a trading query with real-time streaming updates (SSE).

    This endpoint streams events as the workflow progresses:
    1. Query parsing
    2. Agent analysis (News, Technical, Fundamental)
    3. Risk assessment
    4. Final synthesis decision

    Args:
        analysis_request: Analysis request with query and optional parameters
        client_request: FastAPI request object

    Returns:
        Server-Sent Events stream with real-time updates

    Event types:
        - start: Analysis started
        - query_parsed: Query parsed into structured context
        - agent_update: Individual agent completed (news, technical, fundamental)
        - risk_update: Risk assessment completed
        - decision: Final trading decision
        - complete: Analysis complete with full result
        - error: Error occurred
    """
    client_ip = client_request.client.host
    logger.info(f"🌐 [API] POST /analyze/stream from {client_ip}")
    logger.info(f"🌐 [API] Query: '{analysis_request.query}'")
    start_time = time.time()

    try:
        # Create system with custom parameters if provided
        if analysis_request.account_balance or analysis_request.max_risk_per_trade:
            logger.info(f"🌐 [API] Using custom parameters: balance={analysis_request.account_balance}, risk={analysis_request.max_risk_per_trade}")
            system = StreamingForexSystem(
                account_balance=analysis_request.account_balance,
                max_risk_per_trade=analysis_request.max_risk_per_trade
            )
        else:
            system = get_system()

        async def event_generator():
            """Generate SSE events from the analysis stream."""
            try:
                async for event in system.analyze_stream(analysis_request.query):
                    # Format as SSE event
                    event_type = event.get("type", "message")
                    event_data = event.get("data", {})

                    yield {
                        "event": event_type,
                        "data": json.dumps(event_data)
                    }

                    # Small delay to prevent overwhelming the client
                    await asyncio.sleep(0.01)

            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(f"❌ [API] Stream error after {elapsed:.2f}s: {type(e).__name__}: {str(e)}")

                # Send error event
                yield {
                    "event": "error",
                    "data": json.dumps({
                        "error": str(e),
                        "error_type": type(e).__name__
                    })
                }

        logger.info(f"🌐 [API] Starting SSE stream for query: '{analysis_request.query}'")
        return EventSourceResponse(event_generator())

    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"❌ [API] Failed to start stream after {elapsed:.2f}s: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# GET endpoint for simple queries (useful for testing)
@app.get("/analyze/stream")
async def analyze_stream_get(
    query: str = Query(..., description="Trading query (e.g., 'Analyze gold', 'EUR/USD')"),
    request: Request = None
):
    """
    Streaming analysis with GET request (for easy testing).

    Example:
        GET /analyze/stream?query=Analyze+gold+trading
    """
    analysis_request = AnalysisRequest(query=query)
    return await analyze_stream(analysis_request, request)


# Social media formatting endpoint
@app.post("/api/format-social", response_model=SocialFormatResponse)
async def format_social_post(request: SocialFormatRequest):
    """
    Format analysis result for social media platforms.

    Supports Twitter (280 chars), Telegram (markdown), and Facebook (long-form).
    Can generate all formats at once or individual platform posts.

    Args:
        request: Contains analysis result, platform choice, and formatting options

    Returns:
        Formatted post(s) ready for sharing
    """
    try:
        result = request.result
        platform = request.platform.lower() if request.platform else "all"
        include_params = request.include_trade_params
        custom_opts = request.custom_options or {}

        # Check if it's a trading signal
        signal = is_trading_signal(result)

        if platform == "all":
            # Generate all platforms
            posts = format_all_platforms(
                result,
                include_trade_params=include_params,
                custom_options=custom_opts
            )
            return SocialFormatResponse(
                platform="all",
                posts=posts,
                is_signal=signal
            )

        elif platform == "twitter":
            post = format_for_twitter(
                result,
                include_trade_params=include_params,
                custom_hashtags=custom_opts.get('twitter_hashtags')
            )
            return SocialFormatResponse(
                platform="twitter",
                post=post,
                char_count=len(post),
                is_signal=signal
            )

        elif platform == "telegram":
            post = format_for_telegram(
                result,
                include_trade_params=include_params,
                channel_name=custom_opts.get('telegram_channel')
            )
            return SocialFormatResponse(
                platform="telegram",
                post=post,
                char_count=len(post),
                is_signal=signal
            )

        elif platform == "facebook":
            post = format_for_facebook(
                result,
                include_trade_params=include_params,
                educational_context=custom_opts.get('facebook_educational', True)
            )
            return SocialFormatResponse(
                platform="facebook",
                post=post,
                char_count=len(post),
                is_signal=signal
            )

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid platform: {platform}. Must be 'twitter', 'telegram', 'facebook', or 'all'"
            )

    except Exception as e:
        logger.error(f"❌ [FORMAT-SOCIAL] Error formatting post: {str(e)}")
        return SocialFormatResponse(
            platform=request.platform or "unknown",
            error=str(e),
            is_signal=False
        )


# Root endpoint
@app.get("/")
async def root():
    """API root endpoint with documentation links."""
    return {
        "name": "Forex Agent System API",
        "version": "2.0.0",
        "description": "Real-time streaming API for multi-agent forex/commodity trading analysis",
        "endpoints": {
            "health": "/health",
            "info": "/info",
            "analyze": "/analyze (POST)",
            "stream": "/analyze/stream (POST or GET)",
            "format-social": "/api/format-social (POST)",
            "docs": "/docs"
        },
        "documentation": "/docs"
    }


if __name__ == "__main__":
    import uvicorn

    # Get configuration from environment
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    reload = os.getenv("API_RELOAD", "true").lower() == "true"

    print(f"🚀 Starting Forex Agent System API on {host}:{port}")
    print(f"📖 API Documentation: http://{host}:{port}/docs")
    print(f"🔄 Streaming Endpoint: http://{host}:{port}/analyze/stream")

    uvicorn.run(
        "backend.server:app",
        host=host,
        port=port,
        reload=reload
    )
