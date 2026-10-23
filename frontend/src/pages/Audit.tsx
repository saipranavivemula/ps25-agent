export default function Audit() {
  // Mock audit data to show the judges
  const logs = [
    { id: 1, time: "10:05:22 AM", actor: "analyst_1", event: "ACTION_APPROVED", case: "acmepay-secure-login.com", details: "Block URL executed." },
    { id: 2, time: "10:02:10 AM", actor: "system_agent", event: "CASE_CREATED", case: "acmepay-secure-login.com", details: "Risk score 94. High risk detected." },
    { id: 3, time: "09:45:00 AM", actor: "analyst_2", event: "FALSE_POSITIVE", case: "invoice-update-portal.net", details: "Added to monitoring list. No block." },
  ];

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
            {logs.map((log) => (
              <tr key={log.id} className="hover:bg-panel transition-colors">
                <td className="px-4 py-3 font-mono text-xs">{log.time}</td>
                <td className="px-4 py-3 font-mono">
                  <span className={log.actor === "system_agent" ? "text-accent" : "text-ok"}>
                    {log.actor}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <span className="rounded border border-border/50 px-2 py-0.5 text-xs font-bold">
                    {log.event}
                  </span>
                </td>
                <td className="px-4 py-3 font-mono text-xs">{log.case}</td>
                <td className="px-4 py-3 text-muted">{log.details}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}