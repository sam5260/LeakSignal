import { CheckCircle2, XCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import type { AlertEvidence } from "@/types";

export function FalsePositiveCard({ check }: { check: AlertEvidence["falsePositiveCheck"] }) {
  const cleared = check.result === "cleared";
  return (
    <div
      className={cn(
        "rounded-xl border p-5 shadow-panel",
        cleared ? "border-status-normal/25 bg-status-normal/5" : "border-status-critical/25 bg-status-critical/5"
      )}
    >
      <div className="flex items-start gap-3">
        <div
          className={cn(
            "flex h-9 w-9 shrink-0 items-center justify-center rounded-lg",
            cleared ? "bg-status-normal/15" : "bg-status-critical/15"
          )}
        >
          {cleared ? (
            <CheckCircle2 className="h-5 w-5 text-status-normal" />
          ) : (
            <XCircle className="h-5 w-5 text-status-critical" />
          )}
        </div>
        <div>
          <p className="text-xs uppercase tracking-wide text-ink-700">False-Positive Check</p>
          <p className={cn("mt-0.5 font-mono text-sm font-semibold", cleared ? "text-status-normal" : "text-status-critical")}>
            {check.label}
          </p>
          <p className="mt-2 text-sm leading-relaxed text-ink-500">{check.reasoning}</p>
        </div>
      </div>
    </div>
  );
}
