import { CLASSIFICATION_META } from "@/lib/utils";
import type { RiskClassification } from "@/types";
import { cn } from "@/lib/utils";

export function StatusBadge({
  classification,
  size = "md",
}: {
  classification: RiskClassification;
  size?: "sm" | "md";
}) {
  const meta = CLASSIFICATION_META[classification];
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border font-mono font-medium uppercase tracking-wide",
        meta.bg,
        meta.border,
        meta.color,
        size === "sm" ? "px-2 py-0.5 text-[10px]" : "px-2.5 py-1 text-xs"
      )}
    >
      <span className={cn("h-1.5 w-1.5 rounded-full", meta.dot)} />
      {meta.label}
    </span>
  );
}
