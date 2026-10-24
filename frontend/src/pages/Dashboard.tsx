import { useQuery } from "@tanstack/react-query";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import KpiCard from "../components/KpiCard";
import AgentLoop from "../components/AgentLoop";
import DecisionBadge from "../components/DecisionBadge";
import RiskBar from "../components/RiskBar";

const COLORS = { high: "#ff6b6b", medium: "#ffb020", low: "#3ddc84" };

export default function Dashboard() {
  const stats = useQuery({ queryKey: ["stats"], queryFn: api.stats });
  const cases = useQuery({ queryKey: ["cases", "recent"], queryFn: () => api.cases() });

  // Simulating the agent loop active stage for the demo
  const step = { stage: "investigate", message: "Extracting domain facts for acmepay-secure-login.com..." };

  const d = stats.data?.by_decision;
  const pie = d ? (["high", "medium", "low"] as const).map((k) => ({ name: k, value: d[k] })) : [];

  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <KpiCard label="Threats analysed" value={stats.data?.total ?? "-"} />
        <KpiCard label="High risk" value={d?.high ?? "-"} />
        {/* 👇 THIS IS THE FIXED LINE 👇 */}
        <KpiCard label="Awaiting review" value={stats.data?.awaiting_review ?? "-"} hint="Open the review queue" />
        <KpiCard label="Median detection time" value={(stats.data?.median_detection_seconds ?? 0).toFixed(1) + " s"} hint="Measured on this run" />
      </div>

      {/* Agent Loop Animation */}
      <AgentLoop active={step.stage} message={step.message} />

      {/* Bottom section: List and Chart */}
      <div className="grid gap-6 lg:grid-cols-3">
        <section className="lg:col-span-2 rounded-xl border border-border/60 bg-panel/60 p-4">
          <h2 className="mb-3 font-bold text-accent">Latest threats</h2>
          <ul className="divide-y divide-border/30">
            {cases.data?.items.map((c) => (
              <li key={c.id} className="flex items-center justify-between py-3">
                <Link to={"/cases/" + c.id} className="font-mono text-sm hover:text-accent hover:underline">
                  {c.target}
                </Link>
                <div className="flex items-center gap-4">
                  <RiskBar score={c.risk_score} />
                  <DecisionBadge decision={c.decision} />
                </div>
              </li>
            ))}
          </ul>
        </section>

        <section className="rounded-xl border border-border/60 bg-panel/60 p-4">
          <h2 className="mb-3 font-bold text-accent">Decisions</h2>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={pie} dataKey="value" nameKey="name" innerRadius={55} outerRadius={85}>
                {pie.map((x) => <Cell key={x.name} fill={COLORS[x.name as keyof typeof COLORS]} />)}
              </Pie>
              <Tooltip contentStyle={{ backgroundColor: '#0b2e17', borderColor: '#249344', color: '#fff' }} />
            </PieChart>
          </ResponsiveContainer>
        </section>
      </div>
    </div>
  );
}