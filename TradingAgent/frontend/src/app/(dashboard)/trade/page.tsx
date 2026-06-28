"use client";

import { useState, useEffect } from "react";
import { Card } from "@/components/shared/Card";
import { GlowValue } from "@/components/shared/GlowValue";
import { Badge } from "@/components/shared/Badge";
import { fetchOpenTrades, fetchTradeDetail, fetchTradeMonitoring } from "@/lib/api";
import { Trade, TradeDetail, MonitoringLog } from "@/lib/types";
import { formatPrice, formatTime } from "@/lib/utils";

export default function TradePage() {
  const [openTrades, setOpenTrades] = useState<Trade[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [detail, setDetail] = useState<TradeDetail | null>(null);
  const [monitoring, setMonitoring] = useState<MonitoringLog[]>([]);

  useEffect(() => {
    let active = true;
    const load = async () => {
      try {
        const t = await fetchOpenTrades();
        if (active) {
          setOpenTrades(t);
          if (t.length > 0 && !selected) setSelected(t[0].trade_id);
        }
      } catch {}
    };
    load();
    const interval = setInterval(load, 15000);
    return () => { active = false; clearInterval(interval); };
  }, []);

  useEffect(() => {
    if (!selected) { setDetail(null); setMonitoring([]); return; }
    let active = true;
    const load = async () => {
      try {
        const [d, m] = await Promise.all([
          fetchTradeDetail(selected),
          fetchTradeMonitoring(selected).catch(() => []),
        ]);
        if (active) { setDetail(d); setMonitoring(m); }
      } catch {}
    };
    load();
    const interval = setInterval(load, 15000);
    return () => { active = false; clearInterval(interval); };
  }, [selected]);

  return (
    <div className="space-y-4">
      <h1 className="text-lg font-bold text-terminal-text">Posicion Abierta</h1>

      {openTrades.length === 0 ? (
        <Card title="Estado">
          <div className="text-terminal-muted text-center py-8">No hay posiciones abiertas en este momento.</div>
        </Card>
      ) : (
        <>
          <Card title="Posicion Activa" accent>
            {detail ? (
              <div className="grid grid-cols-6 gap-4">
                <GlowValue value={detail.trade_id} label="ID" color="info" size="sm" />
                <GlowValue value={detail.side === "LONG" ? "Compra" : "Venta"} label="Direccion" color={detail.side === "LONG" ? "accent" : "danger"} size="sm" />
                <GlowValue value={formatPrice(detail.entry_price)} label="Entrada" color="info" size="sm" />
                <GlowValue value={formatPrice(detail.stop_loss)} label="Proteccion" color="danger" size="sm" />
                <GlowValue value={formatPrice(detail.take_profit)} label="Objetivo" color="accent" size="sm" />
                <GlowValue value={detail.strategy} label="Estrategia" color="info" size="sm" />
              </div>
            ) : (
              <div className="text-terminal-muted text-center py-4">Cargando...</div>
            )}
          </Card>

          {monitoring.length > 0 && (
            <Card title="Registro de Monitoreo">
              <div className="space-y-1 max-h-64 overflow-y-auto">
                {monitoring.map((m) => (
                  <div key={m.id} className="flex items-center gap-3 py-1 border-b border-terminal-border/50 last:border-0">
                    <span className="text-[10px] text-terminal-muted w-12">{formatTime(m.timestamp)}</span>
                    <Badge status={m.verdict as any} />
                    <span className="text-[10px] text-terminal-text">{m.reason}</span>
                    {m.regime_changed && <span className="text-[10px] text-terminal-warning">Cambio de Mercado</span>}
                  </div>
                ))}
              </div>
            </Card>
          )}
        </>
      )}
    </div>
  );
}
