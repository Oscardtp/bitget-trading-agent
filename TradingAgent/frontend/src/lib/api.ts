import {
  MarketContext,
  Regime,
  Trade,
  TradeDetail,
  Event,
  MonitoringLog,
  StatsResponse,
  HealthResponse,
} from "./types";

const API_BASE = "http://localhost:8000";

async function fetchJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`API error: ${res.status} ${res.statusText}`);
  return res.json();
}

export async function fetchHealth(): Promise<HealthResponse> {
  return fetchJSON("/api/health");
}

export async function fetchMarketContext(): Promise<MarketContext> {
  return fetchJSON("/api/market/context");
}

export async function fetchCurrentRegime(): Promise<Regime> {
  return fetchJSON("/api/market/regime");
}

export async function fetchTrades(limit = 50): Promise<Trade[]> {
  return fetchJSON(`/api/trades/?limit=${limit}`);
}

export async function fetchOpenTrades(): Promise<Trade[]> {
  return fetchJSON("/api/trades/open");
}

export async function fetchTradeDetail(tradeId: string): Promise<TradeDetail> {
  return fetchJSON(`/api/trades/${tradeId}`);
}

export async function fetchTradeTimeline(tradeId: string): Promise<Event[]> {
  return fetchJSON(`/api/trades/${tradeId}/timeline`);
}

export async function fetchTradeMonitoring(tradeId: string): Promise<MonitoringLog[]> {
  return fetchJSON(`/api/trades/${tradeId}/monitoring`);
}

export async function fetchStats(): Promise<StatsResponse> {
  return fetchJSON("/api/stats/");
}

export async function fetchEvents(limit = 100): Promise<Event[]> {
  return fetchJSON(`/api/events?limit=${limit}`);
}
