import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import DecisionBadge from "../components/DecisionBadge";
import RiskBar from "../components/RiskBar";

export default function Cases() {
  const { data, isLoading } = useQuery({ 
    queryKey: ["cases", "all"], 
    queryFn: () => api.cases() 
  });

  if (isLoading) return <div className="text-muted">Loading all cases...</div>;

  const cases = data?.items || [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-accent">All Analyzed Cases</h1>
        <p className="text-sm text-muted">Complete history of every threat investigated by the AI Agent.</p>
      </div>

      <div className="rounded-xl border border-border/60 bg-panel/60 p-4">
        <ul className="divide-y divide-border/30">
          {cases.length === 0 ? (
             <li className="py-4 text-center text-muted">No cases analyzed yet.</li>
          ) : (
            cases.map((c) => (
              <li key={c.id} className="flex items-center justify-between py-4 hover:bg-black/20 px-2 rounded transition-colors">
                <div>
                  <Link to={"/cases/" + c.id} className="font-mono text-sm hover:text-accent hover:underline font-bold">
                    {c.target}
                  </Link>
                  <div className="text-xs text-muted mt-1">Source: {c.source} | Status: {c.status}</div>
                </div>
                <div className="flex items-center gap-4">
                  <RiskBar score={c.risk_score} />
                  <DecisionBadge decision={c.decision} />
                </div>
              </li>
            ))
          )}
        </ul>
      </div>
    </div>
  );
}