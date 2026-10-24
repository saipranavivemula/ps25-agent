import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";
import RiskGauge from "../components/RiskGauge";
import DecisionBadge from "../components/DecisionBadge";
import HighlightedText from "../components/HighlightedText";

export default function CaseDetail() {
  const id = Number(useParams().id);
  
  const { data: c, isLoading, error } = useQuery({ 
    queryKey: ["case", id], 
    queryFn: () => api.case(id) 
  });

  const { data: actionsData, refetch: refetchActions } = useQuery({
    queryKey: ["actions"],
    queryFn: api.actions
  });

  if (isLoading) return <div className="text-muted">Loading case...</div>;
  if (error || !c) return <div role="alert" className="text-danger">Case not found.</div>;

  // 👇 SAFE EXTRACTIONS (Fixes TypeScript Errors) 👇
  const emailEv = c.evidence?.email;
  const domainEv = c.evidence?.domain || {};
  const bestMatch = domainEv.best_match || {};
  
  const filteredReasons = c.reasons?.filter(r => r.signal !== "domain_age") || [];
  
  // Using (a as any) to safely access case_id in case the types are strict
  const caseAction = actionsData?.find(a => (a as any).case_id === c.id && a.state === "pending_approval");

  async function handleApprove() {
    if (caseAction) {
      await api.approveAction(caseAction.id);
      await api.reviewCase(c.id, "confirmed");
      refetchActions();
      window.location.reload();
    }
  }

  async function handleReject() {
    if (caseAction) {
      await api.reviewCase(c.id, "false_positive");
      refetchActions();
      window.location.reload();
    }
  }

  const dateString = new Date(c.created_at).toLocaleString('en-IN', { 
    day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit' 
  });

  return (
    <div className="space-y-6">
      <Link to="/cases" className="text-sm text-accent hover:underline">← Back to Cases</Link>

      {/* Header Panel */}
      <div className="flex items-center justify-between rounded-xl border border-border/60 bg-panel/60 p-6">
        <div>
          <h1 className="font-mono text-2xl font-bold">{c.target}</h1>
          <div className="mt-2 flex gap-4 text-sm text-muted items-center">
            <DecisionBadge decision={c.decision} />
            <span className="uppercase">{c.target_type}</span>
            <span className="capitalize">{c.status.replace("_", " ")}</span>
            <span>{dateString}</span>
          </div>
          <p className="mt-4 max-w-2xl text-sm leading-relaxed text-gray-300">{c.summary}</p>
        </div>
        <div className="flex flex-col items-center">
          <RiskGauge score={c.risk_score} decision={c.decision} />
          <div className="text-sm font-bold mt-2 text-danger">Risk score {c.risk_score.toFixed(2)}</div>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* WHY THIS SCORE (LIST FORMAT) */}
        <div className="rounded-xl border border-border/60 bg-panel/60 p-6">
          <h2 className="mb-4 font-bold text-accent">Why this score</h2>
          {filteredReasons.length === 0 ? (
            <p className="text-sm text-muted">No strong rule-based signals were detected. This is not a guarantee that the item is safe.</p>
          ) : (
            <ul className="space-y-3">
              {filteredReasons.map((r) => (
                <li key={r.signal} className="flex justify-between items-start border-b border-border/30 pb-2 last:border-0">
                  <div>
                    <div className="font-bold text-sm text-gray-200 capitalize">{r.signal.replace(/_/g, " ")}</div>
                    <div className="text-xs text-muted">{r.detail}</div>
                  </div>
                  <span className="font-mono text-accent text-sm">+{r.contribution.toFixed(3)}</span>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* DOMAIN-STRING EVIDENCE TABLE */}
        <div className="rounded-xl border border-border/60 bg-panel/60 p-6">
          <h2 className="mb-4 font-bold text-accent">Domain-string evidence</h2>
          <table className="w-full text-sm">
            <tbody className="divide-y divide-border/20">
              <tr>
                <td className="py-2 text-muted">Registered domain</td>
                <td className="py-2 font-mono text-right">{domainEv.registered_domain || "N/A"}</td>
              </tr>
              <tr>
                <td className="py-2 text-muted">Closest protected brand</td>
                <td className="py-2 font-mono text-right">{bestMatch.brand || "N/A"}</td>
              </tr>
              <tr>
                <td className="py-2 text-muted">Similarity Score</td>
                <td className="py-2 font-mono text-right">{bestMatch.score ? bestMatch.score.toFixed(3) : "0.000"}</td>
              </tr>
              <tr>
                <td className="py-2 text-muted">Keywords</td>
                <td className="py-2 font-mono text-right">{domainEv.keywords?.join(", ") || "-"}</td>
              </tr>
              <tr>
                <td className="py-2 text-muted">Protected domain</td>
                <td className="py-2 font-mono text-right">{domainEv.is_protected_domain ? "Yes" : "No"}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* PROPOSED RESPONSE */}
      <div className="rounded-xl border border-border/60 bg-panel/60 p-6">
        <h2 className="mb-4 font-bold text-accent">Proposed response</h2>
        {caseAction ? (
          <div className="space-y-4">
            <div className="rounded-lg border border-warn/30 bg-warn/10 p-3 text-sm text-warn">
              Simulation only — no real email or domain is blocked.
            </div>
            <div className="flex items-center justify-between rounded-lg border border-border/60 bg-black/20 p-4">
              <div>
                <div className="font-bold uppercase text-sm">{caseAction.type.replace(/_/g, " ")}</div>
                <div className="text-xs text-muted capitalize">Status: {caseAction.state.replace(/_/g, " ")}</div>
              </div>
              <div className="flex gap-2">
                <button onClick={handleApprove} className="rounded bg-accent px-4 py-2 font-bold text-black hover:bg-accent/80 text-sm">
                  Approve simulation
                </button>
                <button onClick={handleReject} className="rounded border border-danger text-danger px-4 py-2 font-bold hover:bg-danger/10 text-sm">
                  Reject
                </button>
              </div>
            </div>
          </div>
        ) : (
          <p className="text-sm text-muted">No pending actions for this case.</p>
        )}
      </div>

      {/* EMAIL EVIDENCE */}
      {emailEv && (
        <div className="rounded-xl border border-border/60 bg-panel/60 p-6">
          <h2 className="mb-4 font-bold text-accent">Email Evidence</h2>
          <div className="space-y-4">
            <div className="text-sm">
              <span className="text-muted">From: </span> 
              <span className="font-mono text-warn">{emailEv.from}</span>
            </div>
            <div className="text-sm">
              <span className="text-muted">Subject: </span> 
              <span>{emailEv.subject}</span>
            </div>
            <div className="flex gap-2">
              {["spf", "dkim", "dmarc"].map((k) => {
                const v = (emailEv.auth && emailEv.auth[k] ? emailEv.auth[k] : "none").toLowerCase();
                const cls = v === "pass" ? "border-ok text-ok" : v === "none" ? "border-border text-muted" : "border-danger text-danger";
                return <span key={k} className={"rounded border px-2 py-0.5 text-xs font-bold " + cls}>{k.toUpperCase()}: {v}</span>;
              })}
            </div>
            <div className="rounded-lg border border-border/40 bg-black/20 p-3">
              <HighlightedText 
                text={emailEv.text || ""} 
                terms={["verify", "locked", "immediately", "identity"]} 
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}