import type { ReactNode } from "react";

export default function KpiCard({ label, value, hint, icon }: { label: string; value: ReactNode; hint?: string; icon?: ReactNode }) {
  return (
    <div className="rounded-xl border border-border/60 bg-panel/70 p-4">
      <div className="flex items-center justify-between text-sm text-muted">
        {label} {icon}
      </div>
      <div className="mt-2 text-3xl font-bold text-accent tabular-nums">{value}</div>
      {hint && <div className="mt-1 text-xs text-muted">{hint}</div>}
    </div>
  );
}