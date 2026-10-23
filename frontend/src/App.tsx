import { useState } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, NavLink, Outlet } from "react-router-dom";
import { LayoutDashboard, Search, Inbox, Sliders, Brain, ScrollText, MonitorPlay } from "lucide-react";
import Dashboard from "./pages/Dashboard";
import CaseDetail from "./pages/CaseDetail";
import Review from "./pages/Review";
import Analyze from "./pages/Analyze";
import PolicyPage from "./pages/PolicyPage";
import Audit from "./pages/Audit";
import Models from "./pages/Models";

const qc = new QueryClient({
  defaultOptions: { queries: { staleTime: 5000, retry: 1 } }
});

const NAV = [
  { to: "/", label: "Dashboard", Icon: LayoutDashboard },
  { to: "/analyze", label: "Analyze", Icon: Search },
  { to: "/review", label: "Review Queue", Icon: Inbox },
  { to: "/policy", label: "Policy", Icon: Sliders },
  { to: "/models", label: "Models", Icon: Brain },
  { to: "/audit", label: "Audit Log", Icon: ScrollText },
];

function Layout() {
  // 👇 Presentation Mode state
  const [isPresentation, setIsPresentation] = useState(false);

  return (
    // 👇 Apply text-lg and wider spacing if Presentation Mode is on
    <div className={`flex h-screen bg-bg text-foreground ${isPresentation ? "text-lg" : "text-sm"}`}>
      <aside className="w-56 shrink-0 border-r border-border/50 bg-black/30 p-4">
        <div className="mb-6 font-extrabold text-accent text-xl">PhishGuard Agent</div>
        <nav className="space-y-1">
          {NAV.map(({ to, label, Icon }) => (
            <NavLink 
              key={to} 
              to={to} 
              end={to === "/"} 
              className={({ isActive }) => 
                "flex items-center gap-2 rounded-lg px-3 py-2 transition-colors " + 
                (isActive ? "bg-panel text-accent font-bold" : "text-muted hover:bg-panel/60")
              }
            >
              <Icon size={18} aria-hidden /> {label}
            </NavLink>
          ))}
        </nav>
      </aside>

      <main className="flex-1 overflow-auto flex flex-col">
        <header className="flex items-center justify-between border-b border-border/40 px-6 py-3 shrink-0">
          <span className="text-muted">Autonomous phishing intelligence and response</span>
          
          <div className="flex items-center gap-4">
            {/* 👇 The Presentation Mode Toggle */}
            <button 
              onClick={() => setIsPresentation(!isPresentation)}
              className={`flex items-center gap-2 rounded border px-3 py-1 text-xs font-bold transition-colors ${
                isPresentation ? "border-accent text-accent bg-accent/10" : "border-muted text-muted hover:border-accent"
              }`}
            >
              <MonitorPlay size={14} /> {isPresentation ? "Presentation ON" : "Presentation OFF"}
            </button>

            <span className="rounded-full border border-ok text-ok px-3 py-1 text-xs font-bold">
              DRY-RUN: actions need approval
            </span>
          </div>
        </header>
        
        <div className="p-6 flex-1">
          <Outlet />
        </div>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={qc}>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/analyze" element={<Analyze />} />
            <Route path="/cases/:id" element={<CaseDetail />} />
            <Route path="/review" element={<Review />} />
            <Route path="/policy" element={<PolicyPage />} />
            <Route path="/models" element={<Models />} />
            <Route path="/audit" element={<Audit />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}