"use client";

import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { ErsHistoryPoint } from "@/types";

export function ErsTimelineChart({ data }: { data: ErsHistoryPoint[] }) {
  return (
    <ResponsiveContainer width="100%" height={240}>
      <AreaChart data={data} margin={{ top: 8, right: 12, left: -12, bottom: 0 }}>
        <defs>
          <linearGradient id="ersFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#3E8EF7" stopOpacity={0.35} />
            <stop offset="100%" stopColor="#3E8EF7" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid vertical={false} stroke="#1A212C" />
        <XAxis
          dataKey="label"
          tickLine={false}
          axisLine={false}
          tick={{ fill: "#5B6474", fontSize: 11, fontFamily: "var(--font-mono)" }}
        />
        <YAxis
          domain={[0, 100]}
          tickLine={false}
          axisLine={false}
          tick={{ fill: "#5B6474", fontSize: 11 }}
          width={28}
        />
        <Tooltip
          contentStyle={{
            background: "#0F141C",
            border: "1px solid #232B38",
            borderRadius: 8,
            fontSize: 12,
            fontFamily: "var(--font-mono)",
          }}
          labelStyle={{ color: "#E9ECF2" }}
        />
        <Area
          type="monotone"
          dataKey="ers"
          stroke="#3E8EF7"
          strokeWidth={2}
          fill="url(#ersFill)"
          dot={{ r: 3, fill: "#3E8EF7", strokeWidth: 0 }}
          activeDot={{ r: 5 }}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
