import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";
import type { Policy } from "../types";

export default function PolicyPage() {
  const { data: policy, isLoading } = useQuery({ queryKey: ["policy"], queryFn: api.policy });
  const [localPolicy, setLocalPolicy] = useState<Policy | null>(null);
  const [saved, setSaved] = useState(false);

  // Use local state if editing, otherwise use fetched data
  const p = localPolicy || policy;

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  if (isLoading || !p) return <div className="text-muted">Loading policy...</div>;

  const highPct = Math.round(p.high_threshold * 100);
  const medPct = Math.round(p.medium_threshold * 100);

  return (
    <div className="max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-accent">Policy & Thresholds</h1>
        <p className="text-sm text-muted">Adjust how the AI classifies risk and manage safe domains.</p>
      </div>

      {saved && (
        <div className="rounded-lg bg-ok/20 border border-ok text-ok px-4 py-2 text-sm font-bold">
          Policy saved successfully (Dry-run).
        </div>
      )}

      <div className="rounded-xl border border-border/60 bg-panel/60 p-6 space-y-8">
        
        {/* Visual Band Preview */}
        <div>
          <h2 className="mb-4 text-sm font-bold text-accent">Decision Bands Preview</h2>
          <div className="flex h-6 w-full overflow-hidden rounded-full border border-border/50">
            <div className="bg-ok flex items-center justify-center text-[10px] font-bold text-black" style={{ width: `${medPct}%` }}>LOW</div>
            <div className="bg-warn flex items-center justify-center text-[10px] font-bold text-black" style={{ width: `${highPct - medPct}%` }}>MED</div>
            <div className="bg-danger flex items-center justify-center text-[10px] font-bold text-black" style={{ width: `${100 - highPct}%` }}>HIGH</div>
          </div>
        </div>

        {/* Sliders */}
        <div className="space-y-6">
          <div>
            <label className="flex justify-between text-sm mb-2">
              <span>Medium Risk Threshold</span>
              <span className="font-mono text-warn">{p.medium_threshold.toFixed(2)}</span>
            </label>
            <input 
              type="range" min="0.30" max="0.90" step="0.01" 
              value={p.medium_threshold} 
              onChange={(e) => setLocalPolicy({ ...p, medium_threshold: parseFloat(e.target.value) })}
              className="w-full accent-warn" 
            />
          </div>
          
          <div>
            <label className="flex justify-between text-sm mb-2">
              <span>High Risk Threshold</span>
              <span className="font-mono text-danger">{p.high_threshold.toFixed(2)}</span>
            </label>
            <input 
              type="range" min="0.40" max="0.99" step="0.01" 
              value={p.high_threshold} 
              onChange={(e) => setLocalPolicy({ ...p, high_threshold: parseFloat(e.target.value) })}
              className="w-full accent-danger" 
            />
          </div>
        </div>

        {/* Allowlist */}
        <div>
          <h2 className="mb-3 text-sm font-bold text-accent">Global Allowlist</h2>
          <div className="flex flex-wrap gap-2">
            {p.allowlist.map(domain => (
              <span key={domain} className="rounded bg-black/40 border border-border/50 px-3 py-1 text-sm font-mono flex items-center gap-2">
                {domain}
                <button className="text-muted hover:text-danger">&times;</button>
              </span>
            ))}
            <button className="rounded border border-dashed border-muted text-muted hover:text-accent hover:border-accent px-3 py-1 text-sm">
              + Add Domain
            </button>
          </div>
        </div>

        <div className="pt-4 border-t border-border/30 flex justify-end">
          <button onClick={handleSave} className="rounded-lg bg-accent px-6 py-2 font-bold text-black hover:bg-accent/80">
            Save Policy
          </button>
        </div>
      </div>
    </div>
  );
}