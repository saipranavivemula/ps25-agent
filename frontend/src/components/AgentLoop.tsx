import clsx from "clsx";
import { Radar, Search, BadgeCheck, Gauge, ShieldCheck } from "lucide-react";

const STAGES = [
  { key: "monitor", label: "Monitor", Icon: Radar },
  { key: "investigate", label: "Investigate", Icon: Search },
  { key: "verify", label: "Verify", Icon: BadgeCheck },
  { key: "assess", label: "Assess risk", Icon: Gauge },
  { key: "respond", label: "Respond", Icon: ShieldCheck },
];

export default function AgentLoop({ active, message }: { active?: string; message?: string }) {
  const idx = STAGES.findIndex((s) => s.key === active);

  return (
    <div className="rounded-xl border border-border/60 bg-panel/60 p-4">
      <div className="flex items-center justify-between">
        {STAGES.map(({ key, label, Icon }, i) => (
          <div key={key} className="flex flex-1 items-center">
            <div className={clsx("flex flex-col items-center gap-1 transition-all", i === idx ? "scale-110" : "opacity-60")}>
              <div className={clsx(
                "grid h-12 w-12 place-items-center rounded-full border-2", 
                i === idx ? "border-accent bg-accent/15 text-accent shadow-[0_0_18px_rgba(193,255,114,0.5)]" : 
                i < idx ? "border-ok text-ok" : "border-border text-muted"
              )}>
                <Icon size={22} aria-hidden />
              </div>
              <span className="text-xs font-semibold">{label}</span>
            </div>
            {i < STAGES.length - 1 && (
              <div className={clsx("mx-2 h-0.5 flex-1", i < idx ? "bg-ok" : "bg-border/50")} />
            )}
          </div>
        ))}
      </div>
      <p className="mt-3 min-h-5 text-center text-sm text-muted" aria-live="polite">
        {message ?? "Agent idle: waiting for the next signal"}
      </p>
    </div>
  );
}