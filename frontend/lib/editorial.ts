export type EditorialSource =
  | "techcrunch"
  | "hacker_news"
  | "reddit"
  | "google_news"
  | "google_trends"
  | "rss"
  | "linkedin"
  | "x"
  | "github"
  | "product_hunt"
  | "youtube"
  | "newsletter"
  | "manual";

export type AudienceSegment = "founder" | "marketer" | "investor" | "engineer" | "operator" | "general";

export type StoryInput = {
  story_id: string;
  source: EditorialSource;
  url: string;
  title: string;
  body: string;
  published_at: string;
  author?: string | null;
  engagement: number;
  credibility: number;
};

export type AudienceProfile = {
  profile_id: string;
  name: string;
  segments: AudienceSegment[];
  interests: string[];
  avoided_topics: string[];
  tone: "analytical" | "conversational" | "contrarian" | "founder-focused" | "investor-focused";
};

export type EditorialMemoryItem = {
  theme: string;
  last_covered_at: string;
  engagement_score: number;
};

export type NewsletterAngle = {
  title: string;
  angle_type: "analytical" | "contrarian" | "operator" | "founder" | "investor";
  score: number;
  originality: number;
  relevance: number;
  engagement_potential: number;
  rationale: string;
};

export type DraftIntro = {
  headline: string;
  body: string;
  tone: string;
  source_story_ids: string[];
};

export type ThemeCluster = {
  theme_id: string;
  title: string;
  summary: string;
  stories: StoryInput[];
  story_count: number;
  trend_velocity: number;
  audience_relevance: number;
  novelty_score: number;
  saturation_score: number;
  credibility_score: number;
  emotion: "curiosity" | "excitement" | "skepticism" | "urgency";
  explainability: string[];
  narrative_frames: Array<{
    frame_type: "optimistic" | "skeptical" | "founder" | "operator" | "investor";
    headline: string;
  }>;
  angles: NewsletterAngle[];
};

export type NewsletterPlan = {
  generated_at: string;
  audience: AudienceProfile;
  themes: ThemeCluster[];
  top_angles: NewsletterAngle[];
  draft_intro: DraftIntro | null;
  source_mix: Record<string, number>;
  export_targets: string[];
  automation_steps: string[];
  explainability: string[];
};

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8001";

export const demoAudience: AudienceProfile = {
  profile_id: "weekly-ai-operators",
  name: "AI operators, founders, and strategists",
  segments: ["founder", "operator"],
  interests: ["ai agents", "automation", "operations", "workflow", "startups"],
  avoided_topics: ["generic productivity tips"],
  tone: "analytical"
};

const now = "2026-05-15T09:00:00+05:30";

export const demoStories: StoryInput[] = [
  {
    story_id: "tc-agents-ops",
    source: "techcrunch",
    url: "https://example.com/ai-agents-ops",
    title: "AI agents move from demos into operations workflows",
    body: "Founders are deploying AI agents for procurement, support triage, and workflow orchestration. Operators say the hardest part is redesigning broken processes before automation scales.",
    published_at: now,
    author: "Tech desk",
    engagement: 86,
    credibility: 0.84
  },
  {
    story_id: "hn-runtime",
    source: "hacker_news",
    url: "https://example.com/agent-runtime",
    title: "Open-source agent runtimes focus on workflow reliability",
    body: "Engineers are debating AI agent reliability, orchestration, tool permissions, and human review loops for production workflows.",
    published_at: "2026-05-14T12:00:00+05:30",
    author: "HN thread",
    engagement: 63,
    credibility: 0.76
  },
  {
    story_id: "reddit-ops",
    source: "reddit",
    url: "https://example.com/operator-thread",
    title: "Operators warn AI automation exposes messy internal processes",
    body: "A Reddit discussion says automation projects fail when companies skip process mapping and automate unclear ownership.",
    published_at: "2026-05-13T17:00:00+05:30",
    author: "Ops community",
    engagement: 51,
    credibility: 0.64
  },
  {
    story_id: "github-runtime",
    source: "github",
    url: "https://example.com/open-source-agents",
    title: "Developer tools consolidate around agent runtime standards",
    body: "Open-source AI infrastructure projects are converging on runtime protocols, observability, and test harnesses for agent systems.",
    published_at: "2026-05-15T07:30:00+05:30",
    author: "Maintainer notes",
    engagement: 74,
    credibility: 0.81
  },
  {
    story_id: "google-trends",
    source: "google_trends",
    url: "https://example.com/agent-search-trends",
    title: "Search interest rises for AI workflow automation",
    body: "Search data shows rising interest in AI workflow automation, agent orchestration, and back-office automation platforms.",
    published_at: "2026-05-12T08:00:00+05:30",
    author: "Trends monitor",
    engagement: 58,
    credibility: 0.79
  }
];

