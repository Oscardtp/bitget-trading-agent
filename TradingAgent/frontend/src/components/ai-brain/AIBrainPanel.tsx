"use client";

import { useState, useEffect } from "react";
import { Card } from "@/components/shared/Card";
import { GlowValue } from "@/components/shared/GlowValue";
import { Badge } from "@/components/shared/Badge";
import { useLiveEvents } from "@/hooks/useLiveEvents";
import { fetchTrades, fetchOpenTrades, fetchMarketContext, fetchCurrentRegime, fetchStats } from "@/lib/api";
import { Trade, MarketContext, Regime, StatsResponse } from "@/lib/types";
import { formatPrice, pnlColor, formatTime } from "@/lib/utils";
import { getEventLabel, getEventIcon, getRegimeLabel } from "@/lib/eventLabels";

function getDiagnosis(
  trend: string,
  volumeTrend: string | null,
): { label: string; color: string } {
  const vt = volumeTrend || "stable";

  if (trend === "bullish") {
    if (vt === "increasing") return { label: "Subida con Fuerza", color: "accent" };
    if (vt === "decreasing") return { label: "Subida Débil", color: "warning" };
    return { label: "Alcista Neutral", color: "accent" };
  }

  if (trend === "bearish") {
    if (vt === "increasing") return { label: "Caída con Fuerza", color: "danger" };
    if (vt === "decreasing") return { label: "Caída Débil", color: "warning" };
    return { label: "Bajista Neutral", color: "danger" };
  }

  if (vt === "increasing") return { label: "Lateral Activo", color: "warning" };
  if (vt === "decreasing") return { label: "Lateral Inactivo", color: "info" };
  return { label: "Lateral Neutro", color: "warning" };
}

