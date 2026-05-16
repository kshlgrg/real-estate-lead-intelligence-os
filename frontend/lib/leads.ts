export type LeadSource = "meta_ads" | "google_ads" | "website" | "landing_page" | "whatsapp" | "csv_upload";
export type LeadRoute = "hot" | "warm" | "nurture" | "manual_review" | "rejected";

export type ValidationSignal = {
  key: string;
  severity: "info" | "warning" | "critical";
  message: string;
};

export type Lead = {
  id: string;
  name: string;
  email: string;
  phone: string;
  source: LeadSource;
  location: string;
  budget: string;
  propertyType: string;
  message: string;
  language: string;
  timestamp: string;
  score: number;
  confidence: number;
  route: LeadRoute;
  salesperson: string;
  team: string;
  nextAction: string;
  intent: {
    buyerType: string;
    intent: string;
    luxuryLevel: string;
    timeline: string;
  };
  enrichment: {
    company: string;
    designation: string;
    areaCategory: string;
    domainQuality: string;
  };
  validation: ValidationSignal[];
  reasons: string[];
  propertyMatches: Array<{
    name: string;
    location: string;
    type: string;
    price: string;
    score: number;
    reasons: string[];
  }>;
};

export type Analytics = {
  total_leads: number;
  spam_rate: number;
  hot_leads: number;
  avg_confidence: number;
  source_quality: Record<string, { count: number; avg_score: number }>;
  scoring_distribution: Array<{ band: string; leads: number }>;
  funnel: Array<{ stage: string; value: number }>;
};

type ApiAnalyzedLead = {
  lead: {
    lead_id: string;
    name: string;
    email: string | null;
    phone: string | null;
    budget: string | null;
    preferred_location: string | null;
    property_type: string | null;
    message: string | null;
    source: LeadSource;
    timestamp: string;
    language: string;
  };
  enrichment: {
    company: string | null;
    designation: string | null;
    area_category: string;
    domain_quality: string;
  };
  validation: ValidationSignal[];
  intelligence: {
    score: number;
    confidence: number;
    reasons: string[];
    intent: Record<string, string>;
  };
  property_matches: Array<{
    name: string;
    location: string;
    property_type: string;
    price_label: string;
    match_score: number;
    reasons: string[];
  }>;
  assignment: {
    salesperson: string;
    team: string;
    route: LeadRoute;
    next_action: string;
  };
};

const apiBaseUrl =
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  (typeof window !== "undefined" ? `${window.location.origin}/_/backend` : "http://127.0.0.1:8001");

export const emptyAnalytics: Analytics = {
  total_leads: 0,
  spam_rate: 0,
  hot_leads: 0,
  avg_confidence: 0,
  source_quality: {},
  scoring_distribution: [
    { band: "0-2", leads: 0 },
    { band: "3-4", leads: 0 },
    { band: "5-6", leads: 0 },
    { band: "7-8", leads: 0 },
    { band: "9-10", leads: 0 }
  ],
  funnel: [
    { stage: "Ingested", value: 0 },
    { stage: "Validated", value: 0 },
    { stage: "Enriched", value: 0 },
    { stage: "Scored", value: 0 },
    { stage: "Routed", value: 0 },
    { stage: "Rejected", value: 0 }
  ]
};

export async function fetchLeads(): Promise<Lead[]> {
  const response = await fetch(`${apiBaseUrl}/api/leads`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Lead API returned ${response.status}`);
  }
  const data = (await response.json()) as ApiAnalyzedLead[];
  return data.map(toLead);
}

export async function fetchAnalytics(): Promise<Analytics> {
  const response = await fetch(`${apiBaseUrl}/api/leads/analytics`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Analytics API returned ${response.status}`);
  }
  return (await response.json()) as Analytics;
}

function toLead(item: ApiAnalyzedLead): Lead {
  return {
    id: item.lead.lead_id,
    name: item.lead.name,
    email: item.lead.email ?? "Not provided",
    phone: item.lead.phone ?? "Not provided",
    source: item.lead.source,
    location: item.lead.preferred_location ?? "Not provided",
    budget: item.lead.budget ?? "Not provided",
    propertyType: item.lead.property_type ?? "Not provided",
    message: item.lead.message ?? "",
    language: item.lead.language,
    timestamp: new Intl.DateTimeFormat(undefined, {
      dateStyle: "medium",
      timeStyle: "short"
    }).format(new Date(item.lead.timestamp)),
    score: item.intelligence.score,
    confidence: item.intelligence.confidence,
    route: item.assignment.route,
    salesperson: item.assignment.salesperson,
    team: item.assignment.team,
    nextAction: item.assignment.next_action,
    intent: {
      buyerType: item.intelligence.intent.buyer_type ?? "unknown",
      intent: item.intelligence.intent.intent ?? "unknown",
      luxuryLevel: item.intelligence.intent.luxury_level ?? "unknown",
      timeline: item.intelligence.intent.timeline ?? "unknown"
    },
    enrichment: {
      company: item.enrichment.company ?? "Not enriched",
      designation: item.enrichment.designation ?? "Not enriched",
      areaCategory: item.enrichment.area_category,
      domainQuality: item.enrichment.domain_quality
    },
    validation: item.validation,
    reasons: item.intelligence.reasons,
    propertyMatches: item.property_matches.map((match) => ({
      name: match.name,
      location: match.location,
      type: match.property_type,
      price: match.price_label,
      score: match.match_score,
      reasons: match.reasons
    }))
  };
}

export const automationSteps = [
  { title: "n8n webhook", detail: "Accepts only configured real webhooks", status: "healthy" },
  { title: "Validation gate", detail: "Uses submitted fields and configured providers", status: "healthy" },
  { title: "AI analysis", detail: "No mock LLM responses are generated", status: "active" },
  { title: "Decision engine", detail: "Routes only stored real leads", status: "active" },
  { title: "CRM + notify", detail: "Disabled until provider keys are configured", status: "queued" }
];

export const routeLabels: Record<LeadRoute, string> = {
  hot: "Hot",
  warm: "Warm",
  nurture: "Nurture",
  manual_review: "Review",
  rejected: "Rejected"
};
