import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";
import RiskGauge from "../components/RiskGauge";
import DecisionBadge from "../components/DecisionBadge";
import ReasonsChart from "../components/ReasonsChart";
import HighlightedText from "../components/HighlightedText";

export default function CaseDetail() {
  const id = Number(useParams().id);
  const { data: c, isLoading, error } = useQuery({ 
    queryKey: ["case", id], 
    queryFn: () => api.case(id) 
  });

  if (isLoading) return <div className="text-muted">Loading case...</div>;
  if (error || !c) return <div role="alert" className="text-danger">Case not found.</div>;

  return (
    <div className="space-y-6">
      <Link to="/" className="text-sm text-accent hover:underline">← Back to Dashboard</Link>

      {/* Header Panel */}
      <div className="flex items-center justify-between rounded-xl border border-border/60 bg-panel/60 p-6">
        <div>
          <h1 className="font-mono text-2xl font-bold">{c.target}</h1>
          <div className="mt-2 flex gap-4 text-sm text-muted items-center">
            <DecisionBadge decision={c.decision} />
            <span>Source: {c.source}</span>
          </div>
          <p className="mt-4 max-w-2xl text-sm leading-relaxed text-gray-300">{c.summary}</p>
        </div>
        <RiskGauge score={c.risk_score} decision={c.decision} />
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Reasons Chart */}
        <div className="rounded-xl border border-border/60 bg-panel/60 p-4">
          <h2 className="mb-4 font-bold text-accent">Why was this flagged?</h2>
          <ReasonsChart reasons={c.reasons} />
        </div>

        {/* Email Evidence */}
        <div className="rounded-xl border border-border/60 bg-panel/60 p-4">
          <h2 className="mb-4 font-bold text-accent">Email Evidence</h2>
          {c.evidence.email ? (
            <div className="space-y-4">
              <div className="text-sm">
                <span className="text-muted">From: </span> 
                <span className="font-mono text-warn">{c.evidence.email.from}</span>
              </div>
              <div className="text-sm">
                <span className="text-muted">Subject: </span> 
                <span>{c.evidence.email.subject}</span>
              </div>
              
              {/* Auth Chips */}
              <div className="flex gap-2">
                {["spf", "dkim", "dmarc"].map((k) => {
                  const v = (c.evidence.email!.auth[k] ?? "none").toLowerCase();
                  const cls = v === "pass" ? "border-ok text-ok" : v === "none" ? "border-border text-muted" : "border-danger text-danger";
                  return <span key={k} className={"rounded border px-2 py-0.5 text-xs font-bold " + cls}>{k.toUpperCase()}: {v}</span>;
                })}
              </div>

              <div className="rounded-lg border border-border/40 bg-black/20 p-3">
                <HighlightedText 
                  text={c.evidence.email.text} 
                  terms={["verify", "locked", "immediately", "identity"]} 
                />
              </div>
            </div>
          ) : (
            <p className="text-muted text-sm">No email data for this case.</p>
          )}
        </div>
      </div>
    </div>
  );
}