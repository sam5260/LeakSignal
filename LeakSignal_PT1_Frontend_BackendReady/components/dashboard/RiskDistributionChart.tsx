"use client";

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis, Cell } from "recharts";
import type { RiskDistributionPoint } from "@/types";
import { CLASSIFICATION_META } from "@/lib/utils";

const COLOR_HEX: Record<string, string> = {
  normal: "#2FD3A0",
  monitor: "#F0B429",
  suspicious: "#F2803F",
  exfiltration: "#F0466C",
};

export function RiskDistributionChart({ data }: { data: RiskDistributionPoint[] }) {
  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={data} margin={{ top: 8, right: 8, left: -12, bottom: 0 }} barCategoryGap={28}>
        <CartesianGrid vertical={false} stroke="#1A212C" />
        <XAxis
          dataKey="label"
          tickLine={false}
          axisLine={false}
          tick={{ fill: "#8A93A3", fontSize: 12, fontFamily: "var(--font-mono)" }}
        />
        <YAxis tickLine={false} axisLine={false} tick={{ fill: "#5B6474", fontSize: 11 }} width={28} />
        <Tooltip
          cursor={{ fill: "rgba(255,255,255,0.03)" }}
          contentStyle={{
            background: "#0F141C",
            border: "1px solid #232B38",
            borderRadius: 8,
            fontSize: 12,
            fontFamily: "var(--font-mono)",
          }}
          labelStyle={{ color: "#E9ECF2" }}
        />
        <Bar dataKey="count" radius={[6, 6, 0, 0]} maxBarSize={56}>
          {data.map((entry) => (
            <Cell key={entry.classification} fill={COLOR_HEX[entry.classification]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

export function RiskDistributionLegend({ data }: { data: RiskDistributionPoint[] }) {
  return (
    <div className="flex flex-wrap gap-4 pt-1">
      {data.map((d) => {
        const meta = CLASSIFICATION_META[d.classification];
        return (
          <div key={d.classification} className="flex items-center gap-1.5 text-xs text-ink-500">
            <span className={`h-2 w-2 rounded-full ${meta.dot}`} />
            {meta.label}
            <span className="font-mono text-ink-300">{d.count}</span>
          </div>
        );
      })}
    </div>
  );
}
