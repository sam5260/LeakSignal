import { clsx, type ClassValue } from "clsx";
import type { RiskClassification, SignalSeverity } from "@/types";

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

export const CLASSIFICATION_META: Record<
  RiskClassification,
  { label: string; color: string; bg: string; border: string; dot: string }
> = {
  normal: {
    label: "Normal",
    color: "text-status-normal",
    bg: "bg-status-normal/10",
    border: "border-status-normal/30",
    dot: "bg-status-normal",
  },
  monitor: {
    label: "Monitor",
    color: "text-status-monitor",
    bg: "bg-status-monitor/10",
    border: "border-status-monitor/30",
    dot: "bg-status-monitor",
  },
  suspicious: {
    label: "Suspicious",
    color: "text-status-suspicious",
    bg: "bg-status-suspicious/10",
    border: "border-status-suspicious/30",
    dot: "bg-status-suspicious",
  },
  exfiltration: {
    label: "Exfiltration",
    color: "text-status-critical",
    bg: "bg-status-critical/10",
    border: "border-status-critical/30",
    dot: "bg-status-critical",
  },
};

export const SEVERITY_META: Record<SignalSeverity, { label: string; color: string; bg: string }> = {
  low: { label: "Low", color: "text-status-normal", bg: "bg-status-normal/10" },
  medium: { label: "Medium", color: "text-status-monitor", bg: "bg-status-monitor/10" },
  high: { label: "High", color: "text-status-suspicious", bg: "bg-status-suspicious/10" },
  critical: { label: "Critical", color: "text-status-critical", bg: "bg-status-critical/10" },
};

export function formatMB(mb: number): string {
  if (mb >= 1000) return `${(mb / 1000).toFixed(2)} GB`;
  return `${mb.toFixed(1)} MB`;
}

export function formatPct(pct: number): string {
  const sign = pct > 0 ? "+" : "";
  return `${sign}${pct.toFixed(0)}%`;
}
