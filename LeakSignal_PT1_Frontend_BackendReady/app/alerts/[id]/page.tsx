export const dynamic = "force-dynamic";

import Link from "next/link";
import { ArrowUpRight } from "lucide-react";
import { DashboardShell } from "@/components/layout/DashboardShell";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { SignalList } from "@/components/alerts/SignalList";
import { FalsePositiveCard } from "@/components/alerts/FalsePositiveCard";
import { api } from "@/services/api";

export default async function AlertEvidencePage({ params }: { params: any }) {
  const { id } = await params;
  const alert = await api.getAlertEvidence(decodeURIComponent(id));

  return (
    <DashboardShell title="Alert Evidence" subtitle={`Explainability report for ${alert.id}`}>
      <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-base-600 bg-base-850 p-5 shadow-panel">
        <div>
          <p className="font-mono text-lg font-semibold text-ink-100">{alert.id}</p>
          <p className="mt-1 text-sm text-ink-500">{alert.classificationLabel}</p>
          <p className="mt-1 text-xs text-ink-700">{alert.createdAt}</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-right">
            <p className="text-[11px] uppercase tracking-wide text-ink-700">ERS Score</p>
            <p className="font-mono text-2xl font-semibold tabular text-ink-100">{alert.ersScore}</p>
          </div>
          <StatusBadge classification={alert.classification} />
        </div>
      </div>

      <Link
        href={`/hosts/${alert.hostId}`}
        className="mt-3 inline-flex items-center gap-1.5 text-xs font-medium text-signal hover:underline"
      >
        View host investigation — {alert.hostId}
        <ArrowUpRight className="h-3.5 w-3.5" />
      </Link>

      <div className="mt-6 grid grid-cols-1 gap-6 xl:grid-cols-5">
        <div className="xl:col-span-3">
          <h3 className="mb-3 text-sm font-semibold text-ink-100">Why LeakSignal Flagged This</h3>
          <SignalList signals={alert.signals} />
        </div>
        <div className="xl:col-span-2">
          <h3 className="mb-3 text-sm font-semibold text-ink-100">Validation</h3>
          <FalsePositiveCard check={alert.falsePositiveCheck} />
        </div>
      </div>
    </DashboardShell>
  );
}
