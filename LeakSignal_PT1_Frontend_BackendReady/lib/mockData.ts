import type {
  AlertEvidence,
  AlertListItem,
  DashboardSummary,
  ErsHistoryPoint,
  HostProfile,
  HostSummary,
  RiskDistributionPoint,
} from "@/types";

// ---------------------------------------------------------------------------
// Overview Dashboard
// ---------------------------------------------------------------------------

export const mockDashboardSummary: DashboardSummary = {
  monitoredHosts: 248,
  criticalHosts: 3,
  suspiciousHosts: 7,
  alertsToday: 12,
  monitoredHostsDelta: "+6 this week",
  criticalHostsDelta: "+1 since yesterday",
  suspiciousHostsDelta: "+2 since yesterday",
  alertsTodayDelta: "4 unresolved",
};

export const mockHighRiskHosts: HostSummary[] = [
  { id: "FIN-PC-07", ersScore: 91, classification: "exfiltration", lastSeen: "2 min ago", department: "Finance" },
  { id: "HR-PC-02", ersScore: 68, classification: "suspicious", lastSeen: "14 min ago", department: "Human Resources" },
  { id: "ENG-WS-14", ersScore: 58, classification: "suspicious", lastSeen: "31 min ago", department: "Engineering" },
  { id: "OPS-PC-21", ersScore: 44, classification: "monitor", lastSeen: "1 hr ago", department: "Operations" },
  { id: "BACKUP-SERVER-01", ersScore: 12, classification: "normal", lastSeen: "3 min ago", department: "Infrastructure" },
  { id: "SALES-PC-09", ersScore: 37, classification: "monitor", lastSeen: "2 hr ago", department: "Sales" },
  { id: "LEGAL-PC-03", ersScore: 22, classification: "normal", lastSeen: "5 hr ago", department: "Legal" },
];

export const mockRiskDistribution: RiskDistributionPoint[] = [
  { classification: "normal", label: "Normal", count: 214 },
  { classification: "monitor", label: "Monitor", count: 24 },
  { classification: "suspicious", label: "Suspicious", count: 7 },
  { classification: "exfiltration", label: "Exfiltration", count: 3 },
];

export const mockErsActivity: ErsHistoryPoint[] = [
  { label: "Aug 24", ers: 18 },
  { label: "Aug 25", ers: 22 },
  { label: "Aug 26", ers: 26 },
  { label: "Aug 27", ers: 41 },
  { label: "Aug 28", ers: 58 },
  { label: "Aug 29", ers: 74 },
  { label: "Aug 30", ers: 91 },
];

// ---------------------------------------------------------------------------
// Host Investigation — 3 demo hosts
// ---------------------------------------------------------------------------

const finPc07: HostProfile = {
  id: "FIN-PC-07",
  ersScore: 91,
  classification: "exfiltration",
  classificationLabel: "Possible Slow Data Exfiltration",
  department: "Finance",
  lastSeen: "2 min ago",
  baselineOutboundMB: 40,
  currentOutboundMB: 312,
  deviationPct: 680,
  destination: "185.220.101.44 (unclassified, EU)",
  destinationStatus: "first-seen",
  repeatedOffHoursSessions: 4,
  ersHistory: [
    { label: "Day 1", ers: 31 },
    { label: "Day 2", ers: 38 },
    { label: "Day 3", ers: 62 },
    { label: "Day 4", ers: 91 },
  ],
  outboundComparison: [
    { label: "Mon", baselineMB: 5, currentMB: 6 },
    { label: "Tue", baselineMB: 4, currentMB: 7 },
    { label: "Wed", baselineMB: 6, currentMB: 8 },
    { label: "Thu (night)", baselineMB: 5, currentMB: 42 },
  ],
  timeline: [
    { day: "Day 1", date: "Aug 27", classification: "monitor", ers: 31, note: "5–8 MB transfer to same unusual destination, 01:40 AM" },
    { day: "Day 2", date: "Aug 28", classification: "monitor", ers: 38, note: "Repeated low-volume transfer, same destination, 02:05 AM" },
    { day: "Day 3", date: "Aug 29", classification: "suspicious", ers: 62, note: "Third consecutive night, pattern persistence confirmed" },
    { day: "Day 4", date: "Aug 30", classification: "exfiltration", ers: 91, note: "Fourth night, volume increase + off-hours + persistence" },
  ],
};

