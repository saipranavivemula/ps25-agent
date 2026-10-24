import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";

export default function Audit() {
  // Fetch real logs from the backend
  const { data: logs, isLoading } = useQuery({ 
    queryKey: ["audit"], 
    queryFn: api.auditLog 
  });

  if (isLoading) return <div className="text-muted">Loading audit trail...</div>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-accent">Audit Log</h1>
        <p className="text-sm text-muted">Every action, decision, and human review is permanently recorded.</p>
      </div>

      <div className="rounded-xl border border-border/60 bg-panel/60 overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-black/40 text-muted border-b border-border/50">
            <tr>
              <th className="px-4 py-3 font-medium">Time</th>
              <th className="px-4 py-3 font-medium">Actor</th>
              <th className="px-4 py-3 font-medium">Event</th>
              <th className="px-4 py-3 font-medium">Target</th>
              <th className="px-4 py-3 font-medium">Details</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border/30">
            {logs?.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-muted">
                  No audit logs yet. Run an analysis or approve an action to generate logs.
                </td>
              </tr>
            ) : (
              logs?.map((log) => {
                // 👇 FIX: Convert UTC to Indian Standard Time (IST)
                // The backend sends naive UTC strings, so we append 'Z' to tell JS it's UTC.
                const utcString = log.ts.endsWith("Z") ? log.ts : log.ts + "Z";
                const time = new Date(utcString).toLocaleTimeString('en-IN', { 
                  hour: '2-digit', 
                  minute: '2-digit', 
                  second: '2-digit',
                  timeZone: 'Asia/Kolkata' // Forces Indian Standard Time
                });
                
                // Format the details object into a readable string
                const detailsText = log.details 
                  ? Object.entries(log.details).map(([k, v]) => `${k}: ${v}`).join(", ") 
                  : "—";

                // Color the event badges based on the event type
                let eventColor = "text-muted border-border/50";
                if (log.event.includes("created")) eventColor = "text-accent border-accent/50 bg-accent/10";
                if (log.event.includes("executed") || log.event.includes("approved")) eventColor = "text-ok border-ok/50 bg-ok/10";
                if (log.event.includes("reviewed")) eventColor = "text-warn border-warn/50 bg-warn/10";

                return (
                  <tr key={log.id} className="hover:bg-panel transition-colors">
                    <td className="px-4 py-3 font-mono text-xs">{time}</td>
                    <td className="px-4 py-3 font-mono">
                      <span className={log.actor === "system" || log.actor === "system_agent" ? "text-accent" : "text-ok"}>
                        {log.actor}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`rounded border px-2 py-0.5 text-xs font-bold uppercase ${eventColor}`}>
                        {log.event.replace(/_/g, " ")}
                      </span>
                    </td>
                    <td className="px-4 py-3 font-mono text-xs max-w-[200px] truncate" title={log.target || "N/A"}>
                      {log.target || "—"}
                    </td>
                    <td className="px-4 py-3 text-muted text-xs">
                      {detailsText}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}