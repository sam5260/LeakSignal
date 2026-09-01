export const dynamic = "force-dynamic";

import Link from "next/link";
import { ArrowUpRight } from "lucide-react";
import { DashboardShell } from "@/components/layout/DashboardShell";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { api } from "@/services/api";

export default async function AlertsListPage() {
  const alerts = await api.getAlerts();

  return (
    <DashboardShell title="Alerts" subtitle="All generated investigation alerts sorted by severity">
      {alerts.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-xl border border-base-600 bg-base-850 px-6 py-16 text-center">
          <p className="font-medium text-ink-100">No alerts generated yet</p>
          <p className="mt-1 max-w-sm text-sm text-ink-500">
            Upload a CSV dataset to begin detection analysis.
          </p>
          <Link
            href="/upload"
            className="mt-4 inline-flex items-center gap-1.5 text-sm font-medium text-signal hover:underline"
          >
            Upload dataset →
          </Link>
        </div>
      ) : (
        <div className="overflow-hidden rounded-xl border border-base-600 bg-base-850 shadow-panel">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-base-600 bg-base-800/60 text-[11px] uppercase tracking-wide text-ink-700">
                <th className="px-5 py-3 font-medium">Alert ID</th>
                <th className="px-5 py-3 font-medium">Host</th>
                <th className="px-5 py-3 font-medium">ERS</th>
                <th className="px-5 py-3 font-medium">Classification</th>
                <th className="px-5 py-3 font-medium">Summary</th>
                <th className="px-5 py-3 font-medium">Created</th>
                <th className="px-5 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-base-700">
              {alerts.map((alert) => (
                <tr
                  key={alert.id}
                  className="cursor-pointer transition-colors hover:bg-base-800/70"
                >
                  <td className="px-5 py-3.5">
                    <Link href={`/alerts/${alert.id}`} className="font-mono text-sm font-medium text-signal hover:underline">
                      {alert.id}
                    </Link>
                  </td>
                  <td className="px-5 py-3.5">
                    <Link href={`/hosts/${alert.hostId}`} className="font-mono text-sm text-ink-100 hover:text-signal hover:underline">
                      {alert.hostId}
                    </Link>
                  </td>
                  <td className="px-5 py-3.5">
                    <span className="font-mono text-sm font-semibold tabular text-ink-100">
                      {alert.ersScore}
                    </span>
                  </td>
                  <td className="px-5 py-3.5">
                    <StatusBadge classification={alert.classification} size="sm" />
                  </td>
                  <td className="max-w-xs truncate px-5 py-3.5 text-xs text-ink-500">
                    {alert.summary}
                  </td>
                  <td className="px-5 py-3.5 text-xs text-ink-500">{alert.createdAt}</td>
                  <td className="px-5 py-3.5 text-right">
                    <Link href={`/alerts/${alert.id}`}>
                      <ArrowUpRight className="ml-auto h-4 w-4 text-ink-700 hover:text-signal" />
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </DashboardShell>
  );
}
