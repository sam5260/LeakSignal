import type {
  AlertEvidence,
  AlertListItem,
  DashboardSummary,
  ErsHistoryPoint,
  HostProfile,
  HostSummary,
  RiskClassification,
  RiskDistributionPoint,
  TimelineDay,
} from "@/types";
import {
  getMockAlertEvidence,
  getMockHostProfile,
  mockAlertsList,
  mockDashboardSummary,
  mockErsActivity,
  mockHighRiskHosts,
  mockRiskDistribution,
} from "@/lib/mockData";

const BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";
const USE_MOCK_FALLBACK =
  process.env.NEXT_PUBLIC_USE_MOCKS === "true";

class ApiError extends Error {
  status?: number;

  constructor(message: string, status?: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  if (!BASE_URL) {
    throw new ApiError(
      "LeakSignal API URL is not configured. Set NEXT_PUBLIC_API_BASE_URL in .env.local."
    );
  }

  const isFormData =
    typeof FormData !== "undefined" && init?.body instanceof FormData;
  const headers = new Headers(init?.headers);

  if (!isFormData && init?.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const res = await fetch(`${BASE_URL}${path}`, {
    ...init,
    headers,
    cache: "no-store",
  });

  if (!res.ok) {
    let detail = "";
    try {
      const body = await res.json();
      detail = body?.detail ? `: ${String(body.detail)}` : "";
    } catch {
      // Response body optional for errors
    }
    throw new ApiError(`Request to ${path} failed${detail}`, res.status);
  }

  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

async function withFallback<T>(fn: () => Promise<T>, fallback: T): Promise<T> {
  try {
    return await fn();
  } catch (error) {
    if (USE_MOCK_FALLBACK) return fallback;
    throw error instanceof ApiError ? error : new ApiError("Backend unavailable");
  }
}

function value<T = unknown>(obj: any, ...keys: string[]): T | undefined {
  for (const key of keys) {
    if (obj && obj[key] !== undefined && obj[key] !== null) return obj[key] as T;
  }
  return undefined;
}

function numberValue(obj: any, keys: string[], fallback = 0): number {
  const raw = value<any>(obj, ...keys);
  const n = Number(raw);
  return Number.isFinite(n) ? n : fallback;
}

function stringValue(obj: any, keys: string[], fallback = ""): string {
  const raw = value<any>(obj, ...keys);
  return raw === undefined || raw === null ? fallback : String(raw);
}

function normalizeClassification(input: unknown): RiskClassification {
  const raw = String(input ?? "").trim().toLowerCase();

  if (raw === "normal" || raw === "low") return "normal";
  if (raw === "monitor" || raw === "medium") return "monitor";
  if (raw === "suspicious" || raw === "high") return "suspicious";
  if (
    raw === "exfiltration" ||
    raw === "critical" ||
    raw.includes("possible slow data exfiltration") ||
    raw.includes("slow data exfiltration")
  ) {
    return "exfiltration";
  }

  return "normal";
}

function classificationLabel(classification: RiskClassification): string {
  switch (classification) {
    case "exfiltration":
      return "Possible Slow Data Exfiltration";
    case "suspicious":
      return "Suspicious";
    case "monitor":
      return "Monitor";
    default:
      return "Normal";
  }
}

function normalizeDashboard(raw: any): DashboardSummary {
  return {
    monitoredHosts: numberValue(raw, ["monitoredHosts", "monitored_hosts"]),
    criticalHosts: numberValue(raw, ["criticalHosts", "critical_hosts"]),
    suspiciousHosts: numberValue(raw, ["suspiciousHosts", "suspicious_hosts"]),
    alertsToday: numberValue(raw, ["alertsToday", "alerts_today"]),
    monitoredHostsDelta: value(raw, "monitoredHostsDelta", "monitored_hosts_delta"),
    criticalHostsDelta: value(raw, "criticalHostsDelta", "critical_hosts_delta"),
    suspiciousHostsDelta: value(raw, "suspiciousHostsDelta", "suspicious_hosts_delta"),
    alertsTodayDelta: value(raw, "alertsTodayDelta", "alerts_today_delta"),
  };
}

function normalizeHostSummary(raw: any): HostSummary {
  const classification = normalizeClassification(
    value(raw, "classification", "status", "severity")
  );
  return {
    id: stringValue(raw, ["id", "host_id", "hostId"]),
    ersScore: numberValue(raw, ["ersScore", "ers_score", "ers", "risk_score"]),
    classification,
    lastSeen: stringValue(raw, ["lastSeen", "last_seen"], "—"),
    department: value(raw, "department"),
  };
}

function normalizeTimeline(raw: any): TimelineDay[] {
  const list = Array.isArray(raw) ? raw : value<any[]>(raw, "timeline", "data") || [];
  return list.map((point: any, index: number) => {
    const ers = numberValue(point, ["ers", "ers_score", "risk_score"]);
    const classification = normalizeClassification(
      value(point, "classification", "status")
    );
    return {
      day: stringValue(point, ["day", "label"], `Day ${index + 1}`),
      date: stringValue(point, ["date", "timestamp"], stringValue(point, ["day", "label"], `Day ${index + 1}`)),
      classification,
      ers,
      note: value(point, "note", "reason", "summary"),
    };
  });
}

function normalizeHostProfile(raw: any): HostProfile {
  const classification = normalizeClassification(
    value(raw, "classification", "status", "severity")
  );
  const baseline = numberValue(raw, ["baselineOutboundMB", "baseline_outbound_mb", "normal_outbound_mb"]);
  const current = numberValue(raw, ["currentOutboundMB", "current_outbound_mb"]);
  const destination = stringValue(raw, ["destination", "new_destination", "destination_ip", "newDestination"], "Unknown");
  const destinationStatusRaw = stringValue(raw, ["destinationStatus", "destination_status"], "").toLowerCase();
  const firstSeen = Boolean(value(raw, "first_seen_destination", "is_first_seen_destination"));
  const destinationStatus: "known" | "first-seen" =
    destinationStatusRaw.includes("first") || firstSeen ? "first-seen" : "known";

  const timeline = normalizeTimeline(value(raw, "timeline") || []);
  const ersHistoryRaw = value<any[]>(raw, "ersHistory", "ers_history") || timeline;
  const ersHistory: ErsHistoryPoint[] = (Array.isArray(ersHistoryRaw) ? ersHistoryRaw : []).map(
    (point: any, index: number) => ({
      label: stringValue(point, ["label", "day", "date"], `Day ${index + 1}`),
      ers: numberValue(point, ["ers", "ers_score", "risk_score"]),
    })
  );

  const comparisonRaw = value<any[]>(raw, "outboundComparison", "outbound_comparison") || [];
  const outboundComparison = Array.isArray(comparisonRaw)
    ? comparisonRaw.map((point: any, index: number) => ({
        label: stringValue(point, ["label", "day", "date"], `Point ${index + 1}`),
        baselineMB: numberValue(point, ["baselineMB", "baseline_mb", "baseline"]),
        currentMB: numberValue(point, ["currentMB", "current_mb", "current"]),
      }))
    : [];

  return {
    id: stringValue(raw, ["id", "host_id", "hostId"]),
    ersScore: numberValue(raw, ["ersScore", "ers_score", "ers", "risk_score"]),
    classification,
    classificationLabel: stringValue(
      raw,
      ["classificationLabel", "classification_label", "verdict"],
      classificationLabel(classification)
    ),
    department: stringValue(raw, ["department"], "Unknown department"),
    lastSeen: stringValue(raw, ["lastSeen", "last_seen"], "—"),
    baselineOutboundMB: baseline,
    currentOutboundMB: current,
    deviationPct: numberValue(
      raw,
      ["deviationPct", "deviation_pct", "behaviour_deviation_pct"],
      baseline > 0 ? ((current - baseline) / baseline) * 100 : 0
    ),
    destination,
    destinationStatus,
    repeatedOffHoursSessions: numberValue(raw, [
      "repeatedOffHoursSessions",
      "repeated_off_hours_sessions",
      "repeated_nights",
    ]),
    ersHistory,
    outboundComparison,
    timeline,
  };
}

function normalizeAlertListItem(raw: any): AlertListItem {
  const classification = normalizeClassification(
    value(raw, "classification", "status", "severity")
  );
  return {
    id: stringValue(raw, ["id", "alert_id", "alertId"]),
    hostId: stringValue(raw, ["hostId", "host_id"]),
    classification,
    ersScore: numberValue(raw, ["ersScore", "ers_score", "ers", "risk_score"]),
    createdAt: stringValue(raw, ["createdAt", "created_at", "timestamp"], "—"),
    summary: stringValue(raw, ["summary", "title", "verdict"], classificationLabel(classification)),
  };
}

function normalizeAlertEvidence(raw: any): AlertEvidence {
  const classification = normalizeClassification(
    value(raw, "classification", "status", "severity")
  );

  const rawSignals = value<any[]>(raw, "signals", "evidence") || [];
  const signals = (Array.isArray(rawSignals) ? rawSignals : []).map((signal: any, index: number) => ({
    id: stringValue(signal, ["id"], `signal-${index + 1}`),
    title: stringValue(signal, ["title", "name", "signal"], `Signal ${index + 1}`),
    description: stringValue(signal, ["description", "reason", "detail"], "Evidence detected by LeakSignal."),
    severity: (() => {
      const s = String(value(signal, "severity") ?? "high").toLowerCase();
      return (["low", "medium", "high", "critical"].includes(s) ? s : "high") as
        | "low"
        | "medium"
        | "high"
        | "critical";
    })(),
    icon: (() : AlertEvidence["signals"][number]["icon"] => {
      const name = String(value(signal, "icon") ?? "").toLowerCase();
      const title = String(value(signal, "title", "name") ?? "").toLowerCase();
      if (name === "clock" || title.includes("hour") || title.includes("time")) return "clock";
      if (name === "repeat" || title.includes("repeat") || title.includes("session")) return "repeat";
      if (name === "calendar" || title.includes("persist") || title.includes("day")) return "calendar";
      return "destination";
    })(),
  }));

  const fp = value<any>(raw, "falsePositiveCheck", "false_positive_check") || {};
  const fpResult = stringValue(fp, ["result"], "").toLowerCase();
  const approvedDestination = Boolean(value(fp, "approved_destination"));
  const scheduledBackup = Boolean(value(fp, "scheduled_backup"));
  const cleared = fpResult === "cleared" || approvedDestination || scheduledBackup;

  return {
    id: stringValue(raw, ["id", "alert_id", "alertId"]),
    hostId: stringValue(raw, ["hostId", "host_id"]),
    classification,
    classificationLabel: stringValue(
      raw,
      ["classificationLabel", "classification_label", "verdict", "title"],
      classificationLabel(classification)
    ),
    ersScore: numberValue(raw, ["ersScore", "ers_score", "ers", "risk_score"]),
    createdAt: stringValue(raw, ["createdAt", "created_at", "timestamp"], "—"),
    signals,
    falsePositiveCheck: {
      result: cleared ? "cleared" : "flagged",
      label: stringValue(
        fp,
        ["label"],
        cleared ? "Legitimate activity identified" : "No legitimate explanation found"
      ),
      reasoning: stringValue(
        fp,
        ["reasoning", "reason", "result"],
        cleared
          ? "The activity matches an approved or scheduled behavior."
          : "The activity does not match an approved destination or known scheduled behavior."
      ),
    },
  };
}

function riskDistributionFromHosts(hosts: HostSummary[]): RiskDistributionPoint[] {
  const counts: Record<RiskClassification, number> = {
    normal: 0,
    monitor: 0,
    suspicious: 0,
    exfiltration: 0,
  };
  for (const host of hosts) counts[host.classification] += 1;
  return [
    { classification: "normal", label: "Normal", count: counts.normal },
    { classification: "monitor", label: "Monitor", count: counts.monitor },
    { classification: "suspicious", label: "Suspicious", count: counts.suspicious },
    { classification: "exfiltration", label: "Exfiltration", count: counts.exfiltration },
  ];
}

export const api = {
  async uploadDataset(file: File): Promise<{ ok: boolean; message: string; events_processed?: number; hosts_analyzed?: number; critical_hosts?: number; suspicious_hosts?: number }> {
    const form = new FormData();
    form.append("file", file);
    const raw = await request<any>("/api/upload", { method: "POST", body: form });
    return {
      ok: Boolean(value(raw, "ok") ?? String(value(raw, "status") ?? "success").toLowerCase() === "success"),
      message: stringValue(raw, ["message"], "Dataset uploaded successfully"),
      events_processed: numberValue(raw, ["events_processed"]),
      hosts_analyzed: numberValue(raw, ["hosts_analyzed"]),
      critical_hosts: numberValue(raw, ["critical_hosts"]),
      suspicious_hosts: numberValue(raw, ["suspicious_hosts"]),
    };
  },

  async resetDemo(): Promise<{ ok: boolean }> {
    const raw = await request<any>("/api/reset", { method: "POST" });
    return { ok: String(value(raw, "status")) === "success" };
  },

  async reloadDataset(): Promise<{ ok: boolean; message: string }> {
    const raw = await request<any>("/api/reload", { method: "POST" });
    return {
      ok: String(value(raw, "status")) === "success",
      message: stringValue(raw, ["message"], "Dataset reloaded"),
    };
  },

  async getDashboardSummary(): Promise<DashboardSummary> {
    return withFallback(
      async () => normalizeDashboard(await request<any>("/api/dashboard")),
      mockDashboardSummary
    );
  },

  async getHosts(): Promise<HostSummary[]> {
    return withFallback(async () => {
      const raw = await request<any>("/api/hosts");
      const list = Array.isArray(raw) ? raw : value<any[]>(raw, "hosts", "data") || [];
      return list.map(normalizeHostSummary);
    }, mockHighRiskHosts);
  },

  async getRiskDistribution(): Promise<RiskDistributionPoint[]> {
    return withFallback(async () => riskDistributionFromHosts(await api.getHosts()), mockRiskDistribution);
  },

  async getErsActivity(): Promise<ErsHistoryPoint[]> {
    return withFallback(async () => {
      const timeline = await api.getHostTimeline("FIN-PC-07");
      return timeline.map((point) => ({ label: point.date || point.day, ers: point.ers }));
    }, mockErsActivity);
  },

  async getHostProfile(id: string): Promise<HostProfile> {
    return withFallback(
      async () => normalizeHostProfile(await request<any>(`/api/hosts/${encodeURIComponent(id)}`)),
      getMockHostProfile(id)
    );
  },

  async getHostTimeline(id: string): Promise<HostProfile["timeline"]> {
    return withFallback(
      async () => normalizeTimeline(await request<any>(`/api/hosts/${encodeURIComponent(id)}/timeline`)),
      getMockHostProfile(id).timeline
    );
  },

  async getAlerts(): Promise<AlertListItem[]> {
    return withFallback(async () => {
      const raw = await request<any>("/api/alerts");
      const list = Array.isArray(raw) ? raw : value<any[]>(raw, "alerts", "data") || [];
      return list.map(normalizeAlertListItem);
    }, mockAlertsList);
  },

  async getAlertEvidence(id: string): Promise<AlertEvidence> {
    return withFallback(
      async () => normalizeAlertEvidence(await request<any>(`/api/alerts/${encodeURIComponent(id)}`)),
      getMockAlertEvidence(id)
    );
  },
};

export { ApiError };
