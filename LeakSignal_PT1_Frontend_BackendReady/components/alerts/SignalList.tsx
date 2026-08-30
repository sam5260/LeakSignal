import { Globe, Clock, Repeat, CalendarClock, type LucideIcon } from "lucide-react";
import { SEVERITY_META } from "@/lib/utils";
import type { AlertSignal } from "@/types";

const ICON_MAP: Record<AlertSignal["icon"], LucideIcon> = {
  destination: Globe,
  clock: Clock,
  repeat: Repeat,
  calendar: CalendarClock,
};

export function SignalList({ signals }: { signals: AlertSignal[] }) {
  return (
    <div className="space-y-3">
      {signals.map((signal) => {
        const Icon = ICON_MAP[signal.icon];
        const sev = SEVERITY_META[signal.severity];
        return (
          <div
            key={signal.id}
            className="flex items-start gap-4 rounded-xl border border-base-600 bg-base-850 p-4 shadow-panel"
          >
            <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-lg ${sev.bg}`}>
              <Icon className={`h-5 w-5 ${sev.color}`} strokeWidth={2} />
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <h4 className="text-sm font-semibold text-ink-100">{signal.title}</h4>
                <span
                  className={`rounded-full px-2 py-0.5 font-mono text-[10px] font-semibold uppercase tracking-wide ${sev.bg} ${sev.color}`}
                >
                  {sev.label}
                </span>
              </div>
              <p className="mt-1 text-sm leading-relaxed text-ink-500">{signal.description}</p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
