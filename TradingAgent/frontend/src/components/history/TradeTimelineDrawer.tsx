"use client";

import { useState, useEffect } from "react";
import {
  Lightbulb,
  ShieldCheck,
  Crosshair,
  Eye,
  TrendingUp,
  CircleX,
  ClipboardCheck,
  X,
  Loader2,
  AlertTriangle,
} from "lucide-react";
import { fetchTradeTimeline } from "@/lib/api";
import { Event } from "@/lib/types";
import { formatTime } from "@/lib/utils";
import { getEventLabel } from "@/lib/eventLabels";

const EVENT_ICONS: Record<string, React.ComponentType<{ size?: number; className?: string }>> = {
  HYPOTHESIS_CREATED: Lightbulb,
  RISK_CALCULATED: ShieldCheck,
  ENTRY: Crosshair,
  MONITOR_CHECK: Eye,
  TRAILING_UPDATE: TrendingUp,
  EXIT: CircleX,
  TRADE_RESULT: ClipboardCheck,
  ERROR: AlertTriangle,
};

const EVENT_COLORS: Record<string, string> = {
  HYPOTHESIS_CREATED: "text-blue-400",
  RISK_CALCULATED: "text-amber-400",
  ENTRY: "text-green-400",
  MONITOR_CHECK: "text-slate-400",
  TRAILING_UPDATE: "text-cyan-400",
  EXIT: "text-red-400",
  TRADE_RESULT: "text-purple-400",
  ERROR: "text-red-500",
};

const RELEVANT_EVENTS = [
  "HYPOTHESIS_CREATED",
  "RISK_CALCULATED",
  "ENTRY",
  "MONITOR_CHECK",
  "TRAILING_UPDATE",
  "EXIT",
  "TRADE_RESULT",
  "ERROR",
];

function getEventDetail(event: Event): string | null {
  const d = event.data || {};
  switch (event.event_type) {
    case "HYPOTHESIS_CREATED":
      return d.probability != null
        ? `Probabilidad: ${(d.probability * 100).toFixed(0)}%`
        : null;
    case "RISK_CALCULATED":
      return d.risk_pct != null
        ? `Riesgo: ${(d.risk_pct * 100).toFixed(1)}%${d.stop_loss ? ` | SL: $${d.stop_loss}` : ""}`
        : null;
    case "ENTRY":
      return `${d.side || ""} @ $${d.entry_price || "?"}${d.strategy ? ` | ${d.strategy}` : ""}`;
    case "MONITOR_CHECK":
      return d.action ? `${d.verdict || ""}: ${d.reason || ""}` : null;
    case "TRAILING_UPDATE":
      return d.new_stop_loss ? `Nuevo SL: $${d.new_stop_loss}` : null;
    case "EXIT":
      return [
        d.exit_price ? `Salida: $${d.exit_price}` : null,
        d.reason || null,
        d.duration_minutes ? `${d.duration_minutes}min` : null,
      ]
        .filter(Boolean)
        .join(" | ");
    case "TRADE_RESULT":
      return d.result
        ? `${d.result}${d.pnl_pct != null ? ` | PnL: ${d.pnl_pct >= 0 ? "+" : ""}${(d.pnl_pct * 100).toFixed(2)}%` : ""}`
        : null;
    case "ERROR":
      return d.message || "Error desconocido";
    default:
      return null;
  }
}

interface TradeTimelineDrawerProps {
  tradeId: string | null;
  onClose: () => void;
}

export function TradeTimelineDrawer({ tradeId, onClose }: TradeTimelineDrawerProps) {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!tradeId) {
      setEvents([]);
      return;
    }

    let active = true;
    setLoading(true);

    fetchTradeTimeline(tradeId)
      .then((data) => {
        if (active) {
          const filtered = data.filter((e) => RELEVANT_EVENTS.includes(e.event_type));
          setEvents(filtered);
        }
      })
      .catch(() => {
        if (active) setEvents([]);
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [tradeId]);

  if (!tradeId) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      {/* Overlay */}
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />

      {/* Drawer */}
      <div className="relative w-[480px] bg-terminal-surface border-l border-terminal-border shadow-2xl flex flex-col animate-slide-in">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-terminal-border">
          <div className="flex items-center gap-2">
            <span className="text-sm font-bold text-terminal-text">Registro:</span>
            <span className="text-sm font-mono text-terminal-accent">#{tradeId}</span>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded hover:bg-terminal-border/50 transition-colors"
          >
            <X size={18} className="text-terminal-muted" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto px-5 py-4">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 size={24} className="text-terminal-accent animate-spin" />
            </div>
          ) : events.length === 0 ? (
            <div className="text-terminal-muted text-center py-12 text-sm">
              No hay eventos registrados para esta operacion.
            </div>
          ) : (
            <div className="relative">
              {/* Vertical line */}
              <div className="absolute left-[52px] top-0 bottom-0 w-px bg-terminal-border" />

              {/* Events */}
              <div className="space-y-4">
                {events.map((event, i) => {
                  const Icon = EVENT_ICONS[event.event_type] || AlertTriangle;
                  const color = EVENT_COLORS[event.event_type] || "text-terminal-muted";
                  const label = getEventLabel(event.event_type);
                  const detail = getEventDetail(event);

                  return (
                    <div key={event.id || i} className="flex gap-3">
                      {/* Timestamp */}
                      <div className="w-[44px] flex-shrink-0 text-right">
                        <span className="text-[10px] font-mono text-terminal-muted leading-5">
                          {formatTime(event.timestamp)}
                        </span>
                      </div>

                      {/* Icon circle */}
                      <div className="relative z-10 flex-shrink-0">
                        <div className={`w-[22px] h-[22px] rounded-full bg-terminal-bg border border-terminal-border flex items-center justify-center ${color}`}>
                          <Icon size={12} />
                        </div>
                      </div>

                      {/* Content */}
                      <div className="flex-1 min-w-0 pt-0.5">
                        <div className="text-xs font-semibold text-terminal-text leading-5">
                          {label}
                        </div>
                        {detail && (
                          <div className="text-[11px] text-terminal-muted leading-4 mt-0.5">
                            {detail}
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