const hrPc02: HostProfile = {
  id: "HR-PC-02",
  ersScore: 68,
  classification: "suspicious",
  classificationLabel: "New Destination + Off-Hours Transfer",
  department: "Human Resources",
  lastSeen: "14 min ago",
  baselineOutboundMB: 15,
  currentOutboundMB: 12000 / 1000,
  deviationPct: 0,
  destination: "203.0.113.19 (unclassified, first contact)",
  destinationStatus: "first-seen",
  repeatedOffHoursSessions: 1,
  ersHistory: [
    { label: "Day 1", ers: 14 },
    { label: "Day 2", ers: 16 },
    { label: "Day 3", ers: 68 },
  ],
  outboundComparison: [
    { label: "Mon 10AM", baselineMB: 8, currentMB: 9 },
    { label: "Tue 2PM", baselineMB: 6, currentMB: 7 },
    { label: "Wed 2:15AM", baselineMB: 0, currentMB: 12 },
  ],
  timeline: [
    { day: "Day 1", date: "Aug 28", classification: "normal", ers: 14, note: "Normal working-hours activity with known services" },
    { day: "Day 2", date: "Aug 29", classification: "normal", ers: 16, note: "No anomalies detected" },
    { day: "Day 3", date: "Aug 30", classification: "suspicious", ers: 68, note: "12 MB sent to first-seen destination at 2:15 AM" },
  ],
};

const backupServer01: HostProfile = {
  id: "BACKUP-SERVER-01",
  ersScore: 9,
  classification: "normal",
  classificationLabel: "Approved Backup Pattern",
  department: "Infrastructure",
  lastSeen: "3 min ago",
  baselineOutboundMB: 500,
  currentOutboundMB: 512,
  deviationPct: 2,
  destination: "backup-vault.corp-approved.net (approved)",
  destinationStatus: "known",
  repeatedOffHoursSessions: 0,
  ersHistory: [
    { label: "Day 1", ers: 8 },
    { label: "Day 2", ers: 9 },
    { label: "Day 3", ers: 8 },
    { label: "Day 4", ers: 9 },
  ],
  outboundComparison: [
    { label: "Mon", baselineMB: 480, currentMB: 490 },
    { label: "Tue", baselineMB: 510, currentMB: 505 },
    { label: "Wed", baselineMB: 495, currentMB: 512 },
    { label: "Thu", baselineMB: 500, currentMB: 498 },
  ],
  timeline: [
    { day: "Day 1", date: "Aug 27", classification: "normal", ers: 8, note: "400–600 MB nightly transfer, approved destination" },
    { day: "Day 2", date: "Aug 28", classification: "normal", ers: 9, note: "Stable repeated schedule, expected window" },
    { day: "Day 3", date: "Aug 29", classification: "normal", ers: 8, note: "Consistent with 90-day rolling baseline" },
    { day: "Day 4", date: "Aug 30", classification: "normal", ers: 9, note: "No deviation from approved backup pattern" },
  ],
};

export const mockHostProfiles: Record<string, HostProfile> = {
  "FIN-PC-07": finPc07,
  "HR-PC-02": hrPc02,
  "BACKUP-SERVER-01": backupServer01,
};

export function getMockHostProfile(id: string): HostProfile {
  return mockHostProfiles[id] ?? finPc07;
}

// ---------------------------------------------------------------------------
// Alert Evidence
// ---------------------------------------------------------------------------

export const mockAlertsList: AlertListItem[] = [
  { id: "ALRT-1042", hostId: "FIN-PC-07", classification: "exfiltration", ersScore: 91, createdAt: "2 min ago", summary: "4-day slow-drip pattern to first-seen destination" },
  { id: "ALRT-1041", hostId: "HR-PC-02", classification: "suspicious", ersScore: 68, createdAt: "14 min ago", summary: "First-seen destination + off-hours transfer" },
  { id: "ALRT-1039", hostId: "ENG-WS-14", classification: "suspicious", ersScore: 58, createdAt: "31 min ago", summary: "Repeated sessions outside baseline window" },
  { id: "ALRT-1033", hostId: "BACKUP-SERVER-01", classification: "normal", ersScore: 9, createdAt: "3 min ago", summary: "Large transfer matched approved backup pattern" },
];

