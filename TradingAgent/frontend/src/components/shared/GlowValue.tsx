interface GlowValueProps {
  value: string | number;
  label: string;
  color?: "accent" | "warning" | "danger" | "info";
  size?: "sm" | "md" | "lg";
}

const colorMap = {
  accent: "text-terminal-accent",
  warning: "text-terminal-warning",
  danger: "text-terminal-danger",
  info: "text-terminal-info",
};

const sizeMap = {
  sm: "text-lg",
  md: "text-2xl",
  lg: "text-3xl",
};

export function GlowValue({ value, label, color = "accent", size = "md" }: GlowValueProps) {
  return (
    <div className="text-center">
      <div className={`${sizeMap[size]} font-bold ${colorMap[color]} font-mono`}>
        {value}
      </div>
      <div className="text-xs text-terminal-muted mt-1">{label}</div>
    </div>
  );
}
