<div align="center">

# Bitget Trading Agent

### Multi-timeframe algorithmic trading system with AI-powered regime detection

[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e.svg)](LICENSE)
[![Python 3.14](https://img.shields.io/badge/Python-3.14-3b82f6.svg)](https://python.org)
[![Next.js 15](https://img.shields.io/badge/Next.js-15-black)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com)
[![Bitget](https://img.shields.io/badge/Bitget-ccxt-ff6600.svg)](https://ccxt.com)
[![Status](https://img.shields.io/badge/Status-Paper%20Trading-yellow)]()

**The entry is irrelevant. Management is everything.**

A systematic trading agent that tests hypotheses across multiple timeframes,
adapts to market regimes, and manages risk dynamically — all with full lifecycle
logging and a real-time monitoring dashboard.

[Architecture](#architecture) &bull; [Features](#features) &bull; [Quick Start](#quick-start) &bull; [Dashboard](#dashboard) &bull; [Contributing](#contributing)

</div>

---

## Table of Contents

- [Architecture](#architecture)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
- [Directory Structure](#directory-structure)
- [How It Works](#how-it-works)
- [Configuration](#configuration)
- [Dashboard](#dashboard)
- [API Reference](#api-reference)
- [Strategy Phases](#strategy-phases)
- [Risk Management](#risk-management)
- [Database Schema](#database-schema)
- [Available Scripts](#available-scripts)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Architecture

```
                 HYPOTHESIS-DRIVEN EXECUTION PIPELINE

  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
  │   1H Context │────>│  15M Signal  │────>│   5M Entry   │────>│  Risk Engine │
  │              │     │              │     │              │     │              │
  │  Trend       │     │  Breakout    │     │  Precision   │     │  Dynamic     │
  │  Regime      │     │  Filter      │     │  Timing      │     │  Sizing      │
  └──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
        |                    |                    |                    |
        v                    v                    v                    v
  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
  │  8 Regime    │     │  R:R >= 2:1  │     │  Trailing    │     │  Kill        │
  │  Classes     │     │              │     │  Stops       │     │  Switch      │
  └──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

The system operates on a **multi-timeframe architecture** where each timeframe answers one specific question:

| Timeframe | Question Answered | Purpose |
|-----------|------------------|---------|
| **1 Hour** | What is the market doing? | Context generation, regime detection, trend analysis |
| **15 Minutes** | Should I trade? | Signal detection, breakout confirmation, volume validation |
| **5 Minutes** | When exactly do I enter? | Precision timing, pullback detection, orderbook depth |

---

## Features

### Multi-Timeframe Intelligence

- **1H Context** — Market trend, regime, session analysis, and indicator computation (ADX, RSI, Bollinger)
- **15M Signal** — Breakout detection with volume confirmation and R:R validation
- **5M Entry** — Precision timing with pullback detection and orderbook depth analysis
- Each timeframe operates independently with its own data cache and refresh cycle

### AI Regime Detection

- **8 market regimes** with confidence scoring and risk profiles:
  - `TRENDING_BULL`, `TRENDING_BEAR` — Directional trends
  - `SIDEWAYS_LOW_VOL`, `SIDEWAYS_HIGH_VOL` — Range-bound markets
  - `EXPANSION`, `CONTRACTION` — Volatility transitions
  - `OVERLEVERAGED`, `CLIMAX` — Extreme conditions
- Regime-adaptive strategy selection with historical pattern matching
- Real-time indicator computation from OHLCV data

### Hypothesis-Driven Execution

- Every trade is a **testable thesis** with structured logging
- 12 logging fields per operation: Contexto, Regimen, Estrategia, Hipotesis, Confianza, Riesgo, Entrada, Salida, Motivo, Resultado, Duracion, Evidencia
- Verdict tracking: `CONFIRMED` / `INVALIDATED`
- Full lifecycle timeline in Event Store

### Dynamic Risk Management

- **DrawdownManager** — 3F-R protection with 4 states (Normal, Reduced, Defensive, Halted)
- **Kill Switch** — Instant halt capability with file-based persistence
- **Trailing Stops** — 3-stage profit protection
- **Daily Limits** — Max 5 trades/day, max 1 position simultaneously
- Adaptive sizing: 1% base risk, drops to 0.25% after 3 consecutive losses

### Paper Trading

- Realistic simulation with real orderbook spread
- Slippage modeling (0.05%)
- Commission simulation (0.1%)
- Execution delay (100-500ms)
- 1000 USDT virtual capital

### Real-Time Dashboard

- AI reasoning visualization with live market context
- Trade timeline with event filtering and lazy loading
- Performance metrics and system health monitoring
- WebSocket-based real-time event streaming

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Exchange | [ccxt](https://github.com/ccxt/ccxt) | Bitget market data (public, no API keys) |
| Data | Pandas, NumPy | OHLCV processing, indicator computation |
| Database | SQLite (WAL mode) | Trade & event persistence |
| API | FastAPI, Uvicorn, WebSocket | Real-time data bridge |
| Frontend | Next.js 15, React 19, TypeScript | Monitoring dashboard |
| Styling | Tailwind CSS v4 | Dark terminal theme |
| Icons | Lucide React | UI iconography |
| Charts | Recharts | Performance visualization |
| Config | Pydantic Settings | Environment management |
| Testing | pytest, pytest-cov | Python test suite |

---

## Prerequisites

- **Python 3.14+** (tested on 3.14.4)
- **Node.js 18+** (for dashboard)
- **npm** (for frontend dependencies)
- **Bitget account** (optional — paper trading works without API keys)

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/Oscardtp/bitget-trading-agent.git
cd bitget-trading-agent
```

### 2. Install Python Dependencies

```bash
cd TradingAgent
pip install -r requirements.txt
```

This installs:

- `ccxt>=4.0` — Exchange connectivity
- `pandas>=2.0` — Data manipulation
- `numpy>=1.24` — Numerical computation
- `sqlalchemy>=2.0` — ORM and database
- `pydantic>=2.0` — Data validation
- `pydantic-settings>=2.0` — Configuration management
- `fastapi>=0.115.0` — API framework
- `uvicorn[standard]>=0.34.0` — ASGI server
- `websockets>=14.0` — Real-time communication
- `python-dotenv>=1.0` — Environment variable loading
- `pytest>=7.0` — Testing framework
- `pytest-cov>=4.0` — Test coverage

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your Bitget API credentials (optional for paper trading):

```env
TA_BITGET__API_KEY=your_api_key_here
TA_BITGET__SECRET=your_secret_here
TA_BITGET__PASSPHRASE=your_passphrase_here
TA_BITGET__SANDBOX=true
TA_ASSET=BTCUSDT
TA_LOG_LEVEL=INFO
```

### 4. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 5. Run the System

**Option A: Unified (Recommended)**

```bash
cd TradingAgent
python run.py --log-level INFO
```

This starts both the API server (port 8000) and trading bot in a single process.

**Option B: Separate Terminals**

```bash
# Terminal 1: Backend + Trading Bot
cd TradingAgent
python run.py

# Terminal 2: Dashboard
cd TradingAgent/frontend
npm run dev
```

### 6. Access the Dashboard

- **Dashboard**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

---

## Directory Structure

```
Trading Agent/
├── TradingAgent/                   # Main application
│   ├── main_loop.py               # Core trading loop (1007 lines)
│   ├── run.py                     # Unified entry point (API + Bot)
│   ├── main.py                    # Alternative entry point
│   ├── requirements.txt           # Python dependencies
│   ├── .env.example               # Environment template
│   │
│   ├── api/                       # FastAPI backend
│   │   ├── main.py               # FastAPI app with CORS, WebSocket
│   │   ├── config.py             # API-specific settings
│   │   ├── models.py             # Pydantic response schemas
│   │   ├── websocket.py          # WebSocket connection manager
│   │   ├── event_bridge.py       # HTTP → WebSocket bridge
│   │   └── routers/              # API endpoints
│   │       ├── market.py         # Market context endpoints
│   │       ├── trades.py         # Trade data endpoints
│   │       ├── stats.py          # Performance statistics
│   │       ├── events.py         # Historical event loading
│   │       ├── risk.py           # Risk status + Kill Switch
│   │       └── health.py         # System health checks
│   │
│   ├── config/                    # Configuration
│   │   └── settings.py           # Pydantic Settings (risk, strategy, timing)
│   │
│   ├── context/                   # Market context generation
│   │   ├── multi_tf_context.py   # Multi-timeframe context dataclass
│   │   ├── indicators.py         # ADX, RSI, Bollinger, ATR
│   │   ├── trend_analyzer.py     # Trend detection
│   │   ├── volume_analyzer.py    # Volume analysis
│   │   ├── volatility_analyzer.py # Volatility measurement
│   │   ├── liquidity_analyzer.py # Liquidity scoring
│   │   └── session_analyzer.py   # Trading session detection
│   │
│   ├── data/                      # Exchange connectivity
│   │   ├── exchange_client.py    # ccxt wrapper for Bitget
│   │   └── market_data.py        # Multi-TF data with TTL cache
│   │
│   ├── db/                        # Database layer
│   │   ├── database.py           # SQLite engine + session factory
│   │   └── models.py             # 9 SQLAlchemy ORM models
│   │
│   ├── execution/                 # Order execution (future)
│   │   ├── order_executor.py     # Dry-run only (paper trading)
│   │   └── protocol_manager.py   # Position lifecycle management
│   │
│   ├── filters/                   # Trade filters
│   │   └── no_trade_filter.py    # 5-condition filter (volume, spread, etc.)
│   │
│   ├── frontend/                  # Next.js dashboard
│   │   ├── package.json          # Node.js dependencies
│   │   ├── next.config.ts        # Next.js configuration
│   │   ├── postcss.config.mjs    # PostCSS config (Tailwind v4)
│   │   └── src/
│   │       ├── app/              # App Router pages
│   │       │   └── (dashboard)/  # Dashboard layout
│   │       ├── components/       # React components
│   │       │   ├── ai-brain/     # AI reasoning panel
│   │       │   ├── history/      # Trade timeline drawer
│   │       │   ├── layout/       # Sidebar, Header
│   │       │   ├── market/       # Radar chart
│   │       │   ├── shared/       # Card, Badge, GlowValue
│   │       │   └── system/       # System status
│   │       ├── hooks/            # React hooks
│   │       │   ├── useHealth.ts  # Health polling (10s)
│   │       │   └── useLiveEvents.ts # WebSocket events
│   │       └── lib/              # Utilities
│   │           ├── api.ts        # API client functions
│   │           ├── types.ts      # TypeScript interfaces
│   │           ├── utils.ts      # Formatting helpers
│   │           └── eventLabels.ts # Spanish event labels
│   │
│   ├── fundamental/               # Fundamental analysis (future)
│   │
│   ├── hypothesis/                # Hypothesis management
│   │   └── hypothesis_builder.py # Structured hypothesis creation
│   │
│   ├── learning/                  # Learning systems
│   │   ├── feedback_loop.py      # Performance feedback
│   │   └── pattern_discovery.py  # Pattern recognition
│   │
│   ├── logs/                      # Logging infrastructure
│   │   ├── event_store.py        # Lifecycle event tracking
│   │   └── log_manager.py        # SQL-based trade logging
│   │
│   ├── monitor/                   # Position monitoring
│   │   └── thesis_monitor.py     # Regime/volume/confidence exits
│   │
│   ├── patterns/                  # Pattern discovery (future)
│   │
│   ├── regime/                    # Market regime detection
│   │   ├── regime_detector.py    # Real indicator-based detection
│   │   ├── regime_rules.py       # 8 regime definitions
│   │   └── historical_similarity.py # Pattern matching
│   │
│   ├── risk/                      # Risk management
│   │   ├── drawdown.py           # 3F-R drawdown protection
│   │   ├── kill_switch.py        # Emergency halt
│   │   ├── position_sizer.py     # Dynamic position sizing
│   │   ├── sl_tp_calculator.py   # ATR-based SL/TP
│   │   ├── trailing.py           # 3-stage trailing stops
│   │   ├── risk_engine.py        # Full risk engine (not yet integrated)
│   │   ├── capital_allocator.py  # Capital allocation
│   │   ├── regime_risk.py        # Regime-based risk
│   │   └── strategy_risk.py      # Strategy-based risk
│   │
│   ├── strategies/                # Strategy implementations
│   │   ├── orchestrator.py       # Strategy selection engine
│   │   ├── registry.py           # Auto-registration system
│   │   ├── scoring.py            # Strategy scoring
│   │   ├── learning_matrix.py    # Regime x Strategy performance
│   │   ├── strategy_base.py      # Base strategy interface
│   │   ├── mvp_config.py         # MVP phase configuration
│   │   ├── breakout/             # Breakout strategies
│   │   │   └── breakout_15m.py   # 15M breakout detection
│   │   ├── pullback/             # Pullback strategies
│   │   │   └── pullback_5m.py    # 5M pullback entry
│   │   ├── continuation/         # Continuation patterns
│   │   ├── contrarian/           # Contrarian strategies
│   │   ├── momentum/             # Momentum strategies
│   │   ├── reversion/            # Mean reversion
│   │   ├── sentiment/            # Sentiment analysis
│   │   ├── positioning/          # Positioning strategies
│   │   ├── volatility/           # Volatility strategies
│   │   └── filters/              # Strategy-specific filters
│   │
│   ├── validation/                # Trade validation
│   │   ├── metrics.py            # Win rate, expectancy, PF
│   │   ├── hypothesis_validator.py # Hypothesis validation
│   │   ├── evidence_collector.py # Evidence gathering
│   │   ├── market_conditions.py  # Market condition checks
│   │   └── pre_trade_checklist.py # Pre-trade validation
│   │
│   ├── validacion_mvp.py         # Automated validation script
│   ├── VALIDACION_MVP.md         # Validation plan
│   ├── MANUAL_USO.txt            # Usage manual
│   └── PLAN_DE_EJECUCION_DASHBOARD.md # Dashboard execution plan
│
├── Trading AI Agent/              # Architecture documentation
│   ├── 00_SYSTEM_OVERVIEW.md
│   ├── 01_MARKET_CONTEXT.md.md
│   ├── 02_STRATEGY_SELECTOR.md
│   ├── 03_RISK_ENGINE.md
│   ├── 04_VALIDATION_ENGINE.md
│   ├── 05_EXECUTION_PROTOCOL.md
│   ├── 06_LOGGING_SCHEMA.md
│   ├── 07_LEARNING_FEEDBACK_LOOP.md
│   ├── 08_PATTERN_DISCOVERY_ENGINE.md
│   ├── 09_MARKET_REGIME_ENGINE.md
│   └── 10_ALPHA_RESEARCH_ENGINE.md
│
├── Gestion_Riesgo/                 # Risk management documentation
│   ├── 01-atr-orderbook.md
│   ├── 02-3f-r.md
│   ├── checklist-operativa.md
│   └── README.md
│
├── PLAN_DE_EJECUCION.md           # Original execution plan
├── PLAN_MVP.md                    # MVP plan
├── README.md                      # This file
└── .gitignore                     # Git ignore rules
```

---

## How It Works

### The Multi-Timeframe Pipeline

The agent follows a strict pipeline where each stage filters and refines the previous:

```
1H Context (every 5 min)
    │
    ├── Fetch 1H OHLCV data (100 candles)
    ├── Compute indicators: ADX, RSI, Bollinger Width
    ├── Detect market regime (8 classes)
    ├── Generate context: trend, volatility, volume, session
    └── Store in ContextHistory table
         │
         ▼
15M Signal (every 1 min)
    │
    ├── Fetch 15M OHLCV data (100 candles)
    ├── Apply NoTradeFilter (5 conditions)
    ├── Detect breakout patterns
    ├── Validate R:R >= 2:1
    └── Generate hypothesis if signal found
         │
         ▼
5M Entry (on signal)
    │
    ├── Fetch 5M OHLCV data (100 candles)
    ├── Detect pullback entry point
    ├── Calculate position size (dynamic risk)
    ├── Set SL/TP (ATR-based)
    └── Execute paper trade
         │
         ▼
Monitor (every 30 sec)
    │
    ├── Check thesis validity
    ├── Update trailing stops
    ├── Detect regime changes
    └── Exit if thesis invalidated
```

### Market Regime Detection

The regime detector uses real indicators computed from OHLCV data:

| Regime | Conditions | Risk Profile | Recommended Strategies |
|--------|-----------|--------------|----------------------|
| TRENDING_BULL | ADX > 25, RSI > 50, Bullish | Moderate | Relative Strength, Breakout |
| TRENDING_BEAR | ADX > 25, RSI < 50, Bearish | Conservative | Breakout (short) |
| SIDEWAYS_LOW_VOL | ADX < 20, Low ATR | Defensive | Scalping, Mean Reversion |
| SIDEWAYS_HIGH_VOL | ADX < 20, High ATR | Conservative | Wait |
| EXPANSION | ATR rising, Volume rising | Moderate | Breakout, Momentum |
| CONTRACTION | ATR falling, Volume falling | Defensive | Wait |
| OVERLEVERAGED | Extreme funding rate | Defensive | Wait |
| CLIMAX | Extreme volume + reversal | Defensive | Contrarian |

### Strategy Phases

Rollout is **phased** — each strategy must validate before the next activates:

| Phase | Strategies | Capital Allocation | Status |
|-------|-----------|-------------------|--------|
| 1 | Breakout (acceptance) | 100% | Active |
| 2 | + Pullback | 70% / 30% | Planned |
| 3 | + Mean Reversion | 50% / 25% / 25% | Planned |
| 4 | + Scalping | 40% / 20% / 20% / 20% | Planned |

---

## Configuration

### Environment Variables

All variables use the `TA_` prefix with nested delimiters (`__`):

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `TA_BITGET__API_KEY` | Bitget API key | (empty) | `bg_xxxx` |
| `TA_BITGET__SECRET` | Bitget API secret | (empty) | `xxxx` |
| `TA_BITGET__PASSPHRASE` | Bitget API passphrase | (empty) | `xxxx` |
| `TA_BITGET__SANDBOX` | Use sandbox mode | `true` | `true` |
| `TA_ASSET` | Trading asset | `BTCUSDT` | `BTCUSDT` |
| `TA_LOG_LEVEL` | Logging level | `INFO` | `DEBUG` |

### Risk Settings

| Setting | Description | Default |
|---------|-------------|---------|
| `risk.base` | Base risk per trade | 1% |
| `risk.min` | Minimum risk per trade | 0.5% |
| `risk.max` | Maximum risk per trade | 5% |
| `risk.rr_min` | Minimum R:R ratio | 2.0 |
| `risk.max_positions` | Max simultaneous positions | 3 |
| `risk.max_trades_day` | Max trades per day | 5 |
| `risk.max_drawdown_daily` | Max daily drawdown | 5% |
| `risk.max_consecutive_losses` | Losses before reduction | 3 |
| `risk.max_slippage` | Max allowed slippage | 0.5% |

### Strategy Settings

| Setting | Description | Default |
|---------|-------------|---------|
| `strategy.threshold` | Min strategy score to activate | 0.65 |
| `strategy.confidence_threshold` | Min confidence for trade | 0.65 |
| `strategy.duration_limits.scalping` | Max scalping duration | 6 hours |
| `strategy.duration_limits.swing` | Max swing duration | 360 hours |
| `strategy.duration_limits.breakout` | Max breakout duration | 72 hours |
| `strategy.duration_limits.mean_reversion` | Max mean reversion duration | 12 hours |

---

## Dashboard

Five screens designed for **systematic traders** who think in probabilities:

| Screen | Purpose | Key Components |
|--------|---------|---------------|
| **Dashboard** | AI brain — live context, regime, performance, trades | AIBrainPanel, GlowValue, Event Timeline |
| **Market** | Metrics grid — volatility, volume, liquidity, funding, OI | Diagnóstico fusion, Radar chart |
| **Trades** | Open positions, entry/exit, PnL tracking | OpenPosition, MonitoringLog |
| **History** | Trade timeline, performance statistics, event logs | TradeTimelineDrawer, PerformanceStats |
| **Settings** | System health, configuration, kill switch | SystemStatus, Health polling |

### Design Philosophy

> Agent reasoning is the protagonist. Charts are secondary context.

### Key Features

- **Dark terminal theme** (Bloomberg-style) with monospace fonts
- **Real-time updates** via WebSocket (10s health polling, live events)
- **Spanish localization** for all UI labels and event types
- **Diagnóstico fusion** — Combines trend + volume into meaningful labels
- **Trade Timeline Drawer** — 480px slide-over with lazy-loaded event history
- **SVG Radar Chart** — 5-axis visualization of market metrics

---

## API Reference

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | API root info |
| `GET` | `/api/health` | System health (8 components, 30s cache) |
| `GET` | `/api/market/context` | Market context with indicators |
| `GET` | `/api/market/regime` | Current regime detection |
| `GET` | `/api/trades` | Recent trades |
| `GET` | `/api/trades/{trade_id}/timeline` | Trade lifecycle events |
| `GET` | `/api/stats` | Performance statistics |
| `GET` | `/api/events` | Historical events |
| `GET` | `/api/risk` | Drawdown status |
| `POST` | `/api/risk/kill-switch` | Activate kill switch |
| `DELETE` | `/api/risk/kill-switch` | Deactivate kill switch |
| `WS` | `/ws/live` | Real-time event stream |

### WebSocket Events

Connect to `ws://localhost:8000/ws/live` for real-time streaming:

```json
{
  "type": "HYPOTHESIS_CREATED",
  "trade_id": "T-20260628-001",
  "data": {
    "statement": "BTC breaking out above $67,500 resistance",
    "probability": 0.72
  },
  "timestamp": "2026-06-28T14:30:00Z"
}
```

---

## Risk Rules

```
POSITION SIZING
├── Base risk:        0.5% - 2% per trade
├── After 3 losses:   0.25%
├── R:R minimum:      2:1
├── Daily limit:      5 trades
└── Max positions:    1

PROTECTION LAYERS
├── Structure-based SL (ATR)
├── 3-stage trailing stop
├── ThesisMonitor (regime/volume/confidence)
├── DrawdownManager (3F-R)
│   ├── NORMAL:     Full risk (1%)
│   ├── REDUCED:    0.75% after 3 consecutive losses
│   ├── DEFENSIVE:  0.25% after 5+ consecutive losses
│   └── HALTED:     No trading (max drawdown exceeded)
└── Kill Switch (manual or auto)

PAPER TRADING REALISM
├── Real orderbook spread
├── Slippage:         0.05%
├── Commission:       0.1%
├── Execution delay:  100-500ms
└── Virtual capital:  1000 USDT
```

---

## Database Schema

9 SQLAlchemy ORM models with SQLite (WAL mode):

```
trades                    # Complete trade records
├── trade_id (unique)     # T-YYYYMMDD-NNN
├── entry/exit prices     # Entry and exit data
├── strategy              # Strategy used
├── position_size         # Calculated size
├── stop_loss/take_profit # Risk levels
├── gross_pnl/net_pnl     # Profit/loss
├── regime                # Market regime at entry
└── hypothesis_id (FK)    # Linked hypothesis

context_history           # Market context snapshots
├── trade_id (FK)         # One-to-one with trades
├── trend                 # bullish/bearish/neutral
├── volatility_score      # 0-1 scale
├── liquidity_score       # 0-1 scale
├── sentiment_score       # 0-1 scale
└── raw_data              # Full context JSON

regime_history            # Historical regime detections
├── regime                # RegimeType enum
├── confidence            # 0-1 scale
├── adx/atr/rsi           # Indicator values
├── recommended_strategies # JSON array
└── duration_minutes      # How long regime lasted

hypotheses                # Trading hypotheses
├── statement             # Human-readable thesis
├── probability           # 0-1 confidence
├── evidence_for/against  # JSON evidence
├── invalidation_triggers # JSON conditions
├── verdict               # CONFIRMED/INVALIDATED
└── risk_budget           # Max risk allocation

monitoring_log            # Continuous monitoring events
├── trade_id (FK)         # Linked to trade
├── verdict               # HOLD/ADJUST_SL/EXIT
├── regime_changed        # Boolean
└── action                # Action taken

patterns                  # Discovered patterns
├── pattern_type          # Category
├── win_rate              # Historical performance
├── profit_factor         # Risk-adjusted return
├── expectancy            # Expected value
└── sample_size           # Number of observations

strategy_performance_matrix  # Regime x Strategy performance
├── regime                # Market regime
├── strategy              # Strategy name
├── win_rate              # Performance metric
├── profit_factor         # Risk-adjusted return
├── expectancy            # Expected value
└── total_trades          # Trade count

system_versions           # Version tracking
├── version               # Semantic version
├── config_snapshot       # JSON config at version
└── is_active             # Current version flag

event_store               # Lifecycle event tracking
├── event_type            # 14 event types
├── trade_id              # Optional trade link
└── data                  # Event-specific JSON
```

---

## Available Scripts

| Command | Description |
|---------|-------------|
| `python run.py` | Start unified (API + Bot) |
| `python run.py --log-level DEBUG` | Start with debug logging |
| `python run.py --symbol ETH/USDT` | Trade different asset |
| `python run.py --live` | Enable live trading (not paper) |
| `python validacion_mvp.py` | Run MVP validation tests |
| `cd frontend && npm run dev` | Start dashboard dev server |
| `cd frontend && npm run build` | Build dashboard for production |
| `cd frontend && npm run lint` | Lint frontend code |

### CLI Arguments for `run.py`

| Argument | Default | Description |
|----------|---------|-------------|
| `--symbol` | `BTC/USDT` | Trading pair |
| `--scanner-interval` | `60` | Signal scan interval (seconds) |
| `--monitor-interval` | `30` | Position monitor interval (seconds) |
| `--context-interval` | `300` | Context refresh interval (seconds) |
| `--dry-run` | `True` | Paper trading mode |
| `--live` | `False` | Enable live trading |
| `--log-level` | `INFO` | Logging verbosity |
| `--api-port` | `8000` | API server port |

---

## Troubleshooting

### Port Already in Use

**Error:** `Address already in use ::8000`

**Solution:**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <pid> /F

# Or let run.py handle it (auto-kills conflicting processes)
python run.py
```

### Bitget API Connection Issues

**Error:** `Request timeout` or `Connection refused`

**Solution:**
1. Verify internet connection
2. Check if Bitget is accessible: `curl https://api.bitget.com/api/v2/spot/market/tickers`
3. Ensure sandbox mode matches your API keys
4. Check rate limiting (200ms between requests)

### Database Locked

**Error:** `database is locked`

**Solution:**
1. Ensure only one instance is running
2. Check SQLite WAL mode is enabled
3. Restart the application

### Frontend Build Errors

**Error:** `Type error` or `Module not found`

**Solution:**
```bash
cd TradingAgent/frontend
Remove-Item -Recurse -Force .next
npm install
npm run build
```

### WebSocket Connection Fails

**Error:** Dashboard shows "Waiting for data..."

**Solution:**
1. Verify API server is running: `curl http://localhost:8000/api/health`
2. Check CORS settings in `api/config.py`
3. Ensure WebSocket URL is correct in frontend

### Kill Switch Activation

To manually halt all trading:

```bash
# Via API
curl -X POST http://localhost:8000/api/risk/kill-switch

# Via Dashboard
# Settings > Kill Switch > Activate
```

To resume trading:

```bash
# Via API
curl -X DELETE http://localhost:8000/api/risk/kill-switch
```

---

## Go/No-Go Criteria for Real Capital

| Metric | Threshold | Current |
|--------|-----------|---------|
| Expectancy | > 0 | TBD |
| Profit Factor | > 1.5 | TBD |
| Max Drawdown | < 8-10% | TBD |
| Trades Documented | >= 100 | 0 |
| Kill Switch | Tested | Yes |
| Risk Engine | Validated | Yes |

---

## Contributing

Contributions are welcome. Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Areas of Interest

- New strategy implementations (pullback, mean reversion, scalping)
- Additional exchange support (Binance, Bybit, OKX)
- Backtesting framework with historical data
- Performance analytics improvements
- Documentation and testing
- Docker containerization

---

## License

Distributed under the MIT License. See `LICENSE` for more information.

---

<div align="center">

**Built with discipline, not hope.**

</div>
