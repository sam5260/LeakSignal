export const dynamic = "force-dynamic";

import { Moon } from "lucide-react";
import { DashboardShell } from "@/components/layout/DashboardShell";
import { ERSGauge } from "@/components/hosts/ERSGauge";
import { OutboundComparison } from "@/components/hosts/OutboundComparison";
import { DestinationBadge } from "@/components/hosts/DestinationBadge";
import { ActivityTimeline } from "@/components/hosts/ActivityTimeline";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { api } from "@/services/api";

export default async function HostInvestigationPage({ params }: { params: any }) {
  const { id } = await params;
  const hostId = decodeURIComponent(id);

  // Fetch both profile and timeline in parallel
  const [host, timeline] = await Promise.all([
    api.getHostProfile(hostId),
    api.getHostTimeline(hostId),
  ]);

  return (
    <DashboardShell title="Host Investigation" subtitle={`Behavioral profile and evidence for ${host.id}`}>
      <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-base-600 bg-base-850 p-5 shadow-panel">
        <div>
          <p className="font-mono text-2xl font-semibold text-ink-100">{host.id}</p>
          <p className="mt-1 text-sm text-ink-500">{host.classificationLabel}</p>
          <p className="mt-1 text-xs text-ink-700">{host.department} · Last seen {host.lastSeen}</p>
        </div>
        <StatusBadge classification={host.classification} />
      </div>

      <div className="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-3">
        <div className="rounded-xl border border-base-600 bg-base-850 p-5 shadow-panel lg:col-span-1">
          <h3 className="text-sm font-semibold text-ink-100">Exfiltration Risk Score</h3>
          <div className="mt-4 flex justify-center">
            <ERSGauge score={host.ersScore} classification={host.classification} />
          </div>
        </div>

        <div className="lg:col-span-2">
          <OutboundComparison
            data={host.outboundComparison}
            baselineMB={host.baselineOutboundMB}
            currentMB={host.currentOutboundMB}
            deviationPct={host.deviationPct}
          />
        </div>
      </div>

      <div className="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <DestinationBadge destination={host.destination} status={host.destinationStatus} />
        </div>
        <div className="flex items-center justify-between rounded-lg border border-base-600 bg-base-800/50 p-4">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-base-700">
              <Moon className="h-4.5 w-4.5 text-ink-500" />
            </div>
            <div>
              <p className="text-xs uppercase tracking-wide text-ink-700">Off-Hours Sessions</p>
              <p className="font-mono text-sm text-ink-100">Night-time activity count</p>
            </div>
          </div>
          <span className="font-mono text-2xl font-semibold tabular text-ink-100">
            {host.repeatedOffHoursSessions}
          </span>
        </div>
      </div>

      <div className="mt-4">
        <ActivityTimeline days={timeline.length > 0 ? timeline : host.timeline} />
      </div>
    </DashboardShell>
  );
}
