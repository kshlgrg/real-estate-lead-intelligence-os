export type SourceType =
  | "blog"
  | "linkedin"
  | "press_release"
  | "case_study"
  | "pricing"
  | "jobs"
  | "changelog"
  | "github"
  | "youtube"
  | "reddit"
  | "other";

export type Topic =
  | "pricing"
  | "product_launch"
  | "ai_adoption"
  | "enterprise_push"
  | "hiring"
  | "funding"
  | "partnerships"
  | "market_expansion"
  | "customer_proof"
  | "security"
  | "positioning";

export type Competitor = {
  competitor_id: string;
  name: string;
  website: string | null;
  segment: string;
  tracked_keywords: string[];
};

export type IntelligenceSignal = {
  signal_type: string;
  description: string;
  evidence: string[];
  confidence: number;
};

export type ContentItem = {
  content: {
    content_id: string;
    competitor_id: string;
    source: SourceType;
    url: string;
    title: string;
    body: string;
    published_at: string;
    author: string | null;
  };
  competitor_name: string;
  analysis: {
    summary: string;
    key_points: string[];
    topics: Topic[];
    tone: "neutral" | "assertive" | "expansionary" | "promotional" | "defensive" | "investor_focused";
    sentiment: "positive" | "neutral" | "negative";
    priority: number;
    priority_reason: string;
    confidence: number;
    recommended_action: string;
  };
  strategic_signals: IntelligenceSignal[];
};

export type Analytics = {
  monitored_competitors: number;
  total_items: number;
  high_priority_items: number;
  avg_confidence: number;
  topic_heatmap: Array<{ topic: string; mentions: number }>;
  source_mix: Array<{ source: string; items: number }>;
  signal_mix: Array<{ signal: string; items: number }>;
  competitor_activity: Array<{ competitor: string; items: number; avg_priority: number }>;
  priority_distribution: Array<{ band: string; items: number }>;
  pipeline: Array<{ stage: string; value: number }>;
};

export type Digest = {
  items_analyzed: number;
  top_strategic_developments: Array<{
    competitor: string;
    title: string;
    priority: number;
    summary: string;
    signals: string[];
  }>;
  most_aggressive_competitor: string | null;
  emerging_themes: Array<{ topic: string; mentions: number }>;
  recommended_actions: string[];
  low_confidence_items: Array<{ title: string; confidence: number }>;
};

export type IngestPayload = {
  competitor_id: string;
  source: SourceType;
  url: string;
  title: string;
  body: string;
  author?: string;
};

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8001";

export const emptyAnalytics: Analytics = {
  monitored_competitors: 0,
  total_items: 0,
  high_priority_items: 0,
  avg_confidence: 0,
  topic_heatmap: [],
  source_mix: [],
  signal_mix: [],
  competitor_activity: [],
  priority_distribution: [
    { band: "0-3", items: 0 },
    { band: "4-6", items: 0 },
    { band: "7-8", items: 0 },
    { band: "9-10", items: 0 }
  ],
  pipeline: [
    { stage: "Discovered", value: 0 },
    { stage: "Deduplicated", value: 0 },
    { stage: "Analyzed", value: 0 },
    { stage: "High Priority", value: 0 },
    { stage: "Actionable", value: 0 }
  ]
};

export const emptyDigest: Digest = {
  items_analyzed: 0,
  top_strategic_developments: [],
  most_aggressive_competitor: null,
  emerging_themes: [],
  recommended_actions: [],
  low_confidence_items: []
};

export async function fetchCompetitors(): Promise<Competitor[]> {
  return apiGet<Competitor[]>("/api/competitors").catch(() => demoCompetitors);
}

export async function fetchContent(): Promise<ContentItem[]> {
  return apiGet<ContentItem[]>("/api/content").catch(() => demoContent);
}

export async function fetchAnalytics(): Promise<Analytics> {
  return apiGet<Analytics>("/api/analytics").catch(() => demoAnalytics);
}

export async function fetchDigest(): Promise<Digest> {
  return apiGet<Digest>("/api/digest?days=30").catch(() => demoDigest);
}

export async function createCompetitor(competitor: Competitor): Promise<Competitor> {
  return apiPost<Competitor>("/api/competitors", competitor);
}

export async function ingestContent(payload: IngestPayload): Promise<ContentItem> {
  return apiPost<ContentItem>("/api/content", {
    ...payload,
    content_id: `${payload.competitor_id}-${Date.now()}`,
    published_at: new Date().toISOString()
  });
}

async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, { cache: "no-store" });
  if (!response.ok) throw new Error(`API returned ${response.status}`);
  return (await response.json()) as T;
}

async function apiPost<T>(path: string, payload: object): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!response.ok) throw new Error(`API returned ${response.status}`);
  return (await response.json()) as T;
}

