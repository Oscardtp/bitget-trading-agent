# PLAN DE EJECUCION: AI TRADING DASHBOARD

**Version:** 1.0  
**Fecha:** 27 Junio 2026  
**Objetivo:** Dashboard web para supervisar el agente de trading en tiempo real, centrado en el razonamiento del agente, no en graficos de velas.

---

## TABLA DE CONTENIDOS

1. [Objetivos y Restricciones](#1-objetivos-y-restricciones)
2. [Arquitectura General](#2-arquitectura-general)
3. [Tech Stack](#3-tech-stack)
4. [Estructura de Archivos](#4-estructura-de-archivos)
5. [Fase 1: Backend API (FastAPI)](#5-fase-1-backend-api-fastapi)
6. [Fase 2: Frontend Base (Next.js)](#6-fase-2-frontend-base-nextjs)
7. [Fase 3: Dashboard Screen (AI Brain)](#7-fase-3-dashboard-screen-ai-brain)
8. [Fase 4: Market + Trade Screens](#8-fase-4-market--trade-screens)
9. [Fase 5: History + Settings](#9-fase-5-history--settings)
10. [Fase 6: Agent Integration](#10-fase-6-agent-integration)
11. [Testing Strategy](#11-testing-strategy)
12. [Deployment](#12-deployment)
13. [Exit Criteria](#13-exit-criteria)

---

## 1. OBJETIVOS Y RESTRICCIONES

### Objetivo Principal
Dashboard web local que permite al operador supervisar el agente de trading en tiempo real, entendiendo:
- **Que esta pensando** el agente (hipotesis, evidencia, decisiones)
- **Que esta haciendo** (entradas, salidas, posiciones abiertas)
- **Como esta rindiendo** (metricas, historial, patrones)

### Filosofia del Dashboard
> "El dashboard es una herramienta para supervisar un agente autonomo, NO una plataforma de trading manual."

- El **protagonista** es el razonamiento del agente, no los graficos
- Los paneles responden **preguntas reales** del operador
- Sin **vanity panels** (paneles que se ven bien pero no aportan valor)
- Estetica **terminal Bloomberg** (fondo oscuro, tipografia monospace, acentos de color)

### Restricciones Tecnicas
| Restriccion | Valor |
|-------------|-------|
| Frontend | Next.js 15 + React 19 + TypeScript |
| Backend | FastAPI + Uvicorn |
| Database | SQLite (mismo archivo que el agente) |
| Real-time | WebSocket nativo (sin Socket.IO) |
| Theme | Dark terminal (Bloomberg-style) |
| Deploy | Localhost only (:3000 frontend, :8000 API) |
| Auth | Ninguna (MVP) |
| Mobile | No responsive (desktop only) |
| Pagination | No para MVP |

### Filosofia de Diseno (Skills Cargados)
- **frontend-design**: Dark terminal, monospace, glow effects, variables CSS
- **frontend-patterns**: Composicion, hooks custom, TanStack Query, memoizacion
- **api-design**: REST semantico, status codes correctos, Pydantic validation
- **dashboard-builder**: Empezar con preguntas, no con layout; sin vanity panels
- **coding-standards**: Nomenclatura descriptiva, KISS/DRY/YAGNI
- **python-patterns**: Type hints, context managers, async patterns

---

## 2. ARQUITECTURA GENERAL

### Flujo de Datos
```
┌─────────────────┐    HTTP POST    ┌─────────────────┐    WebSocket    ┌─────────────────┐
│  Agent (Python) │ ──────────────▶ │  FastAPI (:8000)│ ──────────────▶ │  Next.js (:3000)│
│  main_loop.py   │                 │  /api/events    │                 │  Dashboard UI   │
└────────┬────────┘                 └────────┬────────┘                 └─────────────────┘
         │                                   │                                   │
         ▼                                   ▼                                   ▼
┌─────────────────┐                 ┌─────────────────┐                 ┌─────────────────┐
│  SQLite (WAL)   │ ◀──Read Only── │  SQLite (WAL)   │ ◀──Read Only── │  SQLite (WAL)   │
│  trading_agent  │                 │  trading_agent  │                 │  trading_agent  │
│  .db            │                 │  .db            │                 │  .db            │
└─────────────────┘                 └─────────────────┘                 └─────────────────┘
```

### Componentes
| Componente | Puerto | Tecnologia | Responsabilidad |
|------------|--------|------------|-----------------|
| Agent | N/A | Python 3.14 | Trading autonomo, escribe en SQLite |
| API | :8000 | FastAPI | sirve datos, acepta eventos, broadcast WebSocket |
| Frontend | :3000 | Next.js 15 | UI del dashboard, consume API, recibe WebSocket |
| Database | N/A | SQLite WAL | Almacenamiento compartido (agent escribe, API lee) |

---

## 3. TECH STACK

### Backend (Python)
```
fastapi>=0.115.0        # Web framework
uvicorn[standard]>=0.34.0  # ASGI server
websockets>=14.0        # WebSocket support
pydantic>=2.0           # Data validation (ya instalado)
sqlalchemy>=2.0         # ORM (ya instalado)
```

### Frontend (Node.js)
```
next>=15.0              # React framework
react>=19.0             # UI library
typescript>=5.0         # Type safety
tailwindcss>=4.0        # CSS utility-first
@tanstack/react-query>=5.0  # Server state management
zustand>=5.0            # Client state management
lucide-react>=0.400     # Icons
recharts>=2.15          # Charts (lightweight)
```

### Herramientas de Desarrollo
```
@types/node             # Node.js types
@types/react            # React types
eslint                  # Linting
prettier                # Formatting
```

---

## 4. ESTRUCTURA DE ARCHIVOS

### Backend API
```
TradingAgent/api/
├── __init__.py
├── main.py              # FastAPI app, CORS, startup/shutdown
├── config.py            # API settings (host, port, CORS, db_path)
├── database.py          # Read-only SQLite connection
├── models.py            # Pydantic schemas (response models)
├── websocket.py         # WebSocket ConnectionManager
├── event_bridge.py      # HTTP POST → WebSocket broadcast
└── routers/
    ├── __init__.py
    ├── market.py        # /api/market/* endpoints
    ├── trades.py        # /api/trades/* endpoints
    ├── stats.py         # /api/stats endpoint
    └── events.py        # POST /api/events endpoint
```

### Frontend
```
TradingAgent/frontend/
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── next.config.ts
├── public/
│   └── fonts/           # JetBrains Mono, IBM Plex Mono
├── src/
│   ├── app/
│   │   ├── layout.tsx           # Root layout (dark theme, fonts)
│   │   ├── page.tsx             # Dashboard screen (AI Brain)
│   │   ├── market/
│   │   │   └── page.tsx         # Market context screen
│   │   ├── trade/
│   │   │   └── page.tsx         # Open position screen
│   │   ├── history/
│   │   │   └── page.tsx         # Trade history + timeline
│   │   └── settings/
│   │       └── page.tsx         # Agent configuration
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Sidebar.tsx      # Navigation sidebar
│   │   │   ├── Header.tsx       # Top bar (status, clock)
│   │   │   └── StatusBar.tsx    # Bottom bar (connection, agent status)
│   │   ├── ai-brain/
│   │   │   ├── AIBrainPanel.tsx      # Main panel: agent reasoning
│   │   │   ├── EvidenceScore.tsx     # Evidence for/against visualization
│   │   │   ├── HypothesisCard.tsx    # Current hypothesis display
│   │   │   ├── InvalidationTriggers.tsx  # What would invalidate hypothesis
│   │   │   └── DecisionTimeline.tsx  # Timeline of agent decisions
│   │   ├── market/
│   │   │   ├── ContextCard.tsx       # Market context summary
│   │   │   ├── RegimeIndicator.tsx   # Current regime display
│   │   │   └── FeatureGrid.tsx       # Market features grid
│   │   ├── trade/
│   │   │   ├── OpenPosition.tsx      # Current open position
│   │   │   ├── TradeMetrics.tsx      # Live P&L, R:R, duration
│   │   │   └── MonitoringLog.tsx     # Position monitoring events
│   │   ├── history/
│   │   │   ├── TradeList.tsx         # List of past trades
│   │   │   ├── TradeDetail.tsx       # Single trade detail view
│   │   │   └── TimelineView.tsx      # Event timeline for trade
│   │   ├── stats/
│   │   │   ├── PerformanceCard.tsx   # Win rate, profit factor, expectancy
│   │   │   ├── StrategyBreakdown.tsx # Per-strategy performance
│   │   │   └── RegimeBreakdown.tsx   # Per-regime performance
│   │   └── shared/
│   │       ├── Card.tsx              # Reusable card component
│   │       ├── Badge.tsx             # Status badges (WIN/LOSS/ACTIVE)
│   │       ├── GlowValue.tsx         # Glowing value display
│   │       └── LoadingSpinner.tsx    # Loading state
│   ├── hooks/
│   │   ├── useWebSocket.ts           # WebSocket connection hook
│   │   ├── useMarketContext.ts       # Fetch market context
│   │   ├── useTrades.ts              # Fetch trades
│   │   ├── useStats.ts               # Fetch statistics
│   │   └── useLiveEvents.ts          # Real-time event stream
│   ├── lib/
│   │   ├── api.ts                    # API client functions
│   │   ├── types.ts                  # TypeScript interfaces
│   │   └── utils.ts                  # Utility functions (formatting, etc.)
│   └── stores/
│       ├── agentStore.ts             # Agent state (current context, position)
│       └── settingsStore.ts          # Dashboard settings
```

---

## 5. FASE 1: BACKEND API (FastAPI)

**Duracion estimada:** 2-3 dias  
**Archivos a crear:** 11 archivos en `api/`  
**Dependencias:** SQLAlchemy, Pydantic (ya instaladas)

### 5.1 Crear Dependencias

**Archivo:** `requirements.txt` (agregar)
```
fastapi>=0.115.0
uvicorn[standard]>=0.34.0
websockets>=14.0
```

**Comando:**
```bash
cd TradingAgent
pip install fastapi uvicorn[standard] websockets
```

### 5.2 Crear Directorio

```bash
mkdir api
mkdir api/routers
```

### 5.3 api/config.py

```python
"""API configuration settings."""
from pydantic_settings import BaseSettings


class APISettings(BaseSettings):
    """Settings for the FastAPI dashboard API."""
    
    host: str = "127.0.0.1"
    port: int = 8000
    cors_origins: list[str] = ["http://localhost:3000"]
    db_path: str = "trading_agent.db"
    ws_heartbeat: int = 30  # seconds
    
    class Config:
        env_prefix = "TA_API_"
        env_file = ".env"


def get_api_settings() -> APISettings:
    """Get API settings singleton."""
    return APISettings()
```

### 5.4 api/database.py

```python
"""Read-only database connection for the API."""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator

from db.database import Base


_engine = None
_SessionLocal = None


def get_readonly_engine(db_path: str = "trading_agent.db"):
    """Create a read-only SQLite engine."""
    global _engine
    if _engine is None:
        _engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False},
            pool_pre_ping=True,
        )
        # Set WAL mode for concurrent reads
        @event.listens_for(_engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA query_only=ON")  # Read-only
            cursor.close()
    return _engine


def get_readonly_session(db_path: str = "trading_agent.db") -> Generator[Session, None, None]:
    """Get a read-only database session (FastAPI dependency)."""
    engine = get_readonly_engine(db_path)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 5.5 api/models.py

```python
"""Pydantic schemas for API responses."""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any


# === Market Context ===
class MarketContextResponse(BaseModel):
    timestamp: datetime
    trend: str
    regime: str
    atr: float
    volume_score: float
    volatility_score: float
    session_score: float
    liquidity_score: float
    
    class Config:
        from_attributes = True


class RegimeResponse(BaseModel):
    regime: str
    confidence: float
    start_time: datetime
    end_time: Optional[datetime]
    duration_minutes: Optional[int]
    adx: Optional[float]
    atr: Optional[float]
    rsi: Optional[float]
    recommended_strategies: Optional[list[str]]
    
    class Config:
        from_attributes = True


# === Trade ===
class TradeResponse(BaseModel):
    trade_id: str
    asset: str
    strategy: str
    side: str
    entry_price: float
    entry_timestamp: datetime
    exit_price: Optional[float]
    exit_timestamp: Optional[datetime]
    exit_reason: Optional[str]
    gross_pnl: Optional[float]
    net_pnl: Optional[float]
    return_pct: Optional[float]
    result: Optional[str]
    regime: Optional[str]
    regime_confidence: Optional[float]
    duration_minutes: Optional[int]
    
    class Config:
        from_attributes = True


class TradeDetailResponse(TradeResponse):
    stop_loss: float
    take_profit: float
    position_size: float
    capital_allocation: float
    strategy_score: float
    hypothesis_id: Optional[int]
    

# === Event ===
class EventResponse(BaseModel):
    id: int
    timestamp: datetime
    event_type: str
    trade_id: Optional[str]
    data: Optional[dict[str, Any]]
    
    class Config:
        from_attributes = True


class LiveEvent(BaseModel):
    """Real-time event pushed via WebSocket."""
    event_type: str
    timestamp: datetime
    trade_id: Optional[str]
    data: Optional[dict[str, Any]]


# === Hypothesis ===
class HypothesisResponse(BaseModel):
    id: int
    statement: str
    asset: str
    created_at: datetime
    probability: float
    evidence_for: list[dict[str, Any]]
    evidence_against: list[dict[str, Any]]
    time_limit_hours: int
    invalidation_triggers: list[dict[str, Any]]
    risk_budget: float
    verdict: Optional[str]
    verdict_timestamp: Optional[datetime]
    verdict_reason: Optional[str]
    strategy_used: Optional[str]
    
    class Config:
        from_attributes = True


# === Stats ===
class PerformanceStats(BaseModel):
    total_trades: int
    win_rate: float
    profit_factor: float
    expectancy: float
    sharpe_ratio: Optional[float]
    max_drawdown: Optional[float]
    avg_win: Optional[float]
    avg_loss: Optional[float]
    avg_duration_minutes: Optional[float]


class StrategyStats(BaseModel):
    strategy: str
    total_trades: int
    win_rate: float
    profit_factor: float
    expectancy: float


class RegimeStats(BaseModel):
    regime: str
    total_trades: int
    win_rate: float
    profit_factor: float
    expectancy: float


class StatsResponse(BaseModel):
    performance: PerformanceStats
    by_strategy: list[StrategyStats]
    by_regime: list[RegimeStats]


# === Health ===
class HealthResponse(BaseModel):
    status: str
    agent_running: bool
    db_connected: bool
    uptime_seconds: float
    last_event_timestamp: Optional[datetime]
```

### 5.6 api/websocket.py

```python
"""WebSocket ConnectionManager for real-time event broadcasting."""
from fastapi import WebSocket
from typing import List
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and broadcasts events."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Broadcast a message to all connected clients."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send to WebSocket: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            try:
                self.active_connections.remove(conn)
            except ValueError:
                pass
    
    @property
    def connection_count(self) -> int:
        return len(self.active_connections)


# Global singleton
manager = ConnectionManager()
```

### 5.7 api/event_bridge.py

```python
"""Event bridge: HTTP POST from agent → WebSocket broadcast."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Any

from db.database import get_db
from db.models import EventStore
from api.websocket import manager
from api.models import LiveEvent

router = APIRouter()


@router.post("/api/events")
async def receive_event(event: dict[str, Any], db: Session = Depends(get_db)):
    """
    Receive an event from the agent and broadcast via WebSocket.
    
    Expected payload:
    {
        "event_type": "ENTRY",
        "trade_id": "BTC_20260627_123456",
        "data": {...}
    }
    """
    # Store event in database
    db_event = EventStore(
        timestamp=datetime.fromisoformat(event.get("timestamp", datetime.now(timezone.utc).isoformat())),
        event_type=event["event_type"],
        trade_id=event.get("trade_id"),
        data=event.get("data"),
    )
    db.add(db_event)
    db.commit()
    
    # Broadcast to WebSocket clients
    live_event = LiveEvent(
        event_type=event["event_type"],
        timestamp=db_event.timestamp,
        trade_id=event.get("trade_id"),
        data=event.get("data"),
    )
    await manager.broadcast(live_event.model_dump(mode="json"))
    
    return {"status": "ok", "event_id": db_event.id}
```

### 5.8 api/routers/market.py

```python
"""Market context and regime endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from db.database import get_db
from db.models import ContextHistory, RegimeHistory
from api.models import MarketContextResponse, RegimeResponse

router = APIRouter(prefix="/api/market")


@router.get("/context", response_model=Optional[MarketContextResponse])
async def get_latest_context(db: Session = Depends(get_db)):
    """Get the latest market context."""
    context = (
        db.query(ContextHistory)
        .order_by(ContextHistory.timestamp.desc())
        .first()
    )
    if not context:
        raise HTTPException(status_code=404, detail="No context available")
    return context


@router.get("/regime", response_model=Optional[RegimeResponse])
async def get_current_regime(db: Session = Depends(get_db)):
    """Get the current market regime."""
    regime = (
        db.query(RegimeHistory)
        .order_by(RegimeHistory.start_time.desc())
        .first()
    )
    if not regime:
        raise HTTPException(status_code=404, detail="No regime available")
    return regime


@router.get("/features")
async def get_market_features(db: Session = Depends(get_db)):
    """Get current market features (ATR, RSI, volume, etc.)."""
    context = (
        db.query(ContextHistory)
        .order_by(ContextHistory.timestamp.desc())
        .first()
    )
    if not context:
        raise HTTPException(status_code=404, detail="No features available")
    
    return {
        "atr": context.raw_data.get("atr") if context.raw_data else None,
        "rsi": context.raw_data.get("rsi") if context.raw_data else None,
        "volume": context.raw_data.get("volume") if context.raw_data else None,
        "volatility": context.volatility_score,
        "trend": context.trend,
        "session": context.session_score,
        "liquidity": context.liquidity_score,
    }
```

### 5.9 api/routers/trades.py

```python
"""Trade endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from db.database import get_db
from db.models import Trade, EventStore, MonitoringLog
from api.models import TradeResponse, TradeDetailResponse, EventResponse

router = APIRouter(prefix="/api/trades")


@router.get("/", response_model=List[TradeResponse])
async def list_trades(
    limit: int = 50,
    offset: int = 0,
    result: str = None,
    db: Session = Depends(get_db)
):
    """List trades with optional filtering."""
    query = db.query(Trade)
    
    if result:
        query = query.filter(Trade.result == result)
    
    trades = (
        query
        .order_by(Trade.timestamp.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return trades


@router.get("/open", response_model=List[TradeResponse])
async def list_open_trades(db: Session = Depends(get_db)):
    """List currently open trades."""
    trades = (
        db.query(Trade)
        .filter(Trade.exit_timestamp.is_(None))
        .order_by(Trade.entry_timestamp.desc())
        .all()
    )
    return trades


@router.get("/{trade_id}", response_model=TradeDetailResponse)
async def get_trade(trade_id: str, db: Session = Depends(get_db)):
    """Get detailed trade information."""
    trade = db.query(Trade).filter(Trade.trade_id == trade_id).first()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    return trade


@router.get("/{trade_id}/timeline", response_model=List[EventResponse])
async def get_trade_timeline(trade_id: str, db: Session = Depends(get_db)):
    """Get event timeline for a specific trade."""
    events = (
        db.query(EventStore)
        .filter(EventStore.trade_id == trade_id)
        .order_by(EventStore.timestamp.asc())
        .all()
    )
    return events


@router.get("/{trade_id}/monitoring")
async def get_trade_monitoring(trade_id: str, db: Session = Depends(get_db)):
    """Get monitoring log for a specific trade."""
    logs = (
        db.query(MonitoringLog)
        .filter(MonitoringLog.trade_id == trade_id)
        .order_by(MonitoringLog.timestamp.asc())
        .all()
    )
    return logs
```

### 5.10 api/routers/stats.py

```python
"""Performance statistics endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from db.database import get_db
from db.models import Trade, StrategyPerformanceMatrix
from api.models import StatsResponse, PerformanceStats, StrategyStats, RegimeStats

router = APIRouter(prefix="/api/stats")


@router.get("/", response_model=StatsResponse)
async def get_stats(db: Session = Depends(get_db)):
    """Get comprehensive performance statistics."""
    
    # === Overall Performance ===
    completed_trades = db.query(Trade).filter(Trade.result.isnot(None)).all()
    total = len(completed_trades)
    
    if total == 0:
        return StatsResponse(
            performance=PerformanceStats(
                total_trades=0,
                win_rate=0.0,
                profit_factor=0.0,
                expectancy=0.0,
            ),
            by_strategy=[],
            by_regime=[],
        )
    
    wins = [t for t in completed_trades if t.result == "WIN"]
    losses = [t for t in completed_trades if t.result == "LOSS"]
    
    win_rate = len(wins) / total if total > 0 else 0.0
    
    gross_profit = sum(t.gross_pnl or 0 for t in wins)
    gross_loss = abs(sum(t.gross_pnl or 0 for t in losses))
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
    
    avg_win = gross_profit / len(wins) if wins else 0.0
    avg_loss = gross_loss / len(losses) if losses else 0.0
    expectancy = (win_rate * avg_win) - ((1 - win_rate) * avg_loss)
    
    avg_duration = (
        sum(t.duration_minutes or 0 for t in completed_trades) / total
        if total > 0 else 0.0
    )
    
    performance = PerformanceStats(
        total_trades=total,
        win_rate=round(win_rate, 4),
        profit_factor=round(profit_factor, 2),
        expectancy=round(expectancy, 2),
        avg_win=round(avg_win, 2),
        avg_loss=round(avg_loss, 2),
        avg_duration_minutes=round(avg_duration, 1),
    )
    
    # === By Strategy ===
    strategy_rows = (
        db.query(StrategyPerformanceMatrix)
        .all()
    )
    by_strategy = [
        StrategyStats(
            strategy=row.strategy,
            total_trades=row.total_trades,
            win_rate=round(row.win_rate, 4),
            profit_factor=round(row.profit_factor, 2),
            expectancy=round(row.expectancy, 2),
        )
        for row in strategy_rows
    ]
    
    # === By Regime ===
    regime_map: dict[str, list] = {}
    for t in completed_trades:
        regime = t.regime or "UNKNOWN"
        if regime not in regime_map:
            regime_map[regime] = []
        regime_map[regime].append(t)
    
    by_regime = []
    for regime, trades in regime_map.items():
        r_total = len(trades)
        r_wins = len([t for t in trades if t.result == "WIN"])
        r_win_rate = r_wins / r_total if r_total > 0 else 0.0
        r_gross_profit = sum(t.gross_pnl or 0 for t in trades if t.result == "WIN")
        r_gross_loss = abs(sum(t.gross_pnl or 0 for t in trades if t.result == "LOSS"))
        r_pf = r_gross_profit / r_gross_loss if r_gross_loss > 0 else float('inf')
        r_expectancy = (r_win_rate * (r_gross_profit / r_wins if r_wins else 0)) - ((1 - r_win_rate) * (r_gross_loss / (r_total - r_wins) if (r_total - r_wins) else 0))
        
        by_regime.append(RegimeStats(
            regime=regime,
            total_trades=r_total,
            win_rate=round(r_win_rate, 4),
            profit_factor=round(r_pf, 2),
            expectancy=round(r_expectancy, 2),
        ))
    
    return StatsResponse(
        performance=performance,
        by_strategy=by_strategy,
        by_regime=by_regime,
    )
```

### 5.11 api/main.py

```python
"""FastAPI application entry point."""
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import logging

from api.config import get_api_settings
from api.websocket import manager
from api.routers import market, trades, stats
from api.event_bridge import router as event_router

logging.basicConfig(level=logging.INFO)
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

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(market.router)
app.include_router(trades.router)
app.include_router(stats.router)
app.include_router(event_router)


# === Health Check ===
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "uptime_seconds": round(time.time() - start_time, 1),
        "websocket_connections": manager.connection_count,
    }


# === WebSocket ===
@app.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time event streaming."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, receive pings
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
```

### 5.12 api/routers/__init__.py

```python
"""API routers package."""
```

### 5.13 api/__init__.py

```python
"""Dashboard API package."""
```

---

## 6. FASE 2: FRONTEND BASE (Next.js)

**Duracion estimada:** 2-3 dias  
**Archivos a crear:** ~15 archivos base  
**Dependencias:** Node.js, npm

### 6.1 Inicializar Proyecto

```bash
cd TradingAgent
npx create-next-app@latest frontend --typescript --tailwind --app --no-eslint --src-dir --import-alias "@/*"
cd frontend
npm install @tanstack/react-query zustand lucide-react recharts
```

### 6.2 Configuracion

**frontend/tailwind.config.ts** - Dark terminal theme:
```typescript
import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        terminal: {
          bg: "#0a0a0f",
          card: "#12121a",
          border: "#1e1e2e",
          text: "#c0c0d0",
          muted: "#6b6b80",
          accent: "#00ff88",
          warning: "#ffaa00",
          danger: "#ff4444",
          info: "#4488ff",
        },
      },
      fontFamily: {
        mono: ["JetBrains Mono", "IBM Plex Mono", "monospace"],
      },
      boxShadow: {
        glow: "0 0 20px rgba(0, 255, 136, 0.15)",
        "glow-red": "0 0 20px rgba(255, 68, 68, 0.15)",
        "glow-blue": "0 0 20px rgba(68, 136, 255, 0.15)",
      },
    },
  },
  plugins: [],
};
export default config;
```

**frontend/src/app/globals.css** - Base styles:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --terminal-bg: #0a0a0f;
  --terminal-card: #12121a;
  --terminal-border: #1e1e2e;
  --terminal-text: #c0c0d0;
  --terminal-muted: #6b6b80;
  --terminal-accent: #00ff88;
  --terminal-warning: #ffaa00;
  --terminal-danger: #ff4444;
  --terminal-info: #4488ff;
}

body {
  background-color: var(--terminal-bg);
  color: var(--terminal-text);
  font-family: "JetBrains Mono", monospace;
}

/* Scrollbar styling */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
::-webkit-scrollbar-track {
  background: var(--terminal-bg);
}
::-webkit-scrollbar-thumb {
  background: var(--terminal-border);
  border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
  background: var(--terminal-muted);
}
```

### 6.3 Layout Components

**frontend/src/components/layout/Sidebar.tsx**:
```tsx
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Brain, BarChart3, History, Settings, Activity } from "lucide-react";

const navItems = [
  { href: "/", label: "AI Brain", icon: Brain },
  { href: "/market", label: "Market", icon: Activity },
  { href: "/trade", label: "Trade", icon: BarChart3 },
  { href: "/history", label: "History", icon: History },
  { href: "/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-terminal-card border-r border-terminal-border flex flex-col">
      <div className="p-4 border-b border-terminal-border">
        <h1 className="text-lg font-bold text-terminal-accent">
          TRADING AGENT
        </h1>
        <p className="text-xs text-terminal-muted mt-1">Dashboard v1.0</p>
      </div>
      
      <nav className="flex-1 p-4">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2 rounded mb-2 transition-colors ${
                isActive
                  ? "bg-terminal-accent/10 text-terminal-accent"
                  : "text-terminal-muted hover:text-terminal-text hover:bg-terminal-border/50"
              }`}
            >
              <Icon size={18} />
              <span className="text-sm">{item.label}</span>
            </Link>
          );
        })}
      </nav>
      
      <div className="p-4 border-t border-terminal-border">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-terminal-accent animate-pulse" />
          <span className="text-xs text-terminal-muted">Agent Online</span>
        </div>
      </div>
    </aside>
  );
}
```

**frontend/src/components/layout/Header.tsx**:
```tsx
"use client";

import { useLiveEvents } from "@/hooks/useLiveEvents";

export function Header() {
  const { isConnected } = useLiveEvents();
  const now = new Date();

  return (
    <header className="h-12 bg-terminal-card border-b border-terminal-border flex items-center justify-between px-6">
      <div className="flex items-center gap-4">
        <span className="text-sm text-terminal-muted">
          {now.toLocaleDateString("en-US", {
            weekday: "short",
            year: "numeric",
            month: "short",
            day: "numeric",
          })}
        </span>
        <span className="text-sm text-terminal-text font-mono">
          {now.toLocaleTimeString("en-US", { hour12: false })}
        </span>
      </div>
      
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <div
            className={`w-2 h-2 rounded-full ${
              isConnected ? "bg-terminal-accent" : "bg-terminal-danger"
            }`}
          />
          <span className="text-xs text-terminal-muted">
            {isConnected ? "LIVE" : "DISCONNECTED"}
          </span>
        </div>
        <span className="text-xs text-terminal-muted">BTC/USDT</span>
      </div>
    </header>
  );
}
```

### 6.4 Shared Components

**frontend/src/components/shared/Card.tsx**:
```tsx
import { ReactNode } from "react";

interface CardProps {
  title: string;
  children: ReactNode;
  className?: string;
  accent?: boolean;
}

export function Card({ title, children, className = "", accent = false }: CardProps) {
  return (
    <div
      className={`bg-terminal-card border rounded-lg p-4 ${
        accent ? "border-terminal-accent/30 shadow-glow" : "border-terminal-border"
      } ${className}`}
    >
      <h3 className="text-xs font-semibold text-terminal-muted uppercase tracking-wider mb-3">
        {title}
      </h3>
      {children}
    </div>
  );
}
```

**frontend/src/components/shared/GlowValue.tsx**:
```tsx
interface GlowValueProps {
  value: string | number;
  label: string;
  color?: "accent" | "warning" | "danger" | "info";
  size?: "sm" | "md" | "lg";
}

const colorMap = {
  accent: "text-terminal-accent",
  warning: "text-terminal-warning",
  danger: "text-terminal-danger",
  info: "text-terminal-info",
};

const sizeMap = {
  sm: "text-lg",
  md: "text-2xl",
  lg: "text-3xl",
};

export function GlowValue({ value, label, color = "accent", size = "md" }: GlowValueProps) {
  return (
    <div className="text-center">
      <div className={`${sizeMap[size]} font-bold ${colorMap[color]} font-mono`}>
        {value}
      </div>
      <div className="text-xs text-terminal-muted mt-1">{label}</div>
    </div>
  );
}
```

**frontend/src/components/shared/Badge.tsx**:
```tsx
interface BadgeProps {
  status: "WIN" | "LOSS" | "ACTIVE" | "PENDING" | "CLOSED";
}

const statusStyles = {
  WIN: "bg-terminal-accent/20 text-terminal-accent",
  LOSS: "bg-terminal-danger/20 text-terminal-danger",
  ACTIVE: "bg-terminal-info/20 text-terminal-info",
  PENDING: "bg-terminal-warning/20 text-terminal-warning",
  CLOSED: "bg-terminal-muted/20 text-terminal-muted",
};

export function Badge({ status }: BadgeProps) {
  return (
    <span
      className={`px-2 py-0.5 rounded text-xs font-semibold ${statusStyles[status]}`}
    >
      {status}
    </span>
  );
}
```

### 6.5 Hooks

**frontend/src/hooks/useLiveEvents.ts**:
```typescript
"use client";

import { useEffect, useState, useCallback } from "react";
import { LiveEvent } from "@/lib/types";

export function useLiveEvents() {
  const [events, setEvents] = useState<LiveEvent[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [ws, setWs] = useState<WebSocket | null>(null);

  const connect = useCallback(() => {
    const websocket = new WebSocket("ws://localhost:8000/ws/live");

    websocket.onopen = () => {
      setIsConnected(true);
      console.log("WebSocket connected");
    };

    websocket.onmessage = (event) => {
      const data: LiveEvent = JSON.parse(event.data);
      setEvents((prev) => [data, ...prev].slice(0, 100)); // Keep last 100
    };

    websocket.onclose = () => {
      setIsConnected(false);
      console.log("WebSocket disconnected, reconnecting in 3s...");
      setTimeout(connect, 3000);
    };

    websocket.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    setWs(websocket);
  }, []);

  useEffect(() => {
    connect();
    return () => {
      ws?.close();
    };
  }, [connect]);

  return { events, isConnected };
}
```

**frontend/src/lib/api.ts**:
```typescript
const API_BASE = "http://localhost:8000";

export async function fetchMarketContext() {
  const res = await fetch(`${API_BASE}/api/market/context`);
  if (!res.ok) throw new Error("Failed to fetch market context");
  return res.json();
}

export async function fetchCurrentRegime() {
  const res = await fetch(`${API_BASE}/api/market/regime`);
  if (!res.ok) throw new Error("Failed to fetch regime");
  return res.json();
}

export async function fetchTrades(limit = 50) {
  const res = await fetch(`${API_BASE}/api/trades/?limit=${limit}`);
  if (!res.ok) throw new Error("Failed to fetch trades");
  return res.json();
}

export async function fetchOpenTrades() {
  const res = await fetch(`${API_BASE}/api/trades/open`);
  if (!res.ok) throw new Error("Failed to fetch open trades");
  return res.json();
}

export async function fetchTradeDetail(tradeId: string) {
  const res = await fetch(`${API_BASE}/api/trades/${tradeId}`);
  if (!res.ok) throw new Error("Failed to fetch trade");
  return res.json();
}

export async function fetchTradeTimeline(tradeId: string) {
  const res = await fetch(`${API_BASE}/api/trades/${tradeId}/timeline`);
  if (!res.ok) throw new Error("Failed to fetch timeline");
  return res.json();
}

export async function fetchStats() {
  const res = await fetch(`${API_BASE}/api/stats/`);
  if (!res.ok) throw new Error("Failed to fetch stats");
  return res.json();
}

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/api/health`);
  if (!res.ok) throw new Error("Failed to fetch health");
  return res.json();
}
```

**frontend/src/lib/types.ts**:
```typescript
export interface MarketContext {
  timestamp: string;
  trend: string;
  regime: string;
  atr: number;
  volume_score: number;
  volatility_score: number;
  session_score: number;
  liquidity_score: number;
}

export interface Trade {
  trade_id: string;
  asset: string;
  strategy: string;
  side: string;
  entry_price: number;
  entry_timestamp: string;
  exit_price: number | null;
  exit_timestamp: string | null;
  exit_reason: string | null;
  gross_pnl: number | null;
  net_pnl: number | null;
  return_pct: number | null;
  result: "WIN" | "LOSS" | null;
  regime: string | null;
  regime_confidence: number | null;
  duration_minutes: number | null;
}

export interface Event {
  id: number;
  timestamp: string;
  event_type: string;
  trade_id: string | null;
  data: Record<string, any> | null;
}

export interface LiveEvent {
  event_type: string;
  timestamp: string;
  trade_id: string | null;
  data: Record<string, any> | null;
}

export interface PerformanceStats {
  total_trades: number;
  win_rate: number;
  profit_factor: number;
  expectancy: number;
  avg_win: number | null;
  avg_loss: number | null;
  avg_duration_minutes: number | null;
}

export interface StatsResponse {
  performance: PerformanceStats;
  by_strategy: StrategyStats[];
  by_regime: RegimeStats[];
}

export interface StrategyStats {
  strategy: string;
  total_trades: number;
  win_rate: number;
  profit_factor: number;
  expectancy: number;
}

export interface RegimeStats {
  regime: string;
  total_trades: number;
  win_rate: number;
  profit_factor: number;
  expectancy: number;
}
```

---

## 7. FASE 3: DASHBOARD SCREEN (AI Brain)

**Duracion estimada:** 2-3 dias  
**Archivos a crear:** 5 componentes en `components/ai-brain/`

### 7.1 AIBrainPanel.tsx

El panel principal que muestra el razonamiento del agente:

```tsx
"use client";

import { Card } from "@/components/shared/Card";
import { EvidenceScore } from "./EvidenceScore";
import { HypothesisCard } from "./HypothesisCard";
import { InvalidationTriggers } from "./InvalidationTriggers";
import { DecisionTimeline } from "./DecisionTimeline";
import { useLiveEvents } from "@/hooks/useLiveEvents";

export function AIBrainPanel() {
  const { events } = useLiveEvents();
  
  // Extract latest hypothesis from events
  const latestHypothesis = events.find(
    (e) => e.event_type === "HYPOTHESIS_CREATED"
  );
  
  // Extract latest context snapshot
  const latestContext = events.find(
    (e) => e.event_type === "CONTEXT_SNAPSHOT"
  );

  return (
    <div className="grid grid-cols-12 gap-4 h-full">
      {/* Left: Hypothesis + Evidence */}
      <div className="col-span-8 flex flex-col gap-4">
        <Card title="Current Hypothesis" accent>
          <HypothesisCard hypothesis={latestHypothesis?.data} />
        </Card>
        
        <Card title="Evidence Score">
          <EvidenceScore hypothesis={latestHypothesis?.data} />
        </Card>
        
        <Card title="Invalidation Triggers">
          <InvalidationTriggers hypothesis={latestHypothesis?.data} />
        </Card>
      </div>
      
      {/* Right: Timeline */}
      <div className="col-span-4">
        <Card title="Decision Timeline" className="h-full">
          <DecisionTimeline events={events.slice(0, 20)} />
        </Card>
      </div>
    </div>
  );
}
```

### 7.2 EvidenceScore.tsx

Visualizacion de evidencia a favor y en contra:

```tsx
interface EvidenceScoreProps {
  hypothesis?: {
    evidence_for: Array<{ source: string; strength: number }>;
    evidence_against: Array<{ source: string; strength: number }>;
    probability: number;
  };
}

export function EvidenceScore({ hypothesis }: EvidenceScoreProps) {
  if (!hypothesis) {
    return <div className="text-terminal-muted">No hypothesis active</div>;
  }

  const totalFor = hypothesis.evidence_for.reduce(
    (sum, e) => sum + e.strength, 0
  );
  const totalAgainst = hypothesis.evidence_against.reduce(
    (sum, e) => sum + e.strength, 0
  );
  const total = totalFor + totalAgainst;
  const forPercent = total > 0 ? (totalFor / total) * 100 : 50;

  return (
    <div className="space-y-4">
      {/* Probability bar */}
      <div className="flex items-center gap-4">
        <span className="text-xs text-terminal-muted w-20">PROBABILITY</span>
        <div className="flex-1 h-3 bg-terminal-border rounded-full overflow-hidden">
          <div
            className="h-full bg-terminal-accent transition-all duration-500"
            style={{ width: `${hypothesis.probability * 100}%` }}
          />
        </div>
        <span className="text-sm font-mono text-terminal-accent w-16 text-right">
          {(hypothesis.probability * 100).toFixed(1)}%
        </span>
      </div>

      {/* Evidence bars */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <div className="text-xs text-terminal-accent mb-2">
            FOR ({hypothesis.evidence_for.length})
          </div>
          {hypothesis.evidence_for.map((e, i) => (
            <div key={i} className="flex items-center gap-2 mb-1">
              <div className="flex-1 h-1.5 bg-terminal-border rounded-full">
                <div
                  className="h-full bg-terminal-accent"
                  style={{ width: `${e.strength * 100}%` }}
                />
              </div>
              <span className="text-xs text-terminal-muted">{e.source}</span>
            </div>
          ))}
        </div>
        
        <div>
          <div className="text-xs text-terminal-danger mb-2">
            AGAINST ({hypothesis.evidence_against.length})
          </div>
          {hypothesis.evidence_against.map((e, i) => (
            <div key={i} className="flex items-center gap-2 mb-1">
              <div className="flex-1 h-1.5 bg-terminal-border rounded-full">
                <div
                  className="h-full bg-terminal-danger"
                  style={{ width: `${e.strength * 100}%` }}
                />
              </div>
              <span className="text-xs text-terminal-muted">{e.source}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
```

### 7.3 HypothesisCard.tsx

```tsx
interface HypothesisCardProps {
  hypothesis?: {
    statement: string;
    strategy_used: string;
    risk_budget: number;
    time_limit_hours: number;
    created_at: string;
  };
}

export function HypothesisCard({ hypothesis }: HypothesisCardProps) {
  if (!hypothesis) {
    return (
      <div className="text-center py-8 text-terminal-muted">
        No active hypothesis
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="text-lg text-terminal-text leading-relaxed">
        "{hypothesis.statement}"
      </div>
      
      <div className="grid grid-cols-4 gap-4 mt-4">
        <div>
          <div className="text-xs text-terminal-muted">STRATEGY</div>
          <div className="text-sm font-mono text-terminal-info">
            {hypothesis.strategy_used}
          </div>
        </div>
        <div>
          <div className="text-xs text-terminal-muted">RISK BUDGET</div>
          <div className="text-sm font-mono text-terminal-warning">
            {(hypothesis.risk_budget * 100).toFixed(2)}%
          </div>
        </div>
        <div>
          <div className="text-xs text-terminal-muted">TIME LIMIT</div>
          <div className="text-sm font-mono text-terminal-text">
            {hypothesis.time_limit_hours}h
          </div>
        </div>
        <div>
          <div className="text-xs text-terminal-muted">CREATED</div>
          <div className="text-sm font-mono text-terminal-text">
            {new Date(hypothesis.created_at).toLocaleTimeString()}
          </div>
        </div>
      </div>
    </div>
  );
}
```

### 7.4 InvalidationTriggers.tsx

```tsx
interface InvalidationTriggersProps {
  hypothesis?: {
    invalidation_triggers: Array<{
      condition: string;
      description: string;
    }>;
  };
}

export function InvalidationTriggers({ hypothesis }: InvalidationTriggersProps) {
  if (!hypothesis) {
    return <div className="text-terminal-muted">No triggers defined</div>;
  }

  return (
    <div className="space-y-2">
      {hypothesis.invalidation_triggers.map((trigger, i) => (
        <div
          key={i}
          className="flex items-start gap-3 p-2 bg-terminal-bg rounded border border-terminal-border"
        >
          <div className="w-2 h-2 rounded-full bg-terminal-danger mt-1.5" />
          <div>
            <div className="text-sm text-terminal-text font-mono">
              {trigger.condition}
            </div>
            <div className="text-xs text-terminal-muted mt-1">
              {trigger.description}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
```

### 7.5 DecisionTimeline.tsx

```tsx
import { Event } from "@/lib/types";

interface DecisionTimelineProps {
  events: Event[];
}

const eventTypeColors: Record<string, string> = {
  CONTEXT_SNAPSHOT: "text-terminal-info",
  STRATEGY_SIGNAL: "text-terminal-accent",
  HYPOTHESIS_CREATED: "text-terminal-accent",
  ENTRY: "text-terminal-accent",
  MONITOR_CHECK: "text-terminal-muted",
  TRAILING_UPDATE: "text-terminal-warning",
  EXIT: "text-terminal-danger",
  TRADE_RESULT: "text-terminal-text",
  NO_TRADE: "text-terminal-muted",
};

export function DecisionTimeline({ events }: DecisionTimelineProps) {
  if (events.length === 0) {
    return (
      <div className="text-center py-8 text-terminal-muted">
        No events yet
      </div>
    );
  }

  return (
    <div className="space-y-2 overflow-y-auto max-h-96">
      {events.map((event) => (
        <div
          key={event.id}
          className="flex items-start gap-3 p-2 hover:bg-terminal-border/30 rounded"
        >
          <div className="text-xs text-terminal-muted w-16 shrink-0">
            {new Date(event.timestamp).toLocaleTimeString("en-US", {
              hour12: false,
              hour: "2-digit",
              minute: "2-digit",
            })}
          </div>
          <div
            className={`text-xs font-mono ${
              eventTypeColors[event.event_type] || "text-terminal-muted"
            }`}
          >
            {event.event_type}
          </div>
          {event.trade_id && (
            <div className="text-xs text-terminal-muted truncate">
              {event.trade_id}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
```

---

## 8. FASE 4: MARKET + TRADE SCREENS

**Duracion estimada:** 2-3 dias  
**Archivos a crear:** ~6 componentes

### 8.1 Market Screen

**frontend/src/app/market/page.tsx**:
```tsx
"use client";

import { Card } from "@/components/shared/Card";
import { ContextCard } from "@/components/market/ContextCard";
import { RegimeIndicator } from "@/components/market/RegimeIndicator";
import { FeatureGrid } from "@/components/market/FeatureGrid";

export default function MarketPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-xl font-bold text-terminal-text">Market Context</h1>
      
      <div className="grid grid-cols-2 gap-6">
        <Card title="Context">
          <ContextCard />
        </Card>
        
        <Card title="Regime">
          <RegimeIndicator />
        </Card>
      </div>
      
      <Card title="Features">
        <FeatureGrid />
      </Card>
    </div>
  );
}
```

### 8.2 Trade Screen (Open Position)

**frontend/src/app/trade/page.tsx**:
```tsx
"use client";

import { Card } from "@/components/shared/Card";
import { OpenPosition } from "@/components/trade/OpenPosition";
import { TradeMetrics } from "@/components/trade/TradeMetrics";
import { MonitoringLog } from "@/components/trade/MonitoringLog";

export default function TradePage() {
  return (
    <div className="space-y-6">
      <h1 className="text-xl font-bold text-terminal-text">Open Position</h1>
      
      <div className="grid grid-cols-2 gap-6">
        <Card title="Position" accent>
          <OpenPosition />
        </Card>
        
        <Card title="Metrics">
          <TradeMetrics />
        </Card>
      </div>
      
      <Card title="Monitoring Log">
        <MonitoringLog />
      </Card>
    </div>
  );
}
```

---

## 9. FASE 5: HISTORY + SETTINGS

**Duracion estimada:** 1-2 dias  
**Archivos a crear:** ~4 componentes

### 9.1 History Screen

**frontend/src/app/history/page.tsx**:
```tsx
"use client";

import { Card } from "@/components/shared/Card";
import { TradeList } from "@/components/history/TradeList";
import { PerformanceCard } from "@/components/stats/PerformanceCard";
import { StrategyBreakdown } from "@/components/stats/StrategyBreakdown";

export default function HistoryPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-xl font-bold text-terminal-text">Trade History</h1>
      
      <div className="grid grid-cols-3 gap-6">
        <Card title="Performance" accent className="col-span-1">
          <PerformanceCard />
        </Card>
        
        <Card title="By Strategy" className="col-span-2">
          <StrategyBreakdown />
        </Card>
      </div>
      
      <Card title="All Trades">
        <TradeList />
      </Card>
    </div>
  );
}
```

### 9.2 Settings Screen

**frontend/src/app/settings/page.tsx**:
```tsx
"use client";

import { Card } from "@/components/shared/Card";

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-xl font-bold text-terminal-text">Settings</h1>
      
      <Card title="Agent Configuration">
        <div className="text-terminal-muted">
          Agent configuration will be displayed here.
        </div>
      </Card>
      
      <Card title="Dashboard Preferences">
        <div className="text-terminal-muted">
          Dashboard preferences will be displayed here.
        </div>
      </Card>
    </div>
  );
}
```

---

## 10. FASE 6: AGENT INTEGRATION

**Duracion estimada:** 1-2 dias  
**Objetivo:** Modificar `logs/event_store.py` para hacer HTTP POST al API

### 10.1 Modificar EventStore

**Archivo:** `logs/event_store.py`

Agregar metodo para enviar eventos al API:

```python
import httpx
from typing import Optional

class EventStore:
    def __init__(self, session=None):
        # ... existing code ...
        self._api_url = "http://localhost:8000/api/events"
    
    def log(self, event_type: str, trade_id: Optional[str] = None, data: Optional[dict] = None):
        """Log an event to the database and optionally push to API."""
        # Existing database logic
        event = Event(
            timestamp=datetime.now(timezone.utc),
            event_type=event_type,
            trade_id=trade_id,
            data=data,
        )
        self.session.add(event)
        self.session.commit()
        
        # Push to API (non-blocking, silent failure)
        self._push_to_api(event)
        
        return event
    
    def _push_to_api(self, event: Event):
        """Push event to dashboard API (fire and forget)."""
        try:
            import httpx
            payload = {
                "event_type": event.event_type,
                "timestamp": event.timestamp.isoformat(),
                "trade_id": event.trade_id,
                "data": event.data,
            }
            # Use sync client for simplicity (agent is sync)
            with httpx.Client(timeout=2.0) as client:
                client.post(self._api_url, json=payload)
        except Exception:
            # Silent failure - dashboard polls DB on next refresh
            pass
```

### 10.2 Agregar httpx a requirements.txt

```
httpx>=0.27.0
```

---

## 11. TESTING STRATEGY

### Backend API Tests

```bash
# Start API server
cd TradingAgent
python -m uvicorn api.main:app --reload --port 8000

# Test endpoints
curl http://localhost:8000/api/health
curl http://localhost:8000/api/market/context
curl http://localhost:8000/api/trades/
curl http://localhost:8000/api/stats/
```

### Frontend Tests

```bash
# Start frontend
cd TradingAgent/frontend
npm run dev

# Open browser
# http://localhost:3000
```

### Integration Test

1. Start API: `python -m uvicorn api.main:app --port 8000`
2. Start Frontend: `cd frontend && npm run dev`
3. Start Agent: `python main.py --log-level INFO`
4. Verify real-time updates appear in dashboard

---

## 12. DEPLOYMENT

### Local Development

```bash
# Terminal 1: API
cd TradingAgent
python -m uvicorn api.main:app --reload --port 8000

# Terminal 2: Frontend
cd TradingAgent/frontend
npm run dev

# Terminal 3: Agent
cd TradingAgent
python main.py --log-level INFO
```

### Production (Local)

```bash
# Build frontend
cd TradingAgent/frontend
npm run build

# Start API with production settings
cd TradingAgent
TA_API_HOST=127.0.0.1 TA_API_PORT=8000 python -m uvicorn api.main:app --host 127.0.0.1 --port 8000

# Serve frontend build (or use nginx)
cd TradingAgent/frontend
npx serve -s . -l 3000
```

---

## 13. EXIT CRITERIA

### MVP Dashboard Complete When:

- [ ] **Backend API**
  - [ ] All endpoints respond correctly
  - [ ] SQLite read-only connection works
  - [ ] WebSocket broadcasts events
  - [ ] Event bridge receives agent events

- [ ] **Frontend**
  - [ ] Dark terminal theme renders correctly
  - [ ] Navigation works across all screens
  - [ ] Real-time updates via WebSocket
  - [ ] No console errors

- [ ] **Dashboard Screen (AI Brain)**
  - [ ] Current hypothesis displayed
  - [ ] Evidence score visualization works
  - [ ] Invalidation triggers listed
  - [ ] Decision timeline shows events

- [ ] **Market Screen**
  - [ ] Market context displayed
  - [ ] Regime indicator shows current regime
  - [ ] Feature grid shows all metrics

- [ ] **Trade Screen**
  - [ ] Open position displayed (or "No open position")
  - [ ] Live P&L updates
  - [ ] Monitoring log shows checks

- [ ] **History Screen**
  - [ ] Trade list displays correctly
  - [ ] Performance stats calculated
  - [ ] Strategy breakdown works

- [ ] **Integration**
  - [ ] Agent events appear in real-time
  - [ ] Dashboard updates without refresh
  - [ ] No data loss between agent → API → frontend

---

## APPENDIX: API ENDPOINTS REFERENCE

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/market/context` | Latest market context |
| GET | `/api/market/regime` | Current regime |
| GET | `/api/market/features` | Market features |
| GET | `/api/trades/` | List trades |
| GET | `/api/trades/open` | Open trades |
| GET | `/api/trades/{id}` | Trade details |
| GET | `/api/trades/{id}/timeline` | Trade event timeline |
| GET | `/api/trades/{id}/monitoring` | Trade monitoring log |
| GET | `/api/stats/` | Performance statistics |
| POST | `/api/events` | Agent pushes events |
| WS | `/ws/live` | Real-time event stream |

---

**FIN DEL PLAN DE EJECUCION**

**Version:** 1.0  
**Autor:** Opencode  
**Fecha:** 27 Junio 2026  
