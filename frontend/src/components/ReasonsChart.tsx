import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";
import type { Reason } from "../types";

export default function ReasonsChart({ reasons }: { reasons: Reason[] }) {
  const data = reasons.map((r) => ({ 
    name: r.signal.replace(/_/g, " "), 
    value: r.contribution, 
    detail: r.detail 
  }));

  return (
    <ResponsiveContainer width="100%" height={Math.max(160, data.length * 50)}>
      <BarChart data={data} layout="vertical" margin={{ left: 40, right: 16 }}>
        <XAxis type="number" domain={[0, 0.5]} tick={{ fill: "#9db5a5", fontSize: 12 }} />
        <YAxis type="category" dataKey="name" width={150} tick={{ fill: "#e8f5ec", fontSize: 13 }} />
        {/* 👇 Fix: Adjusted the formatter to satisfy TypeScript */}
        <Tooltip 
          formatter={(value: any, _name: any, props: any) => [Number(value).toFixed(2), props.payload.detail]} 
          contentStyle={{ backgroundColor: '#0b2e17', borderColor: '#249344', color: '#fff' }}
        />
        <Bar dataKey="value" radius={[0, 4, 4, 0]}>
          {data.map((_, i) => <Cell key={i} fill="#c1ff72" />)}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}