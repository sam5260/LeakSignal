"use client";

import { useState, useRef } from "react";
import { Upload, FileText, CheckCircle2, AlertTriangle, Loader2 } from "lucide-react";
import { DashboardShell } from "@/components/layout/DashboardShell";
import { api } from "@/services/api";

type UploadState = "idle" | "uploading" | "done" | "error";

export default function UploadPage() {
  const [state, setState] = useState<UploadState>("idle");
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");
  const [fileName, setFileName] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);

  const handleUpload = async () => {
    const file = fileRef.current?.files?.[0];
    if (!file) {
      setError("Choose a CSV file first.");
      setState("error");
      return;
    }

    setState("uploading");
    setFileName(file.name);
    setError("");

    try {
      const res = await api.uploadDataset(file);
      setResult(res);
      setState("done");
    } catch (err: any) {
      setError(err?.message || "Upload failed");
      setState("error");
    }
  };

  const handleReset = async () => {
    setState("uploading");
    try {
      await api.resetDemo();
      setState("idle");
      setResult(null);
      setFileName("");
      if (fileRef.current) fileRef.current.value = "";
    } catch (err: any) {
      setError(err?.message || "Reset failed");
      setState("error");
    }
  };

  const handleReload = async () => {
    setState("uploading");
    try {
      const res = await api.reloadDataset();
      setResult({ message: res.message, events_processed: 0, hosts_analyzed: 0, critical_hosts: 0, suspicious_hosts: 0 });
      setState("done");
    } catch (err: any) {
      setError(err?.message || "Reload failed");
      setState("error");
    }
  };

  return (
    <DashboardShell title="Upload Network Data" subtitle="Ingest CSV network metadata for analysis">
      <div className="mx-auto max-w-2xl">
        {/* Upload Card */}
        <div className="rounded-xl border border-base-600 bg-base-850 p-8 shadow-panel">
          <div className="flex flex-col items-center text-center">
            <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-signal/10">
              <Upload className="h-8 w-8 text-signal" />
            </div>
            <h2 className="mt-4 text-lg font-semibold text-ink-100">Upload Network Metadata</h2>
            <p className="mt-1 text-sm text-ink-500">
              CSV with columns: host_id, timestamp, src_ip, dst_ip, port, protocol, bytes_sent, bytes_received, duration, destination_category
            </p>

            {/* File Input */}
            <div className="mt-6 w-full">
              <label className="flex cursor-pointer flex-col items-center rounded-lg border-2 border-dashed border-base-600 bg-base-900/50 p-6 transition hover:border-signal/40 hover:bg-signal/5">
                <FileText className="h-8 w-8 text-ink-500" />
                <span className="mt-2 text-sm text-ink-500">
                  {fileName || "Click to select dataset.csv"}
                </span>
                <input
                  ref={fileRef}
                  type="file"
                  accept=".csv"
                  className="hidden"
                  onChange={(e) => {
                    if (e.target.files?.[0]) setFileName(e.target.files[0].name);
                  }}
                />
              </label>
            </div>

            {/* Action Buttons */}
            <div className="mt-6 flex flex-wrap gap-3">
              <button
                onClick={handleUpload}
                disabled={state === "uploading"}
                className="flex items-center gap-2 rounded-lg bg-signal px-6 py-2.5 text-sm font-semibold text-white transition hover:bg-signal/80 disabled:opacity-50"
              >
                {state === "uploading" ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Upload className="h-4 w-4" />
                )}
                {state === "uploading" ? "Processing..." : "Analyze Dataset"}
              </button>

              <button
                onClick={handleReload}
                disabled={state === "uploading"}
                className="flex items-center gap-2 rounded-lg border border-base-600 bg-base-800 px-4 py-2.5 text-sm font-medium text-ink-300 transition hover:bg-base-700 disabled:opacity-50"
              >
                Reload Demo
              </button>

              <button
                onClick={handleReset}
                disabled={state === "uploading"}
                className="flex items-center gap-2 rounded-lg border border-status-critical/30 bg-status-critical/5 px-4 py-2.5 text-sm font-medium text-status-critical transition hover:bg-status-critical/10 disabled:opacity-50"
              >
                Reset Database
              </button>
            </div>
          </div>
        </div>

        {/* Result Card */}
        {state === "done" && result && (
          <div className="mt-6 rounded-xl border border-status-normal/25 bg-status-normal/5 p-6 shadow-panel">
            <div className="flex items-start gap-3">
              <CheckCircle2 className="h-5 w-5 text-status-normal mt-0.5" />
              <div>
                <p className="font-semibold text-status-normal">Analysis Complete</p>
                <p className="mt-1 text-sm text-ink-500">{result.message}</p>
                {result.events_processed > 0 && (
                  <div className="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-4">
                    <Stat label="Events" value={result.events_processed} />
                    <Stat label="Hosts" value={result.hosts_analyzed} />
                    <Stat label="Critical" value={result.critical_hosts} tone="critical" />
                    <Stat label="Suspicious" value={result.suspicious_hosts} tone="suspicious" />
                  </div>
                )}
                <a
                  href="/"
                  className="mt-4 inline-flex items-center gap-1.5 text-sm font-medium text-signal hover:underline"
                >
                  View Dashboard →
                </a>
              </div>
            </div>
          </div>
        )}

        {/* Error Card */}
        {state === "error" && (
          <div className="mt-6 rounded-xl border border-status-critical/25 bg-status-critical/5 p-6 shadow-panel">
            <div className="flex items-start gap-3">
              <AlertTriangle className="h-5 w-5 text-status-critical mt-0.5" />
              <div>
                <p className="font-semibold text-status-critical">Error</p>
                <p className="mt-1 text-sm text-ink-500">{error}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardShell>
  );
}

function Stat({ label, value, tone }: { label: string; value: number; tone?: "critical" | "suspicious" }) {
  const color = tone === "critical" ? "text-status-critical" : tone === "suspicious" ? "text-status-suspicious" : "text-ink-100";
  return (
    <div className="rounded-lg border border-base-600 bg-base-800/50 p-3 text-center">
      <p className="text-[10px] uppercase tracking-wide text-ink-700">{label}</p>
      <p className={`mt-1 font-mono text-xl font-semibold ${color}`}>{value}</p>
    </div>
  );
}
