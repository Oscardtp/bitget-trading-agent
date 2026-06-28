interface BadgeProps {
  status: "WIN" | "LOSS" | "ACTIVE" | "PENDING" | "CLOSED" | "HOLD";
}

const statusStyles: Record<string, string> = {
  WIN: "bg-terminal-accent/20 text-terminal-accent",
  LOSS: "bg-terminal-danger/20 text-terminal-danger",
  ACTIVE: "bg-terminal-info/20 text-terminal-info",
  PENDING: "bg-terminal-warning/20 text-terminal-warning",
  CLOSED: "bg-terminal-muted/20 text-terminal-muted",
  HOLD: "bg-terminal-info/20 text-terminal-info",
};

export function Badge({ status }: BadgeProps) {
  return (
    <span className={`px-2 py-0.5 rounded text-xs font-semibold ${statusStyles[status] || statusStyles.CLOSED}`}>
      {status}
    </span>
  );
}
