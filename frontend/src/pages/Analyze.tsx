import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Analyze() {
  const [url, setUrl] = useState("");
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);
  const [emailLoading, setEmailLoading] = useState(false);
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
    
    try {
      // 1. Send the URL to your real FastAPI backend
      await fetch("http://localhost:8000/api/analyze/url", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: value })
      });
      
      // 2. Wait for the AI Agent to finish
      setTimeout(() => {
        window.location.href = "/"; 
      }, 12000); 
      
    } catch (error) {
      setLoading(false);
      setErr("Failed to connect to the backend. Is it running?");
      console.error(error);
    }
  }

  async function handleFileUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    setErr("");
    setEmailLoading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      // 1. Send the file to your real FastAPI backend
      await fetch("http://localhost:8000/api/analyze/email", {
        method: "POST",
        body: formData,
        // Note: Do NOT set Content-Type header when sending FormData
      });
      
      // 2. Wait for the AI Agent to finish
      setTimeout(() => {
        window.location.href = "/"; 
      }, 12000); 
      
    } catch (error) {
      setEmailLoading(false);
      setErr("Failed to upload email. Is the backend running?");
      console.error(error);
    }
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
            placeholder="http://localhost:9000" 
            className="w-full rounded-lg border border-border/60 bg-black/30 px-3 py-2 font-mono text-sm focus:outline-none focus:border-accent" 
            disabled={loading || emailLoading}
          />
          <button 
            onClick={submitUrl} 
            disabled={loading || emailLoading}
            className="w-full rounded-lg bg-accent px-4 py-2 font-bold text-black hover:bg-accent/80 disabled:opacity-50"
          >
            {loading ? "Investigating (please wait ~12s)..." : "Investigate"}
          </button>
          {err && <p role="alert" className="text-sm text-danger">{err}</p>}
          
          <div className="pt-4 border-t border-border/30 text-xs text-muted">
            <p className="mb-2">Try a sample:</p>
            <button onClick={() => setUrl("http://localhost:9000")} className="text-accent hover:underline block" disabled={loading || emailLoading}>
              Local Fake Phishing Site
            </button>
          </div>
        </section>

        {/* Email Panel */}
        <section className="rounded-xl border border-dashed border-border/60 bg-panel/20 p-5 flex flex-col justify-center items-center text-center space-y-3">
          <h2 className="font-bold text-accent">Check an email (.eml)</h2>
          {emailLoading ? (
            <p className="text-sm text-accent animate-pulse font-bold">
              Analyzing email... (please wait ~12s)
            </p>
          ) : (
            <p className="text-sm text-muted">Drag and drop an email file here, or click to browse.</p>
          )}
          
          <input 
            type="file" 
            accept=".eml" 
            onChange={handleFileUpload}
            disabled={loading || emailLoading}
            className="text-sm text-muted file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-accent/10 file:text-accent hover:file:bg-accent/20 disabled:opacity-50" 
          />
        </section>
      </div>
    </div>
  );
}