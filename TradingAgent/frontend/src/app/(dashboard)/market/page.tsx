"use client";

import { useState, useEffect } from "react";
import { Card } from "@/components/shared/Card";
import { fetchMarketContext, fetchCurrentRegime } from "@/lib/api";
import { MarketContext, Regime } from "@/lib/types";
import { scoreToLabel, scoreToBar } from "@/lib/utils";
import { getRegimeLabel } from "@/lib/eventLabels";

interface MetricRow {
  label: string;
  value: string;
  bar: string;
  color: string;
}

function getDiagnosis(trend: string, volumeTrend: string | null): { label: string; color: string } {
  const vt = volumeTrend || "stable";
  if (trend === "bullish") {
    if (vt === "increasing") return { label: "Subida con Fuerza", color: "#22c55e" };
    if (vt === "decreasing") return { label: "Subida Débil", color: "#eab308" };
    return { label: "Alcista Neutral", color: "#22c55e" };
  }
  if (trend === "bearish") {
    if (vt === "increasing") return { label: "Caída con Fuerza", color: "#ef4444" };
    if (vt === "decreasing") return { label: "Caída Débil", color: "#eab308" };
    return { label: "Bajista Neutral", color: "#ef4444" };
  }
  if (vt === "increasing") return { label: "Lateral Activo", color: "#eab308" };
  if (vt === "decreasing") return { label: "Lateral Inactivo", color: "#6b7280" };
  return { label: "Lateral Neutro", color: "#eab308" };
}

function buildMetrics(context: MarketContext, regime: Regime | null): MetricRow[] {
  const diag = getDiagnosis(context.trend, regime?.volume_trend ?? null);

  const trendLabel = context.trend === "bullish" ? "Alcista" : context.trend === "bearish" ? "Bajista" : "Lateral";
  const trendColor = context.trend === "bullish" ? "#22c55e" : context.trend === "bearish" ? "#ef4444" : "#eab308";

  const regimeLabel = regime ? getRegimeLabel(regime.regime) : "N/A";
  const regimeColor = regime?.regime?.includes("bull") ? "#22c55e" : regime?.regime?.includes("bear") ? "#ef4444" : "#eab308";

  const volLabel = scoreToLabel(context.volatility_score, "risk");
  const volColor = context.volatility_score > 0.6 ? "#ef4444" : context.volatility_score > 0.3 ? "#eab308" : "#22c55e";

  const volumenLabel = scoreToLabel(context.volumen_score);
  const volumenColor = context.volumen_score > 0.6 ? "#22c55e" : context.volumen_score > 0.3 ? "#eab308" : "#ef4444";

  const liqLabel = scoreToLabel(context.liquidity_score);
  const liqColor = context.liquidity_score > 0.6 ? "#22c55e" : context.liquidity_score > 0.3 ? "#eab308" : "#ef4444";

  const spreadLabel = scoreToLabel(context.spread_score);
  const spreadColor = context.spread_score > 0.6 ? "#22c55e" : context.spread_score > 0.3 ? "#eab308" : "#ef4444";

  const sentimentLabel = scoreToLabel(context.sentiment_score, "sentiment");
  const sentimentColor = (context.sentiment_score ?? 0.5) >= 0.5 ? "#22c55e" : "#ef4444";

  const fundingLabel = context.funding_rate != null
    ? `${(context.funding_rate * 100).toFixed(3)}%`
    : "N/A";
  const fundingColor = (context.funding_rate ?? 0) >= 0 ? "#22c55e" : "#ef4444";

  const oiLabel = context.open_interest != null ? `${(context.open_interest / 1000).toFixed(1)}K` : "N/A";
  const oiColor = "#22c55e";

  return [
    { label: "Diagnóstico", value: diag.label, bar: "", color: diag.color },
    { label: "Tendencia", value: trendLabel, bar: scoreToBar(context.trend === "bullish" ? 0.8 : context.trend === "bearish" ? 0.2 : 0.5), color: trendColor },
    { label: "Estado", value: regimeLabel, bar: scoreToBar(regime?.confidence ?? 0.5), color: regimeColor },
    { label: "Volatilidad", value: volLabel, bar: scoreToBar(context.volatility_score), color: volColor },
    { label: "Volumen", value: volumenLabel, bar: scoreToBar(context.volumen_score), color: volumenColor },
    { label: "Liquididad", value: liqLabel, bar: scoreToBar(context.liquidity_score), color: liqColor },
    { label: "Spread", value: spreadLabel, bar: scoreToBar(context.spread_score), color: spreadColor },
    { label: "Sentimiento", value: sentimentLabel, bar: scoreToBar(context.sentiment_score ?? 0.5), color: sentimentColor },
    { label: "Funding", value: fundingLabel, bar: scoreToBar(Math.min(Math.max(((context.funding_rate ?? 0) + 0.001) / 0.002), 0), 1), color: fundingColor },
    { label: "Open Interest", value: oiLabel, bar: scoreToBar(context.open_interest != null ? Math.min(context.open_interest / 100000, 1) : 0.5), color: oiColor },
  ];
}

export default function MarketPage() {
  const [context, setContext] = useState<MarketContext | null>(null);
  const [regime, setRegime] = useState<Regime | null>(null);

  useEffect(() => {
    let active = true;
    const load = async () => {
      try {
        const [c, r] = await Promise.all([
          fetchMarketContext().catch(() => null),
          fetchCurrentRegime().catch(() => null),
        ]);
        if (active) { setContext(c); setRegime(r); }
      } catch {}
    };
    load();
    const interval = setInterval(load, 15000);
    return () => { active = false; clearInterval(interval); };
  }, []);

  const metrics = context ? buildMetrics(context, regime) : [];

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center gap-3">
        <h1 className="text-lg font-bold text-terminal-text">BTC/USDT</h1>
        <span className="text-xs text-terminal-muted font-mono">Perpetuo</span>
      </div>

      {/* Metrics Grid - Full Width */}
      <Card title="Métricas del Mercado" accent>
        <div className="space-y-1">
          {metrics.map((m) => (
            <div key={m.label} className="flex items-center gap-3 py-1.5 border-b border-terminal-border/30 last:border-0">
              <span className="text-xs text-terminal-muted w-28 font-mono">{m.label}</span>
              <span className="text-xs font-bold w-28" style={{ color: m.color }}>{m.value}</span>
              {m.bar && <span className="text-[10px] text-terminal-muted font-mono tracking-wider">{m.bar}</span>}
            </div>
          ))}
        </div>
      </Card>

      {/* Loading state */}
      {!context && (
        <div className="text-terminal-muted text-center py-12">Esperando datos del mercado...</div>
      )}
    </div>
  );
}