const alertFinPc07: AlertEvidence = {
  id: "ALRT-1042",
  hostId: "FIN-PC-07",
  classification: "exfiltration",
  classificationLabel: "Possible Slow Data Exfiltration",
  ersScore: 91,
  createdAt: "Aug 30, 2026 · 02:12 AM",
  signals: [
    {
      id: "sig-1",
      icon: "destination",
      title: "First-Seen Destination",
      description:
        "This host communicated with a destination that has not previously been observed in its behavioral profile.",
      severity: "high",
    },
    {
      id: "sig-2",
      icon: "clock",
      title: "Off-Hours Transfer",
      description: "Data transfer occurred outside the host's normal operating hours, between 1:30 AM and 2:15 AM.",
      severity: "high",
    },
    {
      id: "sig-3",
      icon: "repeat",
      title: "Repeated Sessions",
      description: "Similar low-volume outbound sessions were detected repeatedly across four consecutive nights.",
      severity: "critical",
    },
    {
      id: "sig-4",
      icon: "calendar",
      title: "Multi-Day Persistence",
      description:
        "Suspicious activity continued across multiple days, increasing confidence that the behavior is persistent rather than accidental.",
      severity: "critical",
    },
  ],
  falsePositiveCheck: {
    result: "flagged",
    label: "No Approved Pattern Found",
    reasoning:
      "Destination is not present in the approved-services registry, and no scheduled job or backup policy matches this transfer window.",
  },
};

const alertHrPc02: AlertEvidence = {
  id: "ALRT-1041",
  hostId: "HR-PC-02",
  classification: "suspicious",
  classificationLabel: "New Destination + Off-Hours Transfer",
  ersScore: 68,
  createdAt: "Aug 30, 2026 · 02:15 AM",
  signals: [
    {
      id: "sig-1",
      icon: "destination",
      title: "First-Seen Destination",
      description: "This host sent data to an IP address never before observed in 90 days of baseline history.",
      severity: "high",
    },
    {
      id: "sig-2",
      icon: "clock",
      title: "Off-Hours Transfer",
      description: "The 12 MB transfer occurred at 2:15 AM, well outside this host's normal 9 AM – 6 PM activity window.",
      severity: "medium",
    },
  ],
  falsePositiveCheck: {
    result: "flagged",
    label: "No Approved Pattern Found",
    reasoning: "No recurring schedule or approved-destination match exists for this host at this transfer volume or time.",
  },
};

const alertBackup: AlertEvidence = {
  id: "ALRT-1033",
  hostId: "BACKUP-SERVER-01",
  classification: "normal",
  classificationLabel: "Approved Backup Pattern",
  ersScore: 9,
  createdAt: "Aug 30, 2026 · 01:00 AM",
  signals: [
    {
      id: "sig-1",
      icon: "calendar",
      title: "Stable Repeated Schedule",
      description: "This host transfers 400–600 MB nightly at the same time window, consistent for 90+ consecutive days.",
      severity: "low",
    },
    {
      id: "sig-2",
      icon: "destination",
      title: "Approved Destination",
      description: "The destination is registered in the approved-services list as the corporate backup vault.",
      severity: "low",
    },
  ],
  falsePositiveCheck: {
    result: "cleared",
    label: "Approved Backup Pattern",
    reasoning:
      "Volume, timing, and destination all match a known, approved backup job. LeakSignal does not classify every large transfer as malicious.",
  },
};

export const mockAlertEvidence: Record<string, AlertEvidence> = {
  "ALRT-1042": alertFinPc07,
  "ALRT-1041": alertHrPc02,
  "ALRT-1033": alertBackup,
};

export function getMockAlertEvidence(id: string): AlertEvidence {
  return mockAlertEvidence[id] ?? alertFinPc07;
}
