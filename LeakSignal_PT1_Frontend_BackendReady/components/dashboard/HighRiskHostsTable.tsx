"use client";

import { useRouter } from "next/navigation";
import { ChevronRight } from "lucide-react";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { CLASSIFICATION_META } from "@/lib/utils";
import type { HostSummary } from "@/types";
import { EmptyState } from "@/components/ui/ErrorState";

export function HighRiskHostsTable({ hosts }: { hosts: HostSummary[] }) {
  const router = useRouter();

  if (hosts.length === 0) {
    return <EmptyState title="No hosts to display" message="No host telemetry has been ingested yet." />;
  }

  return (
    <div className="overflow-hidden rounded-xl border border-base-600 bg-base-850 shadow-panel">
      <table className="w-full text-left text-sm">
        <thead>
          <tr className="border-b border-base-600 bg-base-800/60 text-[11px] uppercase tracking-wide text-ink-700">
            <th className="px-5 py-3 font-medium">Host ID</th>
            <th className="px-5 py-3 font-medium">ERS Score</th>
            <th className="px-5 py-3 font-medium">Classification</th>
            <th className="px-5 py-3 font-medium">Last Seen</th>
            <th className="px-5 py-3" />
          </tr>
        </thead>
        <tbody className="divide-y divide-base-700">
          {hosts.map((host) => {
            const meta = CLASSIFICATION_META[host.classification];
            return (
              <tr
                key={host.id}
                onClick={() => router.push(`/hosts/${host.id}`)}
                className="cursor-pointer transition-colors hover:bg-base-800/70"
              >
                <td className="px-5 py-3.5">
                  <p className="font-mono text-sm font-medium text-ink-100">{host.id}</p>
                  {host.department ? <p className="text-xs text-ink-700">{host.department}</p> : null}
                </td>
                <td className="px-5 py-3.5">
                  <div className="flex items-center gap-2">
                    <span className={`font-mono text-sm font-semibold tabular ${meta.color}`}>
                      {host.ersScore}
                    </span>
                    <div className="h-1.5 w-16 overflow-hidden rounded-full bg-base-700">
                      <div
                        className={`h-full rounded-full ${meta.dot}`}
                        style={{ width: `${host.ersScore}%` }}
                      />
                    </div>
                  </div>
                </td>
                <td className="px-5 py-3.5">
                  <StatusBadge classification={host.classification} size="sm" />
                </td>
                <td className="px-5 py-3.5 text-xs text-ink-500">{host.lastSeen}</td>
                <td className="px-5 py-3.5 text-right">
                  <ChevronRight className="ml-auto h-4 w-4 text-ink-700" />
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
