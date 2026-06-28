"""FastAPI application entry point."""
import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from api.config import get_api_settings
from api.websocket import manager
from api.routers import market, trades, stats, events, risk, health
from api.event_bridge import router as event_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_api_settings()
start_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown."""
    logger.info("Dashboard API starting...")
    logger.info(f"Listening on {settings.host}:{settings.port}")
    yield
    logger.info("Dashboard API shutting down...")


app = FastAPI(
    title="Trading Agent Dashboard API",
    version="1.0.0",
    description="API for supervising the AI trading agent in real-time",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(market.router)
app.include_router(trades.router)
app.include_router(stats.router)
app.include_router(events.router)
app.include_router(event_router)
app.include_router(risk.router)
app.include_router(health.router)


@app.get("/")
async def root():
    """Root endpoint - redirects to health check."""
    return {
        "name": "Trading Agent Dashboard API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/api/health",
    }


@app.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time event streaming."""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )
