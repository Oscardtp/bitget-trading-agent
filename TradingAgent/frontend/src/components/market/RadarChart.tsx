"use client";

interface RadarAxis {
  label: string;
  value: number; // 0-1
}

interface RadarChartProps {
  axes: RadarAxis[];
  size?: number;
}

export function RadarChart({ axes, size = 200 }: RadarChartProps) {
  const center = size / 2;
  const maxRadius = (size / 2) - 30;
  const levels = 5;
  const angleStep = (2 * Math.PI) / axes.length;

  const getPoint = (index: number, value: number) => {
    const angle = angleStep * index - Math.PI / 2;
    const r = value * maxRadius;
    return {
      x: center + r * Math.cos(angle),
      y: center + r * Math.sin(angle),
    };
  };

  // Build polygon points for data
  const dataPoints = axes.map((axis, i) => getPoint(i, axis.value));
  const dataPath = dataPoints.map((p, i) => `${i === 0 ? "M" : "L"} ${p.x} ${p.y}`).join(" ") + " Z";

  return (
    <div className="flex flex-col items-center">
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        {/* Background circles */}
        {Array.from({ length: levels }).map((_, i) => {
          const r = ((i + 1) / levels) * maxRadius;
          return (
            <circle
              key={i}
              cx={center}
              cy={center}
              r={r}
              fill="none"
              stroke="#1a2332"
              strokeWidth="1"
            />
          );
        })}

        {/* Axis lines */}
        {axes.map((_, i) => {
          const end = getPoint(i, 1);
          return (
            <line
              key={i}
              x1={center}
              y1={center}
              x2={end.x}
              y2={end.y}
              stroke="#1a2332"
              strokeWidth="1"
            />
          );
        })}

        {/* Data polygon */}
        <path
          d={dataPath}
          fill="rgba(34, 197, 94, 0.15)"
          stroke="#22c55e"
          strokeWidth="2"
        />

        {/* Data points */}
        {dataPoints.map((p, i) => (
          <circle
            key={i}
            cx={p.x}
            cy={p.y}
            r="3"
            fill="#22c55e"
          />
        ))}

        {/* Labels */}
        {axes.map((axis, i) => {
          const labelPoint = getPoint(i, 1.18);
          const anchor = labelPoint.x < center - 5 ? "end" : labelPoint.x > center + 5 ? "start" : "middle";
          return (
            <text
              key={i}
              x={labelPoint.x}
              y={labelPoint.y}
              textAnchor={anchor}
              dominantBaseline="middle"
              className="fill-terminal-muted text-[9px] font-mono"
            >
              {axis.label}
            </text>
          );
        })}
      </svg>
    </div>
  );
}
