export function formatPrice(price: number | null): string {
  if (price === null) return "--";
  return price.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

export function formatPnl(pnl: number | null): string {
  if (pnl === null) return "--";
  const sign = pnl >= 0 ? "+" : "";
  return `${sign}${pnl.toFixed(2)}`;
}

export function formatPercent(pct: number | null): string {
  if (pct === null) return "--";
  return `${(pct * 100).toFixed(1)}%`;
}

export function formatTime(ts: string | null): string {
  if (!ts) return "--";
  const date = new Date(ts.includes("Z") || ts.includes("+") ? ts : ts + "Z");
  return date.toLocaleTimeString("en-US", { hour12: false, hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

export function formatDate(ts: string | null): string {
  if (!ts) return "--";
  return new Date(ts).toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

export function pnlColor(pnl: number | null): string {
  if (pnl === null) return "text-terminal-muted";
  if (pnl === 0) return "text-terminal-warning";
  return pnl > 0 ? "text-terminal-accent" : "text-terminal-danger";
}

export function scoreToLabel(
  score: number | null,
  type: "default" | "trend" | "sentiment" | "funding" | "oi" | "risk" = "default"
): string {
  if (score === null || score === undefined) return "N/A";

  if (type === "trend") {
    if (score > 0.6) return "Alcista";
    if (score < 0.4) return "Bajista";
    return "Lateral";
  }

  if (type === "sentiment") {
    if (score >= 0.7) return "Positivo";
    if (score >= 0.5) return "Neutral";
    return "Negativo";
  }

  if (type === "funding") {
    if (score > 0.0001) return "Positivo";
    if (score < -0.0001) return "Negativo";
    return "Neutral";
  }

  if (type === "oi") {
    if (score > 0.02) return "Incrementando";
    if (score < -0.02) return "Disminuyendo";
    return "Estable";
  }

  if (type === "risk") {
    if (score >= 0.8) return "Muy Alto";
    if (score >= 0.6) return "Alto";
    if (score >= 0.4) return "Medio";
    if (score >= 0.2) return "Bajo";
    return "Muy Bajo";
  }

  // Default: 0-1 score (higher = better)
  if (score >= 0.8) return "Excelente";
  if (score >= 0.6) return "Alto";
  if (score >= 0.4) return "Medio";
  if (score >= 0.2) return "Bajo";
  return "Muy Bajo";
}

export function scoreToBar(score: number | null, maxBars: number = 10): string {
  if (score === null || score === undefined) return "";
  const filled = Math.round(Math.max(0, Math.min(1, score)) * maxBars);
  return "\u2588".repeat(filled) + "\u2591".repeat(maxBars - filled);
}

export function scoreToColor(score: number | null): string {
  if (score === null || score === undefined) return "#6b7280";
  if (score >= 0.7) return "#22c55e";
  if (score >= 0.4) return "#eab308";
  return "#ef4444";
}
