import { cn } from "@/lib/utils";

export function Skeleton({ className }: { className?: string }) {
  return <div className={cn("animate-pulse rounded-md bg-base-700/70", className)} />;
}

export function SkeletonCard() {
  return (
    <div className="rounded-xl border border-base-600 bg-base-850 p-5 shadow-panel">
      <Skeleton className="h-3 w-24" />
      <Skeleton className="mt-4 h-8 w-16" />
      <Skeleton className="mt-3 h-3 w-32" />
    </div>
  );
}

export function SkeletonTable({ rows = 5 }: { rows?: number }) {
  return (
    <div className="space-y-2">
      {Array.from({ length: rows }).map((_, i) => (
        <Skeleton key={i} className="h-11 w-full" />
      ))}
    </div>
  );
}

export function SkeletonChart() {
  return <Skeleton className="h-64 w-full" />;
}