export function AIBrainPanel() {
  const { events } = useLiveEvents();
  const [trades, setTrades] = useState<Trade[]>([]);
  const [openTrades, setOpenTrades] = useState<Trade[]>([]);
  const [context, setContext] = useState<MarketContext | null>(null);
  const [regime, setRegime] = useState<Regime | null>(null);
  const [stats, setStats] = useState<StatsResponse | null>(null);

  useEffect(() => {
    let active = true;
    const load = async () => {
      try {
        const [t, o, c, r, s] = await Promise.all([
          fetchTrades(10),
          fetchOpenTrades(),
          fetchMarketContext().catch(() => null),
          fetchCurrentRegime().catch(() => null),
          fetchStats().catch(() => null),
        ]);
        if (active) { setTrades(t); setOpenTrades(o); setContext(c); setRegime(r); setStats(s); }
      } catch {}
    };
    load();
    const interval = setInterval(load, 15000);
    return () => { active = false; clearInterval(interval); };
  }, []);

  const latestEvent = events[0];
  const diagnosis = context ? getDiagnosis(context.trend, regime?.volume_trend ?? null) : null;

  return (
    <div className="grid grid-cols-12 gap-4 h-full">
      {/* Left column */}
      <div className="col-span-8 flex flex-col gap-4">
        {/* Live Event Banner */}
        {latestEvent && (
          <Card title="Última Actividad" accent>
            <div className="flex items-center gap-4">
              <Badge status={latestEvent.event_type.includes("WIN") ? "WIN" : latestEvent.event_type.includes("LOSS") ? "LOSS" : "ACTIVE"} />
              <span className="text-sm text-terminal-text font-mono">{getEventLabel(latestEvent.event_type)}</span>
              <span className="text-xs text-terminal-muted">{formatTime(latestEvent.timestamp)}</span>
              {latestEvent.trade_id && (
                <span className="text-xs text-terminal-muted">{latestEvent.trade_id}</span>
              )}
            </div>
          </Card>
        )}

        {/* Unified Context Card */}
        {context && regime && (
          <Card title="Contexto del Mercado" accent>
            {/* Row 1: Diagnosis, Regime, Confidence, Volatility, Liquidity */}
            <div className="grid grid-cols-5 gap-4">
              <GlowValue
                value={diagnosis?.label || "Calculando..."}
                label="Diagnóstico"
                color={(diagnosis?.color || "info") as "accent" | "warning" | "danger" | "info"}
                size="sm"
              />
              <GlowValue value={getRegimeLabel(regime.regime)} label="Estado" color="accent" size="sm" />
              <GlowValue value={`${(regime.confidence * 100).toFixed(0)}%`} label="Confianza" color="info" size="sm" />
              <GlowValue value={`${(context.volatility_score * 100).toFixed(0)}%`} label="Volatilidad" color={context.volatility_score > 0.6 ? "danger" : "warning"} size="sm" />
              <GlowValue value={`${(context.liquidity_score * 100).toFixed(0)}%`} label="Liquididad" color={context.liquidity_score > 0.5 ? "accent" : "warning"} size="sm" />
            </div>
            {/* Row 2: ATR, Strategies */}
            <div className="grid grid-cols-5 gap-4 mt-4">
              <GlowValue value={regime.atr != null ? `$${regime.atr.toFixed(0)}` : "--"} label="ATR" color="warning" size="sm" />
              <GlowValue value={regime.recommended_strategies?.join(", ") || "--"} label="Estrategias" color="info" size="sm" />
            </div>
          </Card>
        )}

        {/* Performance - Compact */}
        {stats && (
          <Card title="Rendimiento">
            <div className="grid grid-cols-4 gap-4">
              <GlowValue value={stats.performance.total_trades} label="Operaciones" color="info" size="sm" />
              <GlowValue value={`${(stats.performance.win_rate * 100).toFixed(1)}%`} label="Tasa de Acierto" color={stats.performance.win_rate >= 0.5 ? "accent" : "danger"} size="sm" />
              <GlowValue value={stats.performance.profit_factor.toFixed(2)} label="Factor de Beneficio" color={stats.performance.profit_factor >= 1 ? "accent" : "danger"} size="sm" />
              <GlowValue value={`${stats.performance.expectancy >= 0 ? "+" : ""}${stats.performance.expectancy.toFixed(2)}`} label="Beneficio Esperado" color={stats.performance.expectancy >= 0 ? "accent" : "danger"} size="sm" />
            </div>
          </Card>
        )}
      </div>

      {/* Right column */}
      <div className="col-span-4 flex flex-col gap-4">
        {/* Open Positions */}
        <Card title="Posiciones Abiertas">
          {openTrades.length === 0 ? (
            <div className="text-xs text-terminal-muted text-center py-4">No hay posiciones abiertas.</div>
          ) : (
            <div className="space-y-2">
              {openTrades.map((t) => (
                <div key={t.trade_id} className="p-2 bg-terminal-bg rounded border border-terminal-border">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-terminal-text font-mono">{t.trade_id}</span>
                    <Badge status="ACTIVE" />
                  </div>
                  <div className="flex items-center gap-3 mt-1">
                    <span className={`text-xs ${t.side === "LONG" ? "text-terminal-accent" : "text-terminal-danger"}`}>{t.side === "LONG" ? "Compra" : "Venta"}</span>
                    <span className="text-xs text-terminal-muted">{formatPrice(t.entry_price)}</span>
                    <span className="text-xs text-terminal-muted">{t.strategy}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>

        {/* Recent Trades */}
        <Card title="Operaciones Recientes" className="flex-1">
          <div className="space-y-1 overflow-y-auto max-h-64">
            {trades.length === 0 ? (
              <div className="text-xs text-terminal-muted text-center py-4">Aún no se han registrado operaciones.</div>
            ) : (
              trades.map((t) => (
                <div key={t.trade_id} className="flex items-center justify-between py-1 border-b border-terminal-border/50 last:border-0">
                  <div className="flex items-center gap-2">
                    <span className={`text-[10px] ${t.side === "LONG" ? "text-terminal-accent" : "text-terminal-danger"}`}>{t.side === "LONG" ? "Compra" : "Venta"}</span>
                    <span className="text-[10px] text-terminal-muted">{formatTime(t.entry_timestamp)}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] text-terminal-muted">{t.strategy}</span>
                    {t.result && <Badge status={t.result} />}
                  </div>
                </div>
              ))
            )}
          </div>
        </Card>

        {/* Event Timeline */}
        <Card title="Historial de Actividad" className="flex-1">
          <div className="space-y-1 overflow-y-auto max-h-64">
            {events.length === 0 ? (
              <div className="text-xs text-terminal-muted text-center py-4">Esperando actividad del sistema...</div>
            ) : (
              events.slice(0, 15).map((e, i) => (
                <div key={i} className="flex items-center gap-2 py-1">
                  <span className="text-[10px] text-terminal-muted w-12">{formatTime(e.timestamp)}</span>
                  <span className="text-xs">{getEventIcon(e.event_type)}</span>
                  <span className="text-[10px] text-terminal-text">{getEventLabel(e.event_type)}</span>
                </div>
              ))
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}
