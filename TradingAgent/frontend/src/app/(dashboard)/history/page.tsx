"use client";

import { useState, useEffect } from "react";
import { Card } from "@/components/shared/Card";
import { GlowValue } from "@/components/shared/GlowValue";
import { Badge } from "@/components/shared/Badge";
import { TradeTimelineDrawer } from "@/components/history/TradeTimelineDrawer";
import { fetchTrades, fetchStats } from "@/lib/api";
import { Trade, StatsResponse } from "@/lib/types";
import { formatPrice, formatTime, formatPnl, pnlColor } from "@/lib/utils";
import { History } from "lucide-react";

export default function HistoryPage() {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [selectedTradeId, setSelectedTradeId] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    const load = async () => {
      try {
        const [t, s] = await Promise.all([fetchTrades(50), fetchStats()]);
        if (active) { setTrades(t); setStats(s); }
      } catch {}
    };
    load();
    return () => { active = false; };
  }, []);

  return (
    <div className="space-y-4">
      <h1 className="text-lg font-bold text-terminal-text">Historial de Operaciones</h1>

      {stats && (
        <Card title="Rendimiento General" accent>
          <div className="grid grid-cols-5 gap-4">
            <GlowValue value={stats.performance.total_trades} label="Total Operaciones" color="info" size="sm" />
            <GlowValue value={`${(stats.performance.win_rate * 100).toFixed(1)}%`} label="Tasa de Acierto" color={stats.performance.win_rate >= 0.5 ? "accent" : "danger"} size="sm" />
            <GlowValue value={stats.performance.profit_factor.toFixed(2)} label="Factor de Beneficio" color={stats.performance.profit_factor >= 1 ? "accent" : "danger"} size="sm" />
            <GlowValue value={`${stats.performance.expectancy >= 0 ? "+" : ""}${stats.performance.expectancy.toFixed(2)}`} label="Beneficio Esperado" color={stats.performance.expectancy >= 0 ? "accent" : "danger"} size="sm" />
            <GlowValue value={stats.performance.avg_duration_minutes?.toFixed(0) || "--"} label="Duracion Promedio (min)" color="info" size="sm" />
          </div>
        </Card>
      )}

      <Card title="Todas las Operaciones">
        {trades.length === 0 ? (
          <div className="text-terminal-muted text-center py-8">Aun no se han registrado operaciones.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-terminal-border text-terminal-muted">
                  <th className="text-left py-2 px-2">ID</th>
                  <th className="text-left py-2 px-2">Hora</th>
                  <th className="text-left py-2 px-2">Direccion</th>
                  <th className="text-left py-2 px-2">Estrategia</th>
                  <th className="text-right py-2 px-2">Entrada</th>
                  <th className="text-right py-2 px-2">Salida</th>
                  <th className="text-right py-2 px-2">Beneficio</th>
                  <th className="text-center py-2 px-2">Resultado</th>
                  <th className="text-center py-2 px-2">Registro</th>
                </tr>
              </thead>
              <tbody>
                {trades.map((t) => (
                  <tr key={t.trade_id} className="border-b border-terminal-border/30 hover:bg-terminal-border/20">
                    <td className="py-2 px-2 font-mono text-terminal-muted">{t.trade_id}</td>
                    <td className="py-2 px-2 text-terminal-muted">{formatTime(t.entry_timestamp)}</td>
                    <td className={`py-2 px-2 ${t.side === "LONG" ? "text-terminal-accent" : "text-terminal-danger"}`}>{t.side === "LONG" ? "Compra" : "Venta"}</td>
                    <td className="py-2 px-2 text-terminal-muted">{t.strategy}</td>
                    <td className="py-2 px-2 text-right">{formatPrice(t.entry_price)}</td>
                    <td className="py-2 px-2 text-right">{formatPrice(t.exit_price)}</td>
                    <td className={`py-2 px-2 text-right font-mono ${pnlColor(t.net_pnl)}`}>{formatPnl(t.net_pnl)}</td>
                    <td className="py-2 px-2 text-center">{t.result ? <Badge status={t.result} /> : <Badge status="PENDING" />}</td>
                    <td className="py-2 px-2 text-center">
                      <button
                        onClick={() => setSelectedTradeId(t.trade_id)}
                        className="p-1.5 rounded hover:bg-terminal-border/50 transition-colors text-terminal-muted hover:text-terminal-accent"
                        title="Ver registro"
                      >
                        <History size={14} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      <TradeTimelineDrawer
        tradeId={selectedTradeId}
        onClose={() => setSelectedTradeId(null)}
      />
    </div>
  );
}
