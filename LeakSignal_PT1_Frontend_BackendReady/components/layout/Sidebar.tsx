"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutGrid, MonitorSmartphone, ShieldAlert, Radar, Upload } from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { href: "/", label: "Overview", icon: LayoutGrid, match: (p: string) => p === "/" },
  { href: "/upload", label: "Upload", icon: Upload, match: (p: string) => p === "/upload" },
  { href: "/hosts/FIN-PC-07", label: "Hosts", icon: MonitorSmartphone, match: (p: string) => p.startsWith("/hosts") },
  { href: "/alerts", label: "Alerts", icon: ShieldAlert, match: (p: string) => p.startsWith("/alerts") },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex h-auto md:h-screen w-full md:w-60 shrink-0 flex-col border-b md:border-b-0 md:border-r border-base-600 bg-base-900/80 z-10">
      <div className="flex items-center gap-2.5 border-b border-base-600 px-5 py-5">
        <div className="relative flex h-8 w-8 items-center justify-center rounded-md bg-signal/15">
          <Radar className="h-4.5 w-4.5 text-signal" strokeWidth={2.25} />
          <span className="absolute -right-0.5 -top-0.5 h-2 w-2 rounded-full bg-status-critical" />
        </div>
        <div className="leading-tight">
          <p className="font-mono text-sm font-semibold tracking-tight text-ink-100">LeakSignal</p>
          <p className="text-[10px] uppercase tracking-widest text-ink-700">Exfil Detection</p>
        </div>
      </div>

      <nav className="flex-1 md:space-y-1 px-3 py-4 flex flex-row md:flex-col gap-2 overflow-x-auto">
        <p className="px-2 pb-2 text-[10px] font-medium uppercase tracking-widest text-ink-700">
          Monitoring
        </p>
        {NAV_ITEMS.map((item) => {
          const active = item.match(pathname);
          const Icon = item.icon;
          return (
            <Link
              key={item.label}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                active
                  ? "bg-signal/10 text-signal border border-signal/20"
                  : "border border-transparent text-ink-500 hover:bg-base-800 hover:text-ink-100"
              )}
            >
              <Icon className="h-4 w-4" strokeWidth={2} />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="border-t border-base-600 px-5 py-4">
        <div className="flex items-center gap-2 text-[11px] text-ink-700">
          <span className="h-1.5 w-1.5 rounded-full bg-status-normal" />
          Engine online · baseline synced
        </div>
      </div>
    </aside>
  );
}
