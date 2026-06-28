"use client";

import { useState, useEffect } from "react";
import { useLiveEvents } from "@/hooks/useLiveEvents";

export function Header() {
  const { isConnected } = useLiveEvents();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const now = new Date();
  const dateStr = now.toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" });
  const timeStr = now.toLocaleTimeString("en-US", { hour12: false });

  return (
    <header className="h-10 bg-terminal-card border-b border-terminal-border flex items-center justify-between px-6 shrink-0">
      <div className="flex items-center gap-4">
        <span className="text-xs text-terminal-muted">{dateStr}</span>
        <span className="text-xs text-terminal-text font-mono">
          {mounted ? timeStr : "--:--:--"}
        </span>
      </div>
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${isConnected ? "bg-terminal-accent animate-pulse-glow" : "bg-terminal-danger"}`} />
          <span className="text-[10px] text-terminal-muted">{isConnected ? "LIVE" : "OFFLINE"}</span>
        </div>
        <span className="text-[10px] text-terminal-muted">BTC/USDT</span>
      </div>
    </header>
  );
}
