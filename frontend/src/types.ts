// src/types.ts

export type Decision = "high" | "medium" | "low";
export type CaseStatus = "new" | "investigating" | "awaiting_review" | "actioned" | "dismissed";
export type ActionState = "simulated" | "pending_approval" | "executed" | "failed" | "rolled_back";

export interface Reason {
  signal: string;
  contribution: number;
  detail: string;
}

export interface TimelineItem {
  ts: string;
  stage: "monitor" | "investigate" | "verify" | "assess" | "respond";
  message: string;
}

export interface ActionItem {
  id: number;
  type: string;
  state: ActionState;
  payload: Record<string, unknown>;
}

export interface CaseBrief {
  id: number;
  created_at: string;
  source: string;
  target: string;
  target_type: "domain" | "url" | "email";
  status: CaseStatus;
  risk_score: number;
  decision: Decision;
}

export interface CaseFull extends CaseBrief {
  reasons: Reason[];
  summary: string;
  timeline: TimelineItem[];
  actions: ActionItem[];
  evidence: {
    domain?: any;
    cert?: any;
    dns?: any;
    whois?: any;
    email?: {
      from: string;
      subject: string;
      auth: Record<string, string>;
      links: string[];
      reply_to_mismatch?: boolean;
      text: string;
    };
    website?: {
      final_url?: string;
      title?: string;
      screenshot?: string;
      forms?: { action: string; hasPassword: boolean; posts_to_other_host: boolean }[];
    };
    nlp?: {
      probability: number;
      top_terms: { term: string; weight: number }[];
    };
    vision?: {
      brand: string | null;
      similarity: number;
      impersonation: boolean;
    };
  };
}

export interface Policy {
  high_threshold: number;
  medium_threshold: number;
  auto_actions_enabled: boolean;
  allowlist: string[];
}

export interface Stats {
  total: number;
  by_decision: Record<Decision, number>;
  median_detection_seconds: number;
  per_hour: { hour: string; count: number }[];
}