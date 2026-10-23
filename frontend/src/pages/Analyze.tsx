import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Analyze() {
  const [url, setUrl] = useState("");
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);
  const nav = useNavigate();

  async function submitUrl() {
    const value = /^https?:\/\//i.test(url) ? url : "https://" + url;
    try { 
      new URL(value); 
    } catch { 
      return setErr("Enter a valid domain or URL"); 
    }
    
    setErr("");
    setLoading(true);
    
    // Simulate backend processing time
    setTimeout(() => {
      // We route to case 101 (our high-risk mock case) so it looks like it analyzed it!
      nav("/cases/101"); 
    }, 1500);
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-accent">Analyze Threat</h1>
        <p className="text-sm text-muted">Submit a URL or email to the agentic AI for investigation.</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* URL Panel */}
        <section className="rounded-xl border border-border/60 bg-panel/60 p-5 space-y-4">
          <h2 className="font-bold text-accent">Check a URL or domain</h2>
          <input 
            value={url} 
            onChange={(e) => setUrl(e.target.value)} 
            placeholder="acmepay-secure-login.com" 
            className="w-full rounded-lg border border-border/60 bg-black/30 px-3 py-2 font-mono text-sm focus:outline-none focus:border-accent" 
          />
          <button 
            onClick={submitUrl} 
            disabled={loading}
            className="w-full rounded-lg bg-accent px-4 py-2 font-bold text-black hover:bg-accent/80 disabled:opacity-50"
          >
            {loading ? "Investigating..." : "Investigate"}
          </button>
          {err && <p role="alert" className="text-sm text-danger">{err}</p>}
          
          <div className="pt-4 border-t border-border/30 text-xs text-muted">
            <p className="mb-2">Try a sample:</p>
            <button onClick={() => setUrl("acmepay-secure-login.com")} className="text-accent hover:underline block">Lookalike domain</button>
          </div>
        </section>

        {/* Email Panel */}
        <section className="rounded-xl border border-dashed border-border/60 bg-panel/20 p-5 flex flex-col justify-center items-center text-center space-y-3">
          <h2 className="font-bold text-accent">Check an email (.eml)</h2>
          <p className="text-sm text-muted">Drag and drop an email file here, or click to browse.</p>
          <input type="file" accept=".eml" className="text-sm text-muted file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-accent/10 file:text-accent hover:file:bg-accent/20" />
        </section>
      </div>
    </div>
  );
}