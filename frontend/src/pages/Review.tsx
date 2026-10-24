import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import DecisionBadge from "../components/DecisionBadge";

export default function Review() {
  // Fetch cases awaiting review
  const { data, isLoading, refetch: refetchCases } = useQuery({ 
    queryKey: ["cases", "review"], 
    queryFn: () => api.cases() 
  });

  // Fetch all actions so we can find the block action for a case
  const { data: actionsData, refetch: refetchActions } = useQuery({
    queryKey: ["actions"],
    queryFn: () => api.actions()
  });

  const cases = data?.items.filter(c => c.status === "awaiting_review") || [];
  const [selectedCase, setSelectedCase] = useState<number | null>(cases[0]?.id || null);
  
  const [toast, setToast] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);

  async function handleApprove(caseId: number) {
    if (!actionsData) return;
    setIsProcessing(true);
    try {
      // 1. Find the pending action for this case
      const action = actionsData.find(a => a.case_id === caseId && a.state === "pending_approval");
      
      // 2. If an action exists, approve it (this triggers the SIMULATED block in terminal)
      if (action) {
        await api.approveAction(action.id);
      }
      
      // 3. Mark the case as confirmed in the database
      await api.reviewCase(caseId, "confirmed");
      
      setToast("Action Approved & Executed! Check backend terminal.");
      refetchCases();
      refetchActions();
      setSelectedCase(null);
    } catch (e) {
      setToast("Failed to approve action.");
      console.error(e);
    } finally {
      setIsProcessing(false);
      setTimeout(() => setToast(""), 4000);
    }
  }

  async function handleFalsePositive(caseId: number) {
    setIsProcessing(true);
    try {
      await api.reviewCase(caseId, "false_positive");
      setToast("Case marked as False Positive.");
      refetchCases();
      setSelectedCase(null);
    } catch (e) {
      setToast("Failed to update case.");
    } finally {
      setIsProcessing(false);
      setTimeout(() => setToast(""), 4000);
    }
  }

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
                <p className="text-sm text-muted mt-2">Reviewing threat target: {activeCase.target}</p>
              </div>

              <div className="flex gap-3 border-t border-border/30 pt-4">
                <button 
                  onClick={() => handleApprove(activeCase.id)}
                  disabled={isProcessing}
                  className="rounded-lg bg-accent px-4 py-2 font-bold text-black hover:bg-accent/80 disabled:opacity-50"
                >
                  {isProcessing ? "Processing..." : "Approve Action"}
                </button>
                <button 
                  onClick={() => handleFalsePositive(activeCase.id)}
                  disabled={isProcessing}
                  className="rounded-lg border border-warn text-warn px-4 py-2 font-bold hover:bg-warn/10 disabled:opacity-50"
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