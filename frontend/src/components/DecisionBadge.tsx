import clsx from "clsx";
import { ShieldAlert, ShieldQuestion, ShieldCheck } from "lucide-react";
import type { Decision } from "../types";

const MAP = {
  high: { label: "HIGH", cls: "border-danger text-danger bg-danger/10", Icon: ShieldAlert },
  medium: { label: "MEDIUM", cls: "border-warn text-warn bg-warn/10", Icon: ShieldQuestion },
  low: { label: "LOW", cls: "border-ok text-ok bg-ok/10", Icon: ShieldCheck },
} as const;

export default function DecisionBadge({ decision }: { decision: Decision }) {
  const { label, cls, Icon } = MAP[decision];
  return (
    <span className={clsx("inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-bold", cls)}>
      <Icon size={14} aria-hidden /> {label}
    </span>
  );
}