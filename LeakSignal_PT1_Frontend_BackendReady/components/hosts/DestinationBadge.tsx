import { Globe, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";

export function DestinationBadge({
  destination,
  status,
}: {
  destination: string;
  status: "known" | "first-seen";
}) {
  const firstSeen = status === "first-seen";
  return (
    <div
      className={cn(
        "flex items-center justify-between rounded-lg border p-4",
        firstSeen
          ? "border-status-critical/30 bg-status-critical/5"
          : "border-base-600 bg-base-800/50"
      )}
    >
      <div className="flex items-center gap-3">
        <div
          className={cn(
            "flex h-9 w-9 items-center justify-center rounded-lg",
            firstSeen ? "bg-status-critical/15" : "bg-base-700"
          )}
        >
          {firstSeen ? (
            <Sparkles className="h-4.5 w-4.5 text-status-critical" />
          ) : (
            <Globe className="h-4.5 w-4.5 text-ink-500" />
          )}
        </div>
        <div>
          <p className="text-xs uppercase tracking-wide text-ink-700">Destination</p>
          <p className="font-mono text-sm text-ink-100">{destination}</p>
        </div>
      </div>
      <span
        className={cn(
          "rounded-full border px-2.5 py-1 font-mono text-[10px] font-semibold uppercase tracking-wide",
          firstSeen
            ? "border-status-critical/30 bg-status-critical/10 text-status-critical"
            : "border-status-normal/30 bg-status-normal/10 text-status-normal"
        )}
      >
        {firstSeen ? "First-Seen" : "Known"}
      </span>
    </div>
  );
}
