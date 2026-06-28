export interface MarketContext {
  id: number;
  trade_id: string;
  timestamp: string;
  trend: string;
  volumen_score: number;
  volatility_score: number;
  session_score: number;
  liquidity_score: number;
  spread_score: number;
  sentiment_score: number | null;
  funding_rate: number | null;
  open_interest: number | null;
  open_interest_value: number | null;
  rsi: number | null;
  adx: number | null;
  raw_data: Record<string, any> | null;
}

export interface Regime {
  id: number;
  regime: string;
  confidence: number;
  start_time: string;
  end_time: string | null;
  duration_minutes: number | null;
  adx: number | null;
  atr: number | null;
  rsi: number | null;
  volume_trend: string | null;
  recommended_strategies: string[] | null;
  historical_match: number | null;
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

export interface TradeDetail extends Trade {
  stop_loss: number;
  take_profit: number;
  position_size: number;
  capital_allocation: number;
  strategy_score: number;
  hypothesis_id: number | null;
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

export interface MonitoringLog {
  id: number;
  trade_id: string;
  timestamp: string;
  verdict: string;
  reason: string | null;
  context_delta: Record<string, any> | null;
  regime_changed: boolean;
  score_delta: number | null;
  action: string | null;
  action_percentage: number | null;
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

export interface StatsResponse {
  performance: PerformanceStats;
  by_strategy: StrategyStats[];
  by_regime: RegimeStats[];
}

export interface ComponentHealth {
  name: string;
  status: "ok" | "error";
  message: string | null;
}

export interface HealthResponse {
  status: string;
  timestamp: string;
  components: ComponentHealth[];
  summary: {
    total: number;
    ok: number;
    error: number;
  };
}
