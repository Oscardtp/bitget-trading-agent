# Bitget Trading Agent

Multi-timeframe algorithmic trading agent for Bitget with AI-powered market regime detection, hypothesis-driven strategy execution, and real-time monitoring dashboard.

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  1H Context  │────▶│ 15M Signal   │────▶│  5M Entry    │
│  (Trend)     │     │ (Breakout)   │     │ (Precision)  │
└─────────────┘     └──────────────┘     └──────────────┘
       │                    │                    │
       ▼                    ▼                    ▼
  Regime Detection    Strategy Filter     Risk Management
  (8 regimes)         (R:R ≥ 2:1)        (0.5-2% per trade)
```

## Features

- **Multi-Timeframe Pipeline**: 1H context → 15M signal → 5M entry optimization
- **Market Regime Detection**: 8 regimes with confidence scoring and strategy recommendations
- **Hypothesis-Driven Execution**: Every trade is a testable thesis with structured logging
- **Dynamic Risk Management**: DrawdownManager, Kill Switch, trailing stops, daily trade limits
- **Paper Trading**: Realistic simulation with real orderbook spread, slippage, and commission
- **Real-Time Dashboard**: AI reasoning, market context, trades, and performance metrics
- **Event Store**: Full lifecycle timeline for every trade decision

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Exchange | [ccxt](https://github.com/ccxt/ccxt) (Bitget) |
| Data | Pandas, NumPy |
| Database | SQLite (WAL mode) |
| Backend API | FastAPI, Uvicorn, WebSocket |
| Frontend | Next.js 15, React 19, TypeScript, Tailwind CSS v4 |
| Config | Pydantic Settings |

## Quick Start

### 1. Install Python dependencies

```bash
cd TradingAgent
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your Bitget API keys (optional for paper trading)
```

### 3. Install frontend dependencies

```bash
cd frontend
npm install
```

### 4. Run

```bash
# Terminal 1: Backend + Bot
cd TradingAgent
python run.py

# Terminal 2: Dashboard
cd TradingAgent/frontend
npm run dev
```

Dashboard available at [http://localhost:3000](http://localhost:3000)

## Dashboard

The real-time monitoring dashboard provides:

- **AI Brain**: Live market context, regime detection, and system reasoning
- **Market**: Metrics radar, funding rates, open interest, sentiment
- **Trades**: Open positions, entry/exit prices, PnL tracking
- **History**: Trade timeline, performance statistics, event logs
- **Settings**: System health, configuration, kill switch

## Strategy Phases

| Phase | Strategies | Status |
|-------|-----------|--------|
| 1 | Breakout (acceptance) | Active |
| 2 | + Pullback | Planned |
| 3 | + Mean Reversion | Planned |
| 4 | + Scalping | Planned |

## Risk Rules

- Position size: 0.5-2% of capital per trade
- Risk/Reward minimum: 2:1
- 3 consecutive losses → risk reduces to 0.25%
- Daily trade limit: 5 trades
- Kill switch available for immediate halt

## Project Structure

```
TradingAgent/
├── main_loop.py          # Core trading loop
├── run.py                # Unified entry point (API + Bot)
├── api/                  # FastAPI backend
├── config/               # Settings
├── context/              # Multi-timeframe context, indicators
├── data/                 # Exchange client, market data
├── db/                   # SQLite models
├── execution/            # Order execution (future)
├── filters/              # No-trade filters
├── hypothesis/           # Hypothesis builder
├── logs/                 # Event store, log manager
├── monitor/              # Thesis monitor
├── regime/               # Regime detector
├── risk/                 # Drawdown, kill switch, position sizing
├── strategies/           # Strategy orchestrator, breakout, pullback
├── validation/           # Metrics tracking
└── frontend/             # Next.js dashboard
```

## Contributing

Contributions welcome. Areas of interest:

- New strategy implementations (pullback, mean reversion, scalping)
- Additional exchange support
- Backtesting framework
- Performance analytics improvements
- Documentation and testing

## License

MIT
