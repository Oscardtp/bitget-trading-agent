import { ReactNode } from "react";

interface CardProps {
  title: string;
  children: ReactNode;
  className?: string;
  accent?: boolean;
}

export function Card({ title, children, className = "", accent = false }: CardProps) {
  return (
    <div
      className={`bg-terminal-card border rounded-lg p-4 ${
        accent ? "border-terminal-accent/30 shadow-[0_0_20px_rgba(0,255,136,0.08)]" : "border-terminal-border"
      } ${className}`}
    >
      <h3 className="text-xs font-semibold text-terminal-muted uppercase tracking-wider mb-3">
        {title}
      </h3>
      {children}
    </div>
  );
}
