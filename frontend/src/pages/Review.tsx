import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import DecisionBadge from "../components/DecisionBadge";

export default function Review() {
  const { data, isLoading } = useQuery({ 
    queryKey: ["cases", "review"], 
    queryFn: () => api.cases() 
  });

  // We only want to show cases that are "awaiting_review"
  const cases = data?.items.filter(c => c.status === "awaiting_review") || [];
  const [selectedCase, setSelectedCase] = useState<number | null>(cases[0]?.id || null);
  
  // Fake toast message state
  const [toast, setToast] = useState("");

  const handleAction = (action: string) => {
    setToast(`Action ${action} recorded (dry-run: no real system changed).`);
    setTimeout(() => setToast(""), 4000); // Hide toast after 4 seconds
  };

  if (isLoading) return <div className="text-muted">Loading queue...</div>;

  const activeCase = cases.find(c => c.id === selectedCase);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-2xl font-bold text-accent">Review Queue</h1>
          <p className="text-sm text-muted">Medium and high-risk cases awaiting human approval.</p>
        </div>
        {toast && (
          <div className="rounded-lg bg-ok/20 border border-ok text-ok px-4 py-2 text-sm font-bold animate-pulse">
            {toast}
          </div>
        )}
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        {/* Left column: List of cases */}
        <div className="space-y-2 border-r border-border/30 pr-4">
          {cases.length === 0 ? (
            <p className="text-sm text-muted">No cases awaiting review.</p>
          ) : (
            cases.map((c) => (
              <button
                key={c.id}
                onClick={() => setSelectedCase(c.id)}
                className={`w-full text-left rounded-lg border p-3 transition-colors ${
                  selectedCase === c.id ? "border-accent bg-panel" : "border-border/40 hover:bg-panel/60"
                }`}
              >
                <div className="font-mono text-sm truncate">{c.target}</div>
                <div className="mt-2 flex justify-between items-center">
                  <span className="text-xs text-muted">Score: {Math.round(c.risk_score * 100)}</span>
                  <DecisionBadge decision={c.decision} />
                </div>
              </button>
            ))
          )}
        </div>

        {/* Right column: Detail & Actions */}
        <div className="md:col-span-2">
          {activeCase ? (
            <div className="rounded-xl border border-border/60 bg-panel/60 p-6 space-y-6">
              <div>
                <h2 className="font-mono text-xl">{activeCase.target}</h2>
                {/* 👇 THIS IS THE FIXED LINE */}
                <p className="text-sm text-muted mt-2">Reviewing threat target: {activeCase.target}</p>
              </div>

              <div className="flex gap-3 border-t border-border/30 pt-4">
                <button 
                  onClick={() => handleAction("Approve")}
                  className="rounded-lg bg-accent px-4 py-2 font-bold text-black hover:bg-accent/80"
                >
                  Approve Action
                </button>
                <button 
                  onClick={() => handleAction("Reject")}
                  className="rounded-lg border border-muted text-muted px-4 py-2 font-bold hover:bg-white/5"
                >
                  Reject
                </button>
                <button 
                  onClick={() => handleAction("False Positive")}
                  className="rounded-lg border border-warn text-warn px-4 py-2 font-bold hover:bg-warn/10"
                >
                  Mark False Positive
                </button>
              </div>
              
              <div className="text-sm text-muted">
                <Link to={`/cases/${activeCase.id}`} className="text-accent hover:underline">
                  Open full case details →
                </Link>
              </div>
            </div>
          ) : (
            <div className="text-muted grid place-items-center h-full">Select a case to review</div>
          )}
        </div>
      </div>
    </div>
  );
}