export function formatTopic(topic: string) {
  return topic.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

export function formatDate(value: string) {
  return new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

export const demoCompetitors: Competitor[] = [
  {
    competitor_id: "acme",
    name: "Acme AI",
    website: "https://acme.example",
    segment: "AI automation",
    tracked_keywords: ["agents", "enterprise", "pricing"]
  },
  {
    competitor_id: "contoso",
    name: "Contoso Growth",
    website: "https://contoso.example",
    segment: "B2B marketing automation",
    tracked_keywords: ["case study", "enterprise", "workflow"]
  }
];

export const demoContent: ContentItem[] = [
  {
    content: {
      content_id: "acme-001",
      competitor_id: "acme",
      source: "blog",
      url: "https://acme.example/blog/enterprise-agents",
      title: "Acme launches enterprise AI agents with new pricing",
      body: "Acme announced enterprise AI agents, SSO controls, procurement workflows, and a new pricing package for large customers.",
      published_at: "2026-05-15T10:00:00+05:30",
      author: "Acme Newsroom"
    },
    competitor_name: "Acme AI",
    analysis: {
      summary: "Acme launched enterprise AI agents with SSO controls, procurement workflows, and new pricing for larger customers.",
      key_points: ["Enterprise controls are now part of the pitch.", "Pricing language suggests a packaging shift."],
      topics: ["pricing", "product_launch", "ai_adoption", "enterprise_push", "security", "positioning"],
      tone: "expansionary",
      sentiment: "positive",
      priority: 10,
      priority_reason: "Detected pricing, product launch, and enterprise push.",
      confidence: 0.95,
      recommended_action: "Review positioning, packaging, and sales objection handling against this pricing move."
    },
    strategic_signals: [
      {
        signal_type: "pricing_change",
        description: "Pricing or packaging change detected.",
        evidence: ["Acme launches enterprise AI agents with new pricing"],
        confidence: 0.82
      },
      {
        signal_type: "enterprise_push",
        description: "Competitor is emphasizing enterprise buyers and larger customer controls.",
        evidence: ["SSO controls and procurement workflows are featured in the announcement."],
        confidence: 0.78
      }
    ]
  },
  {
    content: {
      content_id: "contoso-001",
      competitor_id: "contoso",
      source: "case_study",
      url: "https://contoso.example/customers/ops-team",
      title: "Contoso publishes workflow automation case study",
      body: "The case study claims a mid-market operations team reduced manual campaign reporting by 42 percent after adopting Contoso workflows.",
      published_at: "2026-05-14T12:00:00+05:30",
      author: "Contoso Marketing"
    },
    competitor_name: "Contoso Growth",
    analysis: {
      summary: "Contoso is using customer proof to support workflow automation positioning for mid-market operations teams.",
      key_points: ["Customer proof is now central to the campaign.", "Manual reporting reduction is the main ROI claim."],
      topics: ["ai_adoption", "customer_proof", "positioning"],
      tone: "promotional",
      sentiment: "positive",
      priority: 7,
      priority_reason: "Detected customer proof and automation positioning.",
      confidence: 0.76,
      recommended_action: "Compare AI automation claims and update product proof points where needed."
    },
    strategic_signals: [
      {
        signal_type: "strategic_shift",
        description: "Narrative is moving from feature description toward ROI-backed customer proof.",
        evidence: ["The case study includes a 42 percent reduction claim."],
        confidence: 0.69
      }
    ]
  }
];

export const demoAnalytics: Analytics = {
  monitored_competitors: 2,
  total_items: 2,
  high_priority_items: 1,
  avg_confidence: 0.86,
  topic_heatmap: [
    { topic: "ai_adoption", mentions: 2 },
    { topic: "positioning", mentions: 2 },
    { topic: "pricing", mentions: 1 },
    { topic: "enterprise_push", mentions: 1 },
    { topic: "customer_proof", mentions: 1 }
  ],
  source_mix: [
    { source: "blog", items: 1 },
    { source: "case_study", items: 1 }
  ],
  signal_mix: [
    { signal: "pricing_change", items: 1 },
    { signal: "enterprise_push", items: 1 },
    { signal: "strategic_shift", items: 1 }
  ],
  competitor_activity: [
    { competitor: "Acme AI", items: 1, avg_priority: 10 },
    { competitor: "Contoso Growth", items: 1, avg_priority: 7 }
  ],
  priority_distribution: [
    { band: "0-3", items: 0 },
    { band: "4-6", items: 0 },
    { band: "7-8", items: 1 },
    { band: "9-10", items: 1 }
  ],
  pipeline: [
    { stage: "Discovered", value: 2 },
    { stage: "Deduplicated", value: 2 },
    { stage: "Analyzed", value: 2 },
    { stage: "High Priority", value: 1 },
    { stage: "Actionable", value: 2 }
  ]
};

export const demoDigest: Digest = {
  items_analyzed: 2,
  top_strategic_developments: [
    {
      competitor: "Acme AI",
      title: "Acme launches enterprise AI agents with new pricing",
      priority: 10,
      summary: "Acme launched enterprise AI agents with SSO controls, procurement workflows, and new pricing for larger customers.",
      signals: ["Pricing or packaging change detected.", "Competitor is emphasizing enterprise buyers and larger customer controls."]
    }
  ],
  most_aggressive_competitor: "Acme AI",
  emerging_themes: [
    { topic: "ai_adoption", mentions: 2 },
    { topic: "positioning", mentions: 2 },
    { topic: "pricing", mentions: 1 }
  ],
  recommended_actions: [
    "Review positioning, packaging, and sales objection handling against this pricing move.",
    "Compare AI automation claims and update product proof points where needed."
  ],
  low_confidence_items: []
};
