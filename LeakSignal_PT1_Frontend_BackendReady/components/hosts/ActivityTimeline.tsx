import { CLASSIFICATION_META } from "@/lib/utils";
import type { TimelineDay } from "@/types";

export function ActivityTimeline({ days }: { days: TimelineDay[] }) {
  return (
    <div className="rounded-xl border border-base-600 bg-base-850 p-5 shadow-panel">
      <h3 className="text-sm font-semibold text-ink-100">Activity Timeline</h3>
      <p className="mt-1 text-xs text-ink-500">
        How the host&apos;s risk developed gradually across observed sessions.
      </p>

      <ol className="mt-5 space-y-0">
        {days.map((d, i) => {
          const meta = CLASSIFICATION_META[d.classification];
          const isLast = i === days.length - 1;
          return (
            <li key={d.day} className="relative flex gap-4 pb-6 last:pb-0">
              {!isLast && (
                <span className="absolute left-[15px] top-8 h-[calc(100%-1.5rem)] w-px bg-base-600" />
              )}
              <div
                className={`z-10 flex h-8 w-8 shrink-0 items-center justify-center rounded-full border-2 ${meta.border} ${meta.bg}`}
              >
                <span className={`h-2 w-2 rounded-full ${meta.dot}`} />
              </div>
              <div className="flex-1 pt-0.5">
                <div className="flex flex-wrap items-center gap-2">
                  <p className="font-mono text-sm font-medium text-ink-100">
                    {d.day} <span className="text-ink-700">· {d.date}</span>
                  </p>
                  <span className={`rounded-full border px-2 py-0.5 font-mono text-[10px] font-semibold uppercase ${meta.border} ${meta.bg} ${meta.color}`}>
                    {meta.label}
                  </span>
                  <span className="ml-auto font-mono text-xs tabular text-ink-500">ERS {d.ers}</span>
                </div>
                {d.note ? <p className="mt-1 text-xs text-ink-500">{d.note}</p> : null}
              </div>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