export const demoMemory: EditorialMemoryItem[] = [
  {
    theme: "AI productivity tools",
    last_covered_at: "2026-05-01T08:00:00+05:30",
    engagement_score: 0.52
  }
];

export async function fetchNewsletterPlan(): Promise<NewsletterPlan> {
  try {
    const response = await fetch(`${apiBaseUrl}/api/newsletter-plan`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        audience: demoAudience,
        stories: demoStories,
        memory: demoMemory
      }),
      cache: "no-store"
    });

    if (!response.ok) {
      throw new Error(`Newsletter API returned ${response.status}`);
    }

    return (await response.json()) as NewsletterPlan;
  } catch {
    return demoPlan;
  }
}

export const sourceLabels: Record<string, string> = {
  techcrunch: "TechCrunch",
  hacker_news: "Hacker News",
  reddit: "Reddit",
  google_news: "Google News",
  google_trends: "Google Trends",
  rss: "RSS",
  linkedin: "LinkedIn",
  x: "X",
  github: "GitHub",
  product_hunt: "Product Hunt",
  youtube: "YouTube",
  newsletter: "Newsletter",
  manual: "Manual"
};

export const demoPlan: NewsletterPlan = {
  generated_at: now,
  audience: demoAudience,
  themes: [
    {
      theme_id: "ai-replacing-operational-workflows",
      title: "AI replacing operational workflows",
      summary: "5 stories from GitHub, Google Trends, Hacker News, Reddit, and TechCrunch point to AI replacing operational workflows as a useful editorial theme.",
      stories: demoStories,
      story_count: 5,
      trend_velocity: 10,
      audience_relevance: 10,
      novelty_score: 7.3,
      saturation_score: 3.5,
      credibility_score: 7.7,
      emotion: "skepticism",
      explainability: [
        "Trend velocity is increasing across multiple recent stories.",
        "Audience alignment is high based on profile interests and segment language.",
        "Novelty remains usable because the angle is not fully saturated.",
        "Source credibility is strong enough for a grounded editorial draft."
      ],
      narrative_frames: [
        { frame_type: "operator", headline: "The workflow is the story, not the model." },
        { frame_type: "skeptical", headline: "The weak point is execution quality." },
        { frame_type: "founder", headline: "The winners package reliability, not novelty." },
        { frame_type: "investor", headline: "Budget is moving toward invisible operations capacity." },
        { frame_type: "optimistic", headline: "Automation can remove coordination drag when the process is real." }
      ],
      angles: [
        {
          title: "Why most AI automation stories are missing the operational failure mode.",
          angle_type: "contrarian",
          score: 9.2,
          originality: 8.2,
          relevance: 10,
          engagement_potential: 10,
          rationale: "Grounded in 5 source stories about AI replacing operational workflows."
        },
        {
          title: "Most companies automate workflows before fixing broken processes.",
          angle_type: "operator",
          score: 9,
          originality: 7.5,
          relevance: 10,
          engagement_potential: 9.8,
          rationale: "The strongest operator frame from this week's source cluster."
        },
        {
          title: "AI agents are creating a new layer of invisible operations teams.",
          angle_type: "analytical",
          score: 8.7,
          originality: 7.2,
          relevance: 9.5,
          engagement_potential: 9.1,
          rationale: "A clear synthesis angle for founders and operators."
        },
        {
          title: "The founder playbook hidden inside this week's AI operations trend.",
          angle_type: "founder",
          score: 8.3,
          originality: 7,
          relevance: 9,
          engagement_potential: 8.5,
          rationale: "Useful when the newsletter needs a founder-facing lesson."
        },
        {
          title: "What AI operations reveals about the next software budget line.",
          angle_type: "investor",
          score: 8,
          originality: 6.8,
          relevance: 8.4,
          engagement_potential: 8.5,
          rationale: "Investor frame for market structure and budget migration."
        }
      ]
    }
  ],
  top_angles: [],
  draft_intro: {
    headline: "Why most AI automation stories are missing the operational failure mode.",
    body: "This week, AI agents stopped looking like demos and started looking like an operations question. The signal is coming from startup coverage, developer debates, search interest, and operator threads. The useful question is not whether the technology works in isolation, but whether teams understand the workflow well enough to automate it without scaling the mess.",
    tone: "analytical",
    source_story_ids: ["tc-agents-ops", "hn-runtime", "reddit-ops", "github-runtime", "google-trends"]
  },
  source_mix: {
    techcrunch: 1,
    hacker_news: 1,
    reddit: 1,
    github: 1,
    google_trends: 1
  },
  export_targets: ["Notion", "Google Docs"],
  automation_steps: ["Fetch trends", "Deduplicate", "Cluster themes", "Score relevance", "Generate angles", "Draft intro"],
  explainability: [
    "Themes are ranked by trend velocity, audience fit, novelty, saturation, and source credibility.",
    "Angles are generated only from submitted story titles and bodies."
  ]
};

demoPlan.top_angles = demoPlan.themes[0].angles;
