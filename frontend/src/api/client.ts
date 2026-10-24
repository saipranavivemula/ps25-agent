import type { CaseBrief, CaseFull, Policy, Stats } from "../types";
import mockCases from "../mocks/cases.json";
import mockStats from "../mocks/stats.json";
import mockPolicy from "../mocks/policy.json";

const BASE = import.meta.env.VITE_API_URL ?? "";
const KEY = import.meta.env.VITE_API_KEY ?? "";
const IS_MOCK = import.meta.env.VITE_MOCK === "true"; // 👈 This is the magic switch

// Fake delay to simulate network request
const delay = (ms: number) => new Promise((res) => setTimeout(res, ms));

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const res = await fetch(BASE + path, {
    ...init,
    headers: {
      "X-API-Key": KEY,
      ...(init.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
      ...init.headers,
    },
  });
  if (!res.ok) throw new Error((await res.text()) || "HTTP " + res.status);
  return res.json() as Promise<T>;
}

export const api = {
  stats: async (): Promise<Stats> => {
    if (IS_MOCK) { await delay(400); return mockStats as Stats; }
    return request<Stats>("/api/stats");
  },

  cases: async (qs = ""): Promise<{ total: number; items: CaseBrief[] }> => {
    if (IS_MOCK) { await delay(500); return { total: mockCases.length, items: mockCases as CaseBrief[] }; }
    
    // Fetch the raw list from backend and wrap it so the UI is happy
    const items = await request<CaseBrief[]>("/api/cases" + qs);
    return { total: items.length, items: items };
  },

  case: async (id: number): Promise<CaseFull> => {
    if (IS_MOCK) { 
      await delay(400); 
      const found = mockCases.find((c) => c.id === id);
      if (!found) throw new Error("Case not found");
      return found as unknown as CaseFull; 
    }
    return request<CaseFull>("/api/cases/" + id);
  },

  policy: async (): Promise<Policy> => {
    if (IS_MOCK) { await delay(200); return mockPolicy as Policy; }
    return request<Policy>("/api/policy");
  },

  // 👇 NEW ADDITIONS FOR ACTIONS AND REVIEWS 👇
  actions: async (): Promise<any[]> => {
    return request<any[]>("/api/actions");
  },

  approveAction: async (id: number): Promise<any> => {
    return request<any>(`/api/actions/${id}/approve`, { method: "POST" });
  },

  reviewCase: async (id: number, verdict: string): Promise<any> => {
    return request<any>(`/api/cases/${id}/review`, { 
      method: "POST", 
      body: JSON.stringify({ verdict, note: "Analyst review", analyst: "admin" }) 
    });
  },

  // 👇 NEW ADDITION FOR POLICY UPDATES 👇
  updatePolicy: async (data: any): Promise<any> => {
    return request<any>("/api/policy", { 
      method: "PUT", 
      body: JSON.stringify(data) 
    });
  },

  getModelMetrics: async (): Promise<any> => {
    return request<any>("/api/models/metrics");
  },

  // 👇 NEW ADDITION FOR AUDIT LOGS 👇
  auditLog: async (): Promise<any[]> => {
    return request<any[]>("/api/audit");
  },
};