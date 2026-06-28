"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Brain, Activity, BarChart3, History, Settings } from "lucide-react";

const navItems = [
  { href: "/", label: "Cerebro IA", icon: Brain },
  { href: "/market", label: "Mercado", icon: Activity },
  { href: "/trade", label: "Operacion", icon: BarChart3 },
  { href: "/history", label: "Historial", icon: History },
  { href: "/settings", label: "Configuracion", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-56 bg-terminal-card border-r border-terminal-border flex flex-col shrink-0">
      <div className="p-4 border-b border-terminal-border">
        <h1 className="text-sm font-bold text-terminal-accent tracking-wider">
          TRADING AGENT
        </h1>
        <p className="text-[10px] text-terminal-muted mt-1">Dashboard v1.0</p>
      </div>

      <nav className="flex-1 p-3">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2 rounded mb-1 text-sm transition-colors ${
                isActive
                  ? "bg-terminal-accent/10 text-terminal-accent"
                  : "text-terminal-muted hover:text-terminal-text hover:bg-terminal-border/50"
              }`}
            >
              <Icon size={16} />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="p-3 border-t border-terminal-border">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-terminal-accent animate-pulse-glow" />
          <span className="text-[10px] text-terminal-muted">Agente Activo</span>
        </div>
      </div>
    </aside>
  );
}
