"use client";

import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { ArrowUpRight, ArrowDownRight } from "lucide-react";
import type { OutboundComparisonPoint } from "@/types";
import { formatMB, formatPct } from "@/lib/utils";

export function OutboundComparison({
  data,
  baselineMB,
  currentMB,
  deviationPct,
}: {
  data: OutboundComparisonPoint[];
  baselineMB: number;
  currentMB: number;
  deviationPct: number;
}) {
  const isUp = deviationPct >= 0;

  return (
    <div className="rounded-xl border border-base-600 bg-base-850 p-5 shadow-panel">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-ink-100">Normal vs Current Outbound Activity</h3>
      </div>

      <div className="mt-4 grid grid-cols-3 gap-3">
        <StatBlock label="Baseline daily" value={formatMB(baselineMB)} />
        <StatBlock label="Current" value={formatMB(currentMB)} accent />
        <div className="rounded-lg border border-base-600 bg-base-800/50 p-3">
          <p className="text-[11px] uppercase tracking-wide text-ink-700">Deviation</p>
          <div
            className={`mt-1.5 flex items-center gap-1 font-mono text-lg font-semibold tabular ${
              isUp ? "text-status-critical" : "text-status-normal"
            }`}
          >
            {isUp ? <ArrowUpRight className="h-4 w-4" /> : <ArrowDownRight className="h-4 w-4" />}
            {formatPct(deviationPct)}
          </div>
        </div>
      </div>

      <div className="mt-5">
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={data} margin={{ top: 4, right: 8, left: -16, bottom: 0 }} barGap={4}>
            <CartesianGrid vertical={false} stroke="#1A212C" />
            <XAxis
              dataKey="label"
              tickLine={false}
              axisLine={false}
              tick={{ fill: "#5B6474", fontSize: 11, fontFamily: "var(--font-mono)" }}
            />
            <YAxis tickLine={false} axisLine={false} tick={{ fill: "#5B6474", fontSize: 11 }} width={32} />
            <Tooltip
              contentStyle={{
                background: "#0F141C",
                border: "1px solid #232B38",
                borderRadius: 8,
                fontSize: 12,
              }}
              labelStyle={{ color: "#E9ECF2" }}
            />
            <Legend wrapperStyle={{ fontSize: 11, color: "#8A93A3" }} />
            <Bar dataKey="baselineMB" name="Baseline (MB)" fill="#3E8EF7" fillOpacity={0.35} radius={[4, 4, 0, 0]} maxBarSize={28} />
            <Bar dataKey="currentMB" name="Current (MB)" fill="#F0466C" radius={[4, 4, 0, 0]} maxBarSize={28} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

function StatBlock({ label, value, accent }: { label: string; value: string; accent?: boolean }) {
  return (
    <div className="rounded-lg border border-base-600 bg-base-800/50 p-3">
      <p className="text-[11px] uppercase tracking-wide text-ink-700">{label}</p>
      <p className={`mt-1.5 font-mono text-lg font-semibold tabular ${accent ? "text-ink-100" : "text-ink-300"}`}>
        {value}
      </p>
    </div>
  );
}
