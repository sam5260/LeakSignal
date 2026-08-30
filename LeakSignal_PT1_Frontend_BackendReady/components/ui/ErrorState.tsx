import { AlertTriangle, Inbox } from "lucide-react";

export function ErrorState({
  title = "Connection to LeakSignal backend failed",
  message = "The dashboard could not reach the detection engine. Data shown may be stale or unavailable.",
}: {
  title?: string;
  message?: string;
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-xl border border-status-critical/25 bg-status-critical/5 px-6 py-12 text-center">
      <div className="flex h-10 w-10 items-center justify-center rounded-full bg-status-critical/10">
        <AlertTriangle className="h-5 w-5 text-status-critical" />
      </div>
      <p className="font-medium text-ink-100">{title}</p>
      <p className="max-w-sm text-sm text-ink-500">{message}</p>
    </div>
  );
}

export function EmptyState({
  title = "No data available",
  message = "Nothing to show yet for this view.",
}: {
  title?: string;
  message?: string;
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-xl border border-base-600 bg-base-850 px-6 py-12 text-center">
      <div className="flex h-10 w-10 items-center justify-center rounded-full bg-base-700">
        <Inbox className="h-5 w-5 text-ink-500" />
      </div>
      <p className="font-medium text-ink-100">{title}</p>
      <p className="max-w-sm text-sm text-ink-500">{message}</p>
    </div>
  );
}
