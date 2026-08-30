"use client";

import { CLASSIFICATION_META } from "@/lib/utils";
import type { RiskClassification } from "@/types";

const THRESHOLDS = [
  { from: 0, to: 25, classification: "normal" as const },
  { from: 26, to: 50, classification: "monitor" as const },
  { from: 51, to: 75, classification: "suspicious" as const },
  { from: 76, to: 100, classification: "exfiltration" as const },
];

const START_ANGLE = -220;
const END_ANGLE = 40;
const SWEEP = END_ANGLE - START_ANGLE; // 260 degrees

function polar(cx: number, cy: number, r: number, angleDeg: number) {
  const rad = (angleDeg * Math.PI) / 180;
  return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
}

function arcPath(cx: number, cy: number, r: number, a0: number, a1: number) {
  const start = polar(cx, cy, r, a0);
  const end = polar(cx, cy, r, a1);
  const largeArc = a1 - a0 > 180 ? 1 : 0;
  return `M ${start.x} ${start.y} A ${r} ${r} 0 ${largeArc} 1 ${end.x} ${end.y}`;
}

const COLOR_HEX: Record<string, string> = {
  normal: "#2FD3A0",
  monitor: "#F0B429",
  suspicious: "#F2803F",
  exfiltration: "#F0466C",
};

export function ERSGauge({ score, classification }: { score: number; classification: RiskClassification }) {
  const meta = CLASSIFICATION_META[classification];
  const cx = 130;
  const cy = 130;
  const r = 100;
  const needleAngle = START_ANGLE + (score / 100) * SWEEP;

  return (
    <div className="flex flex-col items-center">
      <svg viewBox="0 0 260 190" className="w-full max-w-[260px]">
        {/* threshold track segments */}
        {THRESHOLDS.map((t) => {
          const a0 = START_ANGLE + (t.from / 100) * SWEEP;
          const a1 = START_ANGLE + (t.to / 100) * SWEEP;
          return (
            <path
              key={t.classification}
              d={arcPath(cx, cy, r, a0, a1)}
              fill="none"
              stroke={COLOR_HEX[t.classification]}
              strokeOpacity={t.classification === classification ? 0.95 : 0.22}
              strokeWidth={14}
              strokeLinecap="butt"
            />
          );
        })}

        {/* tick marks at threshold boundaries */}
        {[0, 25, 50, 75, 100].map((v) => {
          const a = START_ANGLE + (v / 100) * SWEEP;
          const inner = polar(cx, cy, r - 12, a);
          const outer = polar(cx, cy, r + 8, a);
          return (
            <line
              key={v}
              x1={inner.x}
              y1={inner.y}
              x2={outer.x}
              y2={outer.y}
              stroke="#5B6474"
              strokeWidth={1.5}
            />
          );
        })}

        {/* needle */}
        <line
          x1={cx}
          y1={cy}
          x2={polar(cx, cy, r - 22, needleAngle).x}
          y2={polar(cx, cy, r - 22, needleAngle).y}
          stroke="#E9ECF2"
          strokeWidth={2.5}
          strokeLinecap="round"
        />
        <circle cx={cx} cy={cy} r={5} fill="#E9ECF2" />

        {/* score readout */}
        <text
          x={cx}
          y={cy - 30}
          textAnchor="middle"
          className="tabular"
          fill="#E9ECF2"
          fontFamily="var(--font-mono)"
          fontSize={40}
          fontWeight={600}
        >
          {score}
        </text>
        <text
          x={cx}
          y={cy - 10}
          textAnchor="middle"
          fill="#5B6474"
          fontFamily="var(--font-mono)"
          fontSize={10}
          letterSpacing={2}
        >
          ERS / 100
        </text>
      </svg>

      <div className="mt-1 flex items-center gap-2 rounded-full border px-3 py-1"
        style={{ borderColor: `${COLOR_HEX[classification]}4D`, backgroundColor: `${COLOR_HEX[classification]}1A` }}
      >
        <span className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: COLOR_HEX[classification] }} />
        <span className={`font-mono text-xs font-semibold uppercase tracking-wide ${meta.color}`}>
          {meta.label}
        </span>
      </div>

      <div className="mt-4 grid w-full grid-cols-4 gap-1 text-center text-[10px] text-ink-700">
        <span>0–25</span>
        <span>26–50</span>
        <span>51–75</span>
        <span>76–100</span>
      </div>
    </div>
  );
}
