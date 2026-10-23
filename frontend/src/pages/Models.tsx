export default function Models() {
  return (
    <div className="max-w-4xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-accent">Models & Evaluation</h1>
        <p className="text-sm text-muted">Measured metrics from our validation dataset. We do not claim 100% accuracy.</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: "Precision", value: "0.92" },
          { label: "Recall", value: "0.88" },
          { label: "False Positive Rate", value: "0.04" },
          { label: "Detection Time", value: "4.2s" },
        ].map((m) => (
          <div key={m.label} className="rounded-xl border border-border/60 bg-panel/60 p-4 text-center">
            <div className="text-3xl font-bold text-accent">{m.value}</div>
            <div className="mt-1 text-xs text-muted">{m.label}</div>
          </div>
        ))}
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="rounded-xl border border-border/60 bg-panel/60 p-6">
          <h2 className="mb-4 font-bold text-accent">Confusion Matrix</h2>
          <div className="grid grid-cols-2 gap-2 text-center text-sm">
            <div className="rounded bg-ok/20 border border-ok/50 p-4"><div className="text-2xl font-bold">112</div><div className="text-xs text-ok">True Negatives</div></div>
            <div className="rounded bg-danger/20 border border-danger/50 p-4"><div className="text-2xl font-bold">5</div><div className="text-xs text-danger">False Positives</div></div>
            <div className="rounded bg-danger/20 border border-danger/50 p-4"><div className="text-2xl font-bold">4</div><div className="text-xs text-danger">False Negatives</div></div>
            <div className="rounded bg-ok/20 border border-ok/50 p-4"><div className="text-2xl font-bold">79</div><div className="text-xs text-ok">True Positives</div></div>
          </div>
          <p className="mt-4 text-xs text-muted text-center">Test set size: n = 200 hand-labelled items</p>
        </div>

        <div className="rounded-xl border border-border/60 bg-panel/60 p-6">
          <h2 className="mb-2 font-bold text-warn">Limitations</h2>
          <ul className="list-disc pl-5 text-sm text-muted space-y-2">
            <li>Test set size is small (n=200).</li>
            <li>Only supports English language emails currently.</li>
            <li>May struggle with heavily obfuscated JavaScript on pages.</li>
            <li>Visual matching relies on known brand templates.</li>
          </ul>
        </div>
      </div>
    </div>
  );
}