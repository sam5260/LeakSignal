export const dynamic = "force-dynamic";

import { Activity, ShieldAlert, MonitorSmartphone, TriangleAlert } from "lucide-react";
import { DashboardShell } from "@/components/layout/DashboardShell";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { HighRiskHostsTable } from "@/components/dashboard/HighRiskHostsTable";
import { RiskDistributionChart, RiskDistributionLegend } from "@/components/dashboard/RiskDistributionChart";
import { ErsTimelineChart } from "@/components/dashboard/ErsTimelineChart";
import { api } from "@/services/api";

export default async function OverviewPage() {
  const [summary, hosts, distribution, ersActivity] = await Promise.all([
    api.getDashboardSummary(),
    api.getHosts(),
    api.getRiskDistribution(),
    api.getErsActivity(),
  ]);

  return (
    <DashboardShell title="Overview Dashboard" subtitle="Real-time exfiltration risk posture across monitored hosts">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Monitored Hosts" value={summary.monitoredHosts} delta={summary.monitoredHostsDelta} icon={MonitorSmartphone} />
        <MetricCard label="Critical Risk Hosts" value={summary.criticalHosts} delta={summary.criticalHostsDelta} icon={TriangleAlert} tone="critical" />
        <MetricCard label="Suspicious Hosts" value={summary.suspiciousHosts} delta={summary.suspiciousHostsDelta} icon={ShieldAlert} tone="suspicious" />
        <MetricCard label="Alerts Today" value={summary.alertsToday} delta={summary.alertsTodayDelta} icon={Activity} />
      </div>

      <div className="mt-6 grid grid-cols-1 gap-4 xl:grid-cols-5">
        <div className="rounded-xl border border-base-600 bg-base-850 p-5 shadow-panel xl:col-span-2">
          <h3 className="text-sm font-semibold text-ink-100">Host Risk Distribution</h3>
          <p className="mt-1 text-xs text-ink-500">Current classification across all monitored hosts</p>
          <RiskDistributionChart data={distribution} />
          <RiskDistributionLegend data={distribution} />
        </div>

        <div className="rounded-xl border border-base-600 bg-base-850 p-5 shadow-panel xl:col-span-3">
          <h3 className="text-sm font-semibold text-ink-100">ERS Progression — FIN-PC-07</h3>
          <p className="mt-1 text-xs text-ink-500">
            Exfiltration Risk Score climbing over repeated low-volume nightly activity
          </p>
          <ErsTimelineChart data={ersActivity} />
        </div>
      </div>

      <div className="mt-6">
        <div className="mb-3 flex items-center justify-between">
          <h3 className="text-sm font-semibold text-ink-100">High-Risk Hosts</h3>
          <span className="text-xs text-ink-700">Click a row to open the investigation view</span>
        </div>
        <HighRiskHostsTable hosts={hosts} />
      </div>
    </DashboardShell>
  );
}
