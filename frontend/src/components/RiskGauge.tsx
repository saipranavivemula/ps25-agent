import type { Decision } from "../types";

export default function RiskGauge({ score, decision }: { score: number; decision: Decision }) {
  const r = 70, len = Math.PI * r;
  const pct = Math.max(0, Math.min(1, score));
  const color = decision === "high" ? "#ff6b6b" : decision === "medium" ? "#ffb020" : "#3ddc84";

  return (
    <svg viewBox="0 0 180 110" className="w-56" role="img" aria-label={"Risk score " + Math.round(pct * 100) + " out of 100"}>
      <path d="M20 90 A70 70 0 0 1 160 90" fill="none" stroke="#143d24" strokeWidth="14" strokeLinecap="round" />
      <path 
        d="M20 90 A70 70 0 0 1 160 90" 
        fill="none" 
        stroke={color} 
        strokeWidth="14" 
        strokeLinecap="round" 
        strokeDasharray={len} 
        strokeDashoffset={len * (1 - pct)} 
        style={{ transition: "stroke-dashoffset .8s ease" }} 
      />
      <text x="90" y="82" textAnchor="middle" fontSize="30" fontWeight="700" fill={color}>
        {Math.round(pct * 100)}
      </text>
      <text x="90" y="102" textAnchor="middle" fontSize="10" fill="#9db5a5">RISK SCORE</text>
    </svg>
  );
}