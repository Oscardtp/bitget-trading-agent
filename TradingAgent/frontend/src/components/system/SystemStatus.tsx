"use client";

import { useHealth } from "@/hooks/useHealth";
import { ComponentHealth } from "@/lib/types";

const STATUS_ICONS: Record<string, string> = {
  ok: "O",
  error: "X",
};

export function SystemStatus() {
  const health = useHealth();

  if (!health) {
    return (
      <div className="rounded-lg border border-terminal-border bg-terminal-bg p-4">
        <div className="mb-3 text-xs font-semibold uppercase tracking-wider text-terminal-muted">
          Estado del Sistema
        </div>
        <div className="text-sm text-terminal-muted">Cargando...</div>
      </div>
    );
  }

  return (
    <div className={`rounded-lg border p-4 ${
      health.status === "ok"
        ? "border-terminal-accent/30 bg-terminal-accent/5"
        : "border-terminal-danger/30 bg-terminal-danger/5"
    }`}>
      <div className="mb-3 flex items-center justify-between">
        <div className={`text-xs font-semibold uppercase tracking-wider ${
          health.status === "ok" ? "text-terminal-accent" : "text-terminal-danger"
        }`}>
          Estado del Sistema
        </div>
        <div className={`text-xs ${
          health.status === "ok" ? "text-terminal-accent" : "text-terminal-danger"
        }`}>
          {health.summary.ok}/{health.summary.total} OK
        </div>
      </div>

      <div className="space-y-2">
        {health.components.map((comp: ComponentHealth) => (
          <div
            key={comp.name}
            className={`flex items-center justify-between rounded border px-3 py-2 ${
              comp.status === "ok"
                ? "border-terminal-accent/20 bg-terminal-accent/5"
                : "border-terminal-danger/20 bg-terminal-danger/5"
            }`}
          >
            <div className="flex items-center gap-2">
              <span className={`font-mono text-sm font-bold ${
                comp.status === "ok" ? "text-terminal-accent" : "text-terminal-danger"
              }`}>
                [{STATUS_ICONS[comp.status] || "?"}]
              </span>
              <span className="text-sm text-terminal-text">{comp.name}</span>
            </div>
            {comp.message && (
              <span className="text-xs text-terminal-muted">{comp.message}</span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
