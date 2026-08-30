export type RiskClassification = "normal" | "monitor" | "suspicious" | "exfiltration";

export interface DashboardSummary {
  monitoredHosts: number;
  criticalHosts: number;
  suspiciousHosts: number;
  alertsToday: number;
  monitoredHostsDelta?: string;
  criticalHostsDelta?: string;
  suspiciousHostsDelta?: string;
  alertsTodayDelta?: string;
}

export interface HostSummary {
  id: string;
  ersScore: number;
  classification: RiskClassification;
  lastSeen: string;
  department?: string;
}

export interface RiskDistributionPoint {
  classification: RiskClassification;
  label: string;
  count: number;
}

export interface ErsHistoryPoint {
  label: string;
  ers: number;
}

export interface OutboundComparisonPoint {
  label: string;
  baselineMB: number;
  currentMB: number;
}

export interface TimelineDay {
  day: string;
  date: string;
  classification: RiskClassification;
  ers: number;
  note?: string;
}

export interface HostProfile {
  id: string;
  ersScore: number;
  classification: RiskClassification;
  classificationLabel: string;
  department: string;
  lastSeen: string;
  baselineOutboundMB: number;
  currentOutboundMB: number;
  deviationPct: number;
  destination: string;
  destinationStatus: "known" | "first-seen";
  repeatedOffHoursSessions: number;
  ersHistory: ErsHistoryPoint[];
  outboundComparison: OutboundComparisonPoint[];
  timeline: TimelineDay[];
}

export type SignalSeverity = "low" | "medium" | "high" | "critical";

export interface AlertSignal {
  id: string;
  title: string;
  description: string;
  severity: SignalSeverity;
  icon: "destination" | "clock" | "repeat" | "calendar";
}

export interface AlertEvidence {
  id: string;
  hostId: string;
  classification: RiskClassification;
  classificationLabel: string;
  ersScore: number;
  createdAt: string;
  signals: AlertSignal[];
  falsePositiveCheck: {
    result: "flagged" | "cleared";
    label: string;
    reasoning: string;
  };
}

export interface AlertListItem {
  id: string;
  hostId: string;
  classification: RiskClassification;
  ersScore: number;
  createdAt: string;
  summary: string;
}
