import type { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

export function MetricCard({
  label,
  value,
  delta,
  icon: Icon,
  tone = "default",
}: {
  label: string;
  value: number | string;
  delta?: string;
  icon: LucideIcon;
  tone?: "default" | "critical" | "suspicious";
}) {
  const toneMap = {
    default: { icon: "text-signal", ring: "bg-signal/10" },
    critical: { icon: "text-status-critical", ring: "bg-status-critical/10" },
    suspicious: { icon: "text-status-suspicious", ring: "bg-status-suspicious/10" },
  } as const;
  const t = toneMap[tone];

  return (
    <div className="rounded-xl border border-base-600 bg-base-850 p-5 shadow-panel">
      <div className="flex items-start justify-between">
        <p className="text-xs font-medium uppercase tracking-wide text-ink-500">{label}</p>
        <div className={cn("flex h-8 w-8 items-center justify-center rounded-lg", t.ring)}>
          <Icon className={cn("h-4 w-4", t.icon)} strokeWidth={2.25} />
        </div>
      </div>
      <p className="mt-4 font-mono text-3xl font-semibold tabular text-ink-100">{value}</p>
      {delta ? <p className="mt-2 text-xs text-ink-500">{delta}</p> : null}
    </div>
  );
}
