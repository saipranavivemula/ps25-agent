export default function RiskBar({ score }: { score: number }) {
  const pct = Math.round(score * 100);
  const color = score >= 0.85 ? "bg-danger" : score >= 0.6 ? "bg-warn" : "bg-ok";
  
  return (
    <div className="flex items-center gap-2" title={"Risk score " + pct + "%"}>
      <div className="h-2 w-24 overflow-hidden rounded bg-white/10">
        <div className={"h-full " + color} style={{ width: pct + "%" }} />
      </div>
      <span className="w-9 text-right text-sm tabular-nums">{pct}</span>
    </div>
  );
}