"use client";

import { useEffect, useMemo, useState } from "react";
import {
  Bell,
  Bot,
  Building2,
  CheckCircle2,
  ExternalLink,
  FileText,
  Flame,
  Github,
  Globe2,
  Home,
  Inbox,
  LayoutDashboard,
  Lightbulb,
  Link2,
  ListFilter,
  Mail,
  Network,
  Newspaper,
  Radar,
  RadioTower,
  Search,
  ShieldCheck,
  Sparkles,
  Target,
  TrendingUp,
  UsersRound
} from "lucide-react";

import {
  Analytics,
  ContentItem,
  Digest,
  SourceType,
  emptyAnalytics,
  emptyDigest,
  fetchAnalytics,
  fetchContent,
  fetchDigest,
  formatDate,
  formatTopic
} from "@/lib/intelligence";

const sourceLabels: Record<SourceType, string> = {
  blog: "Blog",
  linkedin: "LinkedIn",
  press_release: "Press",
  case_study: "Case Study",
  pricing: "Pricing",
  jobs: "Jobs",
  changelog: "Changelog",
  github: "GitHub",
  youtube: "YouTube",
  reddit: "Reddit",
  other: "Other"
};

const navItems = [
  { label: "Submission Systems", icon: LayoutDashboard, href: "#submission-systems", active: true },
  { label: "Intelligence Feed", icon: Inbox, href: "#intelligence-feed" },
  { label: "Strategic Signals", icon: Radar, href: "#strategic-signals" },
  { label: "Digests", icon: Mail, href: "#digest" },
  { label: "Automations", icon: RadioTower, href: "#automations" }
];

const repoUrl = "https://github.com/kshlgrg/real-estate-lead-intelligence-os";

const submissionLinks = [
  { label: "GitHub repo", href: repoUrl, icon: Github },
  { label: "Problem docs", href: `${repoUrl}/tree/main/docs`, icon: FileText },
  { label: "n8n workflows", href: `${repoUrl}/tree/main/workflows`, icon: RadioTower },
  { label: "Screenshots", href: `${repoUrl}/tree/main/screenshots`, icon: ExternalLink }
];

const systems = [
  {
    label: "Problem A",
    title: "Real estate lead qualification",
    icon: Home,
    detail: "Webhook intake, validation, enrichment, 1-10 scoring, property matching, and sales routing.",
    doc: `${repoUrl}/blob/main/docs/problem-a-real-estate-lead-qualification.md`,
    metric: "Hot lead routing + review gates"
  },
  {
    label: "Problem B",
    title: "Competitor content monitoring",
    icon: Building2,
    detail: "Scheduled monitoring, dedupe, topic classification, strategic signals, and daily digest.",
    doc: `${repoUrl}/blob/main/docs/problem-b-competitor-content-monitoring.md`,
    metric: "Live dashboard below"
  },
  {
    label: "Problem C",
    title: "Newsletter ideation engine",
    icon: Newspaper,
    detail: "Trend ingestion, theme clustering, novelty scoring, five angles, and a source-grounded intro draft.",
    doc: `${repoUrl}/blob/main/docs/problem-c-newsletter-ideation-engine.md`,
    metric: "Weekly editor brief"
  }
];

function cx(...classes: Array<string | false | null | undefined>) {
  return classes.filter(Boolean).join(" ");
}

function priorityColor(priority: number) {
  if (priority >= 9) return "#be123c";
  if (priority >= 7) return "#d97706";
  return "#0d9488";
}

function KpiCard({
  label,
  value,
  detail,
  icon: Icon,
  tone
}: {
  label: string;
  value: string;
  detail: string;
  icon: typeof UsersRound;
  tone: "navy" | "teal" | "amber" | "rose";
}) {
  const toneClass = {
    navy: "border-slate-200 bg-slate-100 text-navy",
    teal: "border-teal-100 bg-teal-50 text-teal",
    amber: "border-amber-100 bg-amber-50 text-amber",
    rose: "border-rose-100 bg-rose-50 text-rose-700"
  }[tone];

  return (
    <section className="rounded-lg border border-line bg-white p-4 shadow-panel">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase text-slate">{label}</p>
          <p className="mt-2 text-2xl font-semibold text-ink">{value}</p>
        </div>
        <div className={cx("rounded-md border p-2", toneClass)}>
          <Icon size={18} strokeWidth={2.2} />
        </div>
      </div>
      <p className="mt-3 text-xs leading-5 text-slate">{detail}</p>
    </section>
  );
}

function Sidebar() {
  return (
    <aside className="hidden min-h-screen w-[252px] shrink-0 bg-navy px-4 py-5 text-white lg:block">
      <div className="flex items-center gap-3 px-2">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-teal text-white">
          <Target size={20} strokeWidth={2.4} />
        </div>
        <div>
          <p className="text-sm font-semibold">MarketIntel OS</p>
          <p className="text-xs text-slate-300">Competitive AI monitor</p>
        </div>
      </div>
      <nav className="mt-8 space-y-1">
        {navItems.map((item) => (
          <a
            key={item.label}
            href={item.href}
            className={cx(
              "flex h-10 w-full items-center gap-3 rounded-md px-3 text-sm transition",
              item.active ? "bg-white text-navy" : "text-slate-300 hover:bg-white/10 hover:text-white"
            )}
          >
            <item.icon size={17} strokeWidth={2} />
            {item.label}
          </a>
        ))}
      </nav>
      <div className="mt-8 rounded-lg border border-white/10 bg-white/5 p-4">
        <div className="flex items-center gap-2 text-sm font-semibold">
          <ShieldCheck size={16} />
          Grounded Analysis
        </div>
        <p className="mt-2 text-xs leading-5 text-slate-300">
          Every insight keeps source content, confidence, and evidence attached.
        </p>
      </div>
    </aside>
  );
}

