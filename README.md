<div align="center">

# Bitget Trading Agent

### Multi-timeframe algorithmic trading system with AI-powered regime detection

[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e.svg)](LICENSE)
[![Python 3.14](https://img.shields.io/badge/Python-3.14-3b82f6.svg)](https://python.org)
[![Next.js 15](https://img.shields.io/badge/Next.js-15-black)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com)
[![Bitget](https://img.shields.io/badge/Bitget-ccxt-ff6600.svg)](https://ccxt.com)
[![Status](https://img.shields.io/badge/Status-Paper%20Trading-yellow)]()

<br/>

**The entry is irrelevant. Management is everything.**

A systematic trading agent that tests hypotheses across multiple timeframes,
adapts to market regimes, and manages risk dynamically — all with full lifecycle
logging and a real-time monitoring dashboard.

[Architecture](#architecture) &bull; [Features](#features) &bull; [Quick Start](#quick-start) &bull; [Dashboard](#dashboard) &bull; [Contributing](#contributing)

</div>

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

<br/>

## Features

### Multi-Timeframe Intelligence

- **1H Context** — Market trend, regime, and session analysis
- **15M Signal** — Breakout detection with volume confirmation
- **5M Entry** — Precision timing with orderbook depth
- Each timeframe answers one specific question

### AI Regime Detection

- **8 market regimes** with confidence scoring
- Regime-adaptive strategy selection
- Real-time indicator computation (ADX, RSI, Bollinger)
- Historical pattern matching

### Dynamic Risk Management

- **DrawdownManager** — 3F-R protection with adaptive sizing
- **Kill Switch** — Instant halt capability
- **Trailing Stops** — 3-stage profit protection
- **Daily Limits** — Max 5 trades/day, max 1 position

### Hypothesis-Driven Execution

- Every trade is a **testable thesis**
- Structured logging: 12 fields per operation
- Verdict tracking: CONFIRMED / INVALIDATED
- Full lifecycle timeline in Event Store

### Paper Trading

- Real orderbook spread simulation
- Slippage modeling (0.05%)
- Commission simulation (0.1%)
- Execution delay (100-500ms)

### Real-Time Dashboard

- AI reasoning visualization
- Live market context and regime
- Trade timeline with event filtering
- Performance metrics and system health

<br/>

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Exchange | [ccxt](https://github.com/ccxt/ccxt) | Bitget market data |
| Data | Pandas, NumPy | OHLCV processing, indicators |
| Database | SQLite (WAL) | Trade and event persistence |
| API | FastAPI, WebSocket | Real-time data bridge |
| Frontend | Next.js 15, React 19 | Monitoring dashboard |
| Styling | Tailwind CSS v4 | Dark terminal theme |
| Config | Pydantic Settings | Environment management |

<br/>

## Quick Start

### Prerequisites

- Python 3.14+
- Node.js 18+
- npm or yarn

### Installation

```bash
# Clone the repository
git clone https://github.com/Oscardtp/bitget-trading-agent.git
cd bitget-trading-agent

# Install Python dependencies
cd TradingAgent
pip install -r requirements.txt

# Configure environment (optional for paper trading)
cp .env.example .env

# Install frontend dependencies
cd frontend
npm install
```

### Running

```bash
# Terminal 1: Backend + Trading Bot
cd TradingAgent
python run.py --log-level INFO

# Terminal 2: Dashboard
cd TradingAgent/frontend
npm run dev
```

Dashboard: http://localhost:3000
API: http://localhost:8000

<br/>

## Dashboard

Five screens designed for **systematic traders** who think in probabilities:

| Screen | Purpose |
|--------|---------|
| **Dashboard** | AI brain — live context, regime, performance, trades |
| **Market** | Metrics grid — volatility, volume, liquidity, funding, OI |
| **Trades** | Open positions, entry/exit, PnL tracking |
| **History** | Trade timeline, performance statistics, event logs |
| **Settings** | System health, configuration, kill switch |

> **Design philosophy:** Agent reasoning is the protagonist. Charts are secondary context.

<br/>

## Strategy Phases

Rollout is **phased** — each strategy must validate before the next activates:

| Phase | Strategies | Capital Allocation | Status |
|-------|-----------|-------------------|--------|
| 1 | Breakout (acceptance) | 100% | Active |
| 2 | + Pullback | 70% / 30% | Planned |
| 3 | + Mean Reversion | 50% / 25% / 25% | Planned |
| 4 | + Scalping | 40% / 20% / 20% / 20% | Planned |

### Go/No-Go Criteria for Real Capital

| Metric | Threshold |
|--------|-----------|
| Expectancy | > 0 |
| Profit Factor | > 1.5 |
| Max Drawdown | < 8-10% |
| Trades Documented | >= 100 |
| Kill Switch | Tested |
| Risk Engine | Validated |

<br/>

## Risk Rules

```
POSITION SIZING
+-- Base risk:        0.5% - 2% per trade
+-- After 3 losses:   0.25%
+-- R:R minimum:      2:1
+-- Daily limit:      5 trades
+-- Max positions:    1

PROTECTION LAYERS
+-- Structure-based SL (ATR)
+-- 3-stage trailing stop
+-- ThesisMonitor (regime/volume/confidence)
+-- DrawdownManager (3F-R)
+-- Kill Switch (manual or auto)
```

<br/>

## Project Structure

```
TradingAgent/
+-- main_loop.py          # Core trading loop
+-- run.py                # Unified entry point (API + Bot)
+-- api/                  # FastAPI backend
+-- config/               # Settings
+-- context/              # Multi-timeframe context, indicators
+-- data/                 # Exchange client, market data
+-- db/                   # SQLite models
+-- execution/            # Order execution (future)
+-- filters/              # No-trade filters
+-- hypothesis/           # Hypothesis builder
+-- logs/                 # Event store, log manager
+-- monitor/              # Thesis monitor
+-- regime/               # Regime detector
+-- risk/                 # Drawdown, kill switch, position sizing
+-- strategies/           # Strategy orchestrator, breakout, pullback
+-- validation/           # Metrics tracking
+-- frontend/             # Next.js dashboard
```

<br/>

## Contributing

Contributions are welcome. Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Areas of Interest

- New strategy implementations (pullback, mean reversion, scalping)
- Additional exchange support
- Backtesting framework
- Performance analytics improvements
- Documentation and testing

<br/>

## License

Distributed under the MIT License. See `LICENSE` for more information.

<br/>

<div align="center">

**Built with discipline, not hope.**

</div>
