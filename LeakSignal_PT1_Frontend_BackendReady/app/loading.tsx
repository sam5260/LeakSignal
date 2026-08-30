import { DashboardShell } from "@/components/layout/DashboardShell";
import { SkeletonCard, SkeletonChart, SkeletonTable } from "@/components/ui/Skeleton";

export default function Loading() {
  return (
    <DashboardShell title="LeakSignal" subtitle="Loading detection data…">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <SkeletonCard key={i} />
        ))}
      </div>
      <div className="mt-6 grid grid-cols-1 gap-4 xl:grid-cols-2">
        <SkeletonChart />
        <SkeletonChart />
      </div>
      <div className="mt-6">
        <SkeletonTable />
      </div>
    </DashboardShell>
  );
}