function SubmissionControlCenter({ activeSystem, setActiveSystem }: { activeSystem: number; setActiveSystem: (value: number) => void }) {
  const system = systems[activeSystem];
  return (
    <section id="submission-systems" className="rounded-lg border border-line bg-white p-4 shadow-panel">
      <div className="flex flex-col gap-3 xl:flex-row xl:items-start xl:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase text-slate">Submission control center</p>
          <h2 className="mt-1 text-xl font-semibold text-ink">Three assignment problems, one reviewable package</h2>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate">
            The live page previews the competitor-monitoring operator dashboard. The buttons below jump to the repo evidence for all three systems: docs, n8n exports, screenshots, API commands, tests, and production notes.
          </p>
        </div>
        <div className="grid gap-2 sm:grid-cols-2 xl:min-w-[460px]">
          {submissionLinks.map((link) => (
            <a
              key={link.label}
              href={link.href}
              target="_blank"
              rel="noreferrer"
              className="flex h-10 items-center justify-between rounded-lg border border-line bg-mist px-3 text-sm font-semibold text-ink transition hover:border-teal hover:bg-teal-50"
            >
              <span className="flex items-center gap-2"><link.icon size={16} />{link.label}</span>
              <ExternalLink size={14} />
            </a>
          ))}
        </div>
      </div>
      <div className="mt-4 grid gap-3 lg:grid-cols-[280px_minmax(0,1fr)]">
        <div className="grid gap-2">
          {systems.map((item, index) => (
            <button
              key={item.title}
              onClick={() => setActiveSystem(index)}
              className={cx(
                "flex min-h-16 items-center gap-3 rounded-lg border px-3 py-3 text-left transition",
                activeSystem === index ? "border-teal bg-teal-50 text-ink" : "border-line bg-white text-slate hover:bg-mist"
              )}
            >
              <item.icon className={activeSystem === index ? "text-teal" : "text-slate"} size={18} />
              <span>
                <span className="block text-xs font-semibold uppercase">{item.label}</span>
                <span className="block text-sm font-semibold">{item.title}</span>
              </span>
            </button>
          ))}
        </div>
        <div className="rounded-lg border border-line bg-mist p-4">
          <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase text-slate">{system.label}</p>
              <h3 className="mt-1 text-lg font-semibold text-ink">{system.title}</h3>
              <p className="mt-2 max-w-2xl text-sm leading-6 text-slate">{system.detail}</p>
              <p className="mt-3 text-sm font-semibold text-teal">{system.metric}</p>
            </div>
            <a
              href={system.doc}
              target="_blank"
              rel="noreferrer"
              className="inline-flex h-10 shrink-0 items-center justify-center gap-2 rounded-lg bg-navy px-3 text-sm font-semibold text-white transition hover:bg-navy/90"
            >
              Open writeup
              <ExternalLink size={14} />
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}

function TopicHeatmap({ analytics }: { analytics: Analytics }) {
  const data = analytics.topic_heatmap.length ? analytics.topic_heatmap : [{ topic: "No topics", mentions: 0 }];
  const max = Math.max(1, ...data.map((item) => item.mentions));

  return (
    <section className="rounded-lg border border-line bg-white p-4 shadow-panel">
      <h2 className="text-sm font-semibold text-ink">Topic Heatmap</h2>
      <div className="mt-4 grid gap-3">
        {data.slice(0, 7).map((item, index) => (
          <div key={item.topic} className="grid grid-cols-[150px_minmax(0,1fr)_42px] items-center gap-3">
            <span className="truncate text-xs font-medium text-slate">{formatTopic(item.topic)}</span>
            <div className="h-3 rounded-full bg-slate-100">
              <div
                className="h-3 rounded-full"
                style={{
                  width: `${(item.mentions / max) * 100}%`,
                  background: index % 3 === 0 ? "#0d9488" : index % 3 === 1 ? "#d97706" : "#13283b"
                }}
              />
            </div>
            <span className="text-right text-xs font-semibold text-ink">{item.mentions}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

function ContentFeed({ items, selected, setSelected }: { items: ContentItem[]; selected: ContentItem | null; setSelected: (item: ContentItem) => void }) {
  return (
    <section className="min-w-0 max-w-full rounded-lg border border-line bg-white shadow-panel">
      <div className="flex items-center justify-between border-b border-line px-4 py-3">
        <div>
          <h2 className="text-sm font-semibold text-ink">Competitor Activity Feed</h2>
          <p className="text-xs text-slate">Deduplicated source content with AI intelligence attached</p>
        </div>
        <span className="flex items-center gap-2 rounded-md bg-navy px-3 py-2 text-xs font-semibold text-white">
          <Sparkles size={14} />
          Analyzed
        </span>
      </div>
      <div className="max-w-full overflow-x-auto scrollbar-thin">
        <table className="w-full min-w-[680px] border-collapse text-left">
          <thead className="bg-slate-50 text-xs uppercase text-slate">
            <tr>
              <th className="px-3 py-3 font-semibold">Update</th>
              <th className="px-3 py-3 font-semibold">Source</th>
              <th className="px-3 py-3 font-semibold">Topics</th>
              <th className="px-3 py-3 font-semibold">Priority</th>
              <th className="px-3 py-3 font-semibold">Conf.</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-line">
            {items.map((item) => (
              <tr key={item.content.content_id} onClick={() => setSelected(item)} className={cx("cursor-pointer transition hover:bg-slate-50", selected?.content.content_id === item.content.content_id && "bg-teal-50/60")}>
                <td className="px-3 py-3">
                  <p className="max-w-[340px] truncate text-sm font-semibold text-ink">{item.content.title}</p>
                  <p className="text-xs text-slate">{item.competitor_name} · {formatDate(item.content.published_at)}</p>
                </td>
                <td className="px-3 py-3 text-sm text-slate">{sourceLabels[item.content.source]}</td>
                <td className="px-3 py-3">
                  <div className="flex max-w-[260px] flex-wrap gap-1">
                    {item.analysis.topics.slice(0, 3).map((topic) => (
                      <span key={topic} className="rounded-md border border-line bg-slate-50 px-2 py-1 text-xs font-medium text-slate">{formatTopic(topic)}</span>
                    ))}
                  </div>
                </td>
                <td className="px-3 py-3">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold" style={{ color: priorityColor(item.analysis.priority) }}>{item.analysis.priority}</span>
                    <div className="h-2 w-16 rounded-full bg-slate-100">
                      <div className="h-2 rounded-full" style={{ width: `${item.analysis.priority * 10}%`, background: priorityColor(item.analysis.priority) }} />
                    </div>
                  </div>
                </td>
                <td className="px-3 py-3 text-sm font-medium text-ink">{Math.round(item.analysis.confidence * 100)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
        {!items.length ? (
          <div className="border-t border-line p-8 text-center">
            <p className="text-sm font-semibold text-ink">No competitor activity ingested yet</p>
            <p className="mt-1 text-sm text-slate">Use `POST /api/content` or the API example in the README.</p>
          </div>
        ) : null}
      </div>
    </section>
  );
}

function DetailPanel({ item }: { item: ContentItem | null }) {
  if (!item) {
    return (
      <aside className="rounded-lg border border-line bg-white p-5 shadow-panel">
        <FileText className="text-navy" size={24} />
        <h2 className="mt-4 text-lg font-semibold text-ink">Select an update</h2>
        <p className="mt-2 text-sm leading-6 text-slate">Summary, signals, evidence, and recommended action appear here.</p>
      </aside>
    );
  }

  return (
    <aside className="space-y-3">
      <section className="rounded-lg border border-line bg-white p-4 shadow-panel">
        <div className="flex items-start justify-between gap-3">
          <div>
            <p className="text-xs font-semibold uppercase text-slate">{item.competitor_name}</p>
            <h2 className="mt-1 text-xl font-semibold leading-7 text-ink">{item.content.title}</h2>
          </div>
          <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-lg border border-amber-200 bg-amber-50 text-xl font-semibold text-amber">
            {item.analysis.priority}
          </div>
        </div>
        <p className="mt-4 text-sm leading-6 text-slate">{item.analysis.summary}</p>
      </section>
      <section className="rounded-lg border border-line bg-white p-4 shadow-panel">
        <h3 className="text-sm font-semibold text-ink">Strategic Signals</h3>
        <div className="mt-3 space-y-3">
          {item.strategic_signals.length ? item.strategic_signals.map((signal) => (
            <div key={`${signal.signal_type}-${signal.description}`} className="rounded-lg border border-line bg-mist p-3">
              <div className="flex items-center justify-between gap-2">
                <p className="text-sm font-semibold text-ink">{formatTopic(signal.signal_type)}</p>
                <span className="text-xs font-medium text-slate">{Math.round(signal.confidence * 100)}%</span>
              </div>
              <p className="mt-2 text-sm leading-5 text-slate">{signal.description}</p>
            </div>
          )) : <p className="text-sm text-slate">No major shift detected yet.</p>}
        </div>
      </section>
      <section className="rounded-lg border border-line bg-white p-4 shadow-panel">
        <h3 className="text-sm font-semibold text-ink">Recommended Action</h3>
        <p className="mt-2 text-sm leading-6 text-slate">{item.analysis.recommended_action}</p>
      </section>
    </aside>
  );
}

function DigestPanel({ digest }: { digest: Digest }) {
  const top = digest.top_strategic_developments[0];
  return (
    <section className="rounded-lg border border-line bg-white p-4 shadow-panel">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h2 className="text-sm font-semibold text-ink">Executive Digest</h2>
          <p className="text-xs text-slate">{digest.items_analyzed} analyzed updates in scope</p>
        </div>
        <Lightbulb className="text-teal" size={20} />
      </div>
      {top ? (
        <div className="mt-4 rounded-lg border border-line bg-mist p-4">
          <p className="text-xs font-semibold uppercase text-slate">Top development</p>
          <p className="mt-1 text-sm font-semibold text-ink">{top.competitor}: {top.title}</p>
          <p className="mt-2 text-sm leading-6 text-slate">{top.summary}</p>
        </div>
      ) : <p className="mt-4 text-sm text-slate">Digest will populate after content is ingested.</p>}
      <div className="mt-4 space-y-2">
        {(digest.recommended_actions.length ? digest.recommended_actions : ["Monitor repeated narratives before escalation."]).slice(0, 3).map((action) => (
          <div key={action} className="flex gap-2 text-sm text-slate">
            <CheckCircle2 className="mt-0.5 shrink-0 text-teal" size={16} />
            <span>{action}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

export function CompetitiveDashboard() {
  const [content, setContent] = useState<ContentItem[]>([]);
  const [analytics, setAnalytics] = useState<Analytics>(emptyAnalytics);
  const [digest, setDigest] = useState<Digest>(emptyDigest);
  const [selected, setSelected] = useState<ContentItem | null>(null);
  const [source, setSource] = useState("all");
  const [query, setQuery] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [activeSystem, setActiveSystem] = useState(0);
  const [alertPreview, setAlertPreview] = useState(false);

  useEffect(() => {
    Promise.all([fetchContent(), fetchAnalytics(), fetchDigest()])
      .then(([contentData, analyticsData, digestData]) => {
        setContent(contentData);
        setAnalytics(analyticsData);
        setDigest(digestData);
        setSelected(contentData[0] ?? null);
        setError(null);
      })
      .catch((err: Error) => setError(err.message));
  }, []);

  const filtered = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    return content.filter((item) => {
      const sourceMatch = source === "all" || item.content.source === source;
      const queryMatch = !normalized || [item.content.title, item.competitor_name, item.analysis.summary, item.analysis.topics.join(" "), item.strategic_signals.map((signal) => signal.description).join(" ")].join(" ").toLowerCase().includes(normalized);
      return sourceMatch && queryMatch;
    });
  }, [content, query, source]);

  return (
    <div className="min-h-screen bg-mist text-ink">
      <div className="flex">
        <Sidebar />
        <main className="min-w-0 flex-1">
          <header className="sticky top-0 z-20 border-b border-line bg-mist/95 px-4 py-4 backdrop-blur md:px-6">
            <div className="flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
              <div>
                <h1 className="text-2xl font-semibold text-ink">AI Marketing Automation Systems</h1>
                <p className="text-sm text-slate">Lead qualification, competitor monitoring, and newsletter ideation built as reviewable automation systems.</p>
              </div>
              <div className="flex flex-wrap items-center gap-2">
                <label className="flex h-10 min-w-[250px] items-center gap-2 rounded-lg border border-line bg-white px-3 text-sm text-slate">
                  <Search size={16} />
                  <input value={query} onChange={(event) => setQuery(event.target.value)} className="w-full border-0 bg-transparent text-sm outline-none" placeholder="Search competitors, topics, signals" />
                </label>
                <label className="flex h-10 items-center gap-2 rounded-lg border border-line bg-white px-3 text-sm text-slate">
                  <ListFilter size={16} />
                  <select value={source} onChange={(event) => setSource(event.target.value)} className="bg-transparent text-sm font-medium text-ink outline-none">
                    <option value="all">All sources</option>
                    {Object.entries(sourceLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
                  </select>
                </label>
                <button onClick={() => setAlertPreview((value) => !value)} className="flex h-10 w-10 items-center justify-center rounded-lg border border-line bg-white text-ink transition hover:border-teal hover:bg-teal-50" aria-label="Preview alert">
                  <Bell size={17} />
                </button>
              </div>
            </div>
          </header>
          <div className="space-y-4 p-4 md:p-6">
            {error ? <div className="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm font-medium text-rose-700">Backend unavailable: {error}</div> : null}
            <SubmissionControlCenter activeSystem={activeSystem} setActiveSystem={setActiveSystem} />
            {alertPreview ? (
              <div className="rounded-lg border border-teal-200 bg-teal-50 px-4 py-3 text-sm text-ink">
                <span className="font-semibold">Alert preview:</span> High-priority competitor signals would be sent to Slack/email after the n8n workflow receives a score above the configured threshold.
              </div>
            ) : null}
            <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
              <KpiCard label="Competitors" value={analytics.monitored_competitors.toString()} detail="Tracked companies in intelligence memory" icon={UsersRound} tone="navy" />
              <KpiCard label="Analyzed Items" value={analytics.total_items.toString()} detail="Deduplicated monitored content" icon={FileText} tone="teal" />
              <KpiCard label="High Priority" value={analytics.high_priority_items.toString()} detail="Items scoring 8 or higher" icon={Flame} tone="rose" />
              <KpiCard label="Confidence" value={analytics.avg_confidence.toFixed(2)} detail="Average grounded analysis confidence" icon={Bot} tone="amber" />
            </div>
            <div className="grid gap-3 xl:grid-cols-[1.1fr_0.9fr]">
              <TopicHeatmap analytics={analytics} />
              <section className="rounded-lg border border-line bg-white p-4 shadow-panel">
                <h2 className="text-sm font-semibold text-ink">Competitor Activity</h2>
                <div className="mt-4 space-y-3">
                  {(analytics.competitor_activity.length ? analytics.competitor_activity : [{ competitor: "No competitors", avg_priority: 0, items: 0 }]).slice(0, 5).map((item) => (
                    <div key={item.competitor} className="flex items-center justify-between gap-3 rounded-lg border border-line bg-mist p-3">
                      <div>
                        <p className="text-sm font-semibold text-ink">{item.competitor}</p>
                        <p className="text-xs text-slate">{item.items} monitored updates</p>
                      </div>
                      <span className="rounded-md bg-white px-2 py-1 text-sm font-semibold text-ink">{Number(item.avg_priority).toFixed(1)}</span>
                    </div>
                  ))}
                </div>
              </section>
            </div>
            <div id="intelligence-feed" className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_390px]">
              <div className="min-w-0 space-y-4">
                <ContentFeed items={filtered} selected={selected} setSelected={setSelected} />
                <div className="grid gap-4 xl:grid-cols-2">
                  <div id="digest">
                    <DigestPanel digest={digest} />
                  </div>
                  <section className="rounded-lg border border-line bg-white p-4 shadow-panel">
                    <div className="flex items-center gap-2">
                      <TrendingUp className="text-teal" size={18} />
                      <h2 className="text-sm font-semibold text-ink">Source Coverage</h2>
                    </div>
                    <div className="mt-4 space-y-2">
                      {(analytics.source_mix.length ? analytics.source_mix : [{ source: "No sources", items: 0 }]).map((item) => (
                        <div key={item.source} className="flex items-center justify-between text-sm">
                          <span className="flex items-center gap-2 text-slate"><Link2 size={14} />{formatTopic(item.source)}</span>
                          <span className="font-semibold text-ink">{item.items}</span>
                        </div>
                      ))}
                    </div>
                  </section>
                </div>
              </div>
              <div className="space-y-4">
                <div id="strategic-signals">
                  <DetailPanel item={selected} />
                </div>
                <section id="automations" className="rounded-lg border border-line bg-white p-4 shadow-panel">
                  <div className="flex items-center gap-2">
                    <Globe2 size={18} className="text-teal" />
                    <h2 className="text-sm font-semibold text-ink">Delivery Channels</h2>
                  </div>
                  <div className="mt-4 grid gap-2 text-sm text-slate">
                    <span className="flex items-center gap-2"><Mail size={15} />Email digest ready for Resend integration</span>
                    <span className="flex items-center gap-2"><RadioTower size={15} />Slack alert hooks fit high-priority signals</span>
                    <span className="flex items-center gap-2"><Sparkles size={15} />n8n can schedule discovery and delivery</span>
                  </div>
                </section>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

export const Dashboard = CompetitiveDashboard;
