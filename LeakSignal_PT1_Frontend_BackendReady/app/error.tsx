"use client";

import { useEffect } from "react";
import { DashboardShell } from "@/components/layout/DashboardShell";
import { ErrorState } from "@/components/ui/ErrorState";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("LeakSignal frontend error:", error);
  }, [error]);

  return (
    <DashboardShell title="LeakSignal" subtitle="Backend connection or data loading error">
      <ErrorState
        title="Unable to load LeakSignal data"
        message="Check that the FastAPI backend is running, CORS allows http://localhost:3000, NEXT_PUBLIC_API_BASE_URL is correct, and NEXT_PUBLIC_USE_MOCKS is set as intended."
      />
      <div className="mt-4 flex justify-center">
        <button
          type="button"
          onClick={() => reset()}
          className="rounded-lg border border-signal/30 bg-signal/10 px-4 py-2 text-sm font-medium text-signal transition hover:bg-signal/15"
        >
          Retry connection
        </button>
      </div>
    </DashboardShell>
  );
}
