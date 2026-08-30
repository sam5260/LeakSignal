import { ShieldCheck, UserCircle2 } from "lucide-react";

export function Header({ title, subtitle }: { title: string; subtitle?: string }) {
  return (
    <header className="flex h-16 shrink-0 items-center justify-between border-b border-base-600 bg-base-900/60 px-6 backdrop-blur">
      <div>
        <h1 className="text-base font-semibold text-ink-100">{title}</h1>
        {subtitle ? <p className="text-xs text-ink-500">{subtitle}</p> : null}
      </div>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 rounded-full border border-status-normal/25 bg-status-normal/10 px-3 py-1.5 text-xs font-medium text-status-normal">
          <ShieldCheck className="h-3.5 w-3.5" />
          System Nominal
        </div>
        <div className="flex items-center gap-2 rounded-full border border-base-600 bg-base-850 px-2 py-1.5">
          <UserCircle2 className="h-5 w-5 text-ink-500" />
          <span className="pr-1 text-xs font-medium text-ink-300">SOC Analyst</span>
        </div>
      </div>
    </header>
  );
}
