"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";
import {
  Activity,
  Bell,
  Bot,
  Building2,
  CheckCircle2,
  ChevronDown,
  CircleDollarSign,
  Clock3,
  Filter,
  Flame,
  Home,
  Inbox,
  LayoutDashboard,
  Mail,
  MapPin,
  Megaphone,
  MessageCircle,
  Radar,
  Route,
  Search,
  Send,
  Settings,
  ShieldAlert,
  Sparkles,
  UsersRound,
  Zap
} from "lucide-react";

import {
  Analytics,
  automationSteps,
  emptyAnalytics,
  fetchAnalytics,
  fetchLeads,
  Lead,
  routeLabels
} from "@/lib/leads";

const sourceLabels = {
  meta_ads: "Meta Ads",
  google_ads: "Google Ads",
  website: "Website",
  landing_page: "Landing Page",
  whatsapp: "WhatsApp",
  csv_upload: "CSV Upload"
};

const routeStyles = {
  hot: "border-teal-200 bg-teal-50 text-teal-700",
  warm: "border-amber-200 bg-amber-50 text-amber-700",
  nurture: "border-sky-200 bg-sky-50 text-sky-700",
  manual_review: "border-slate-200 bg-slate-50 text-slate-700",
  rejected: "border-rose-200 bg-rose-50 text-rose-700"
};

const navItems = [
  { label: "Live Feed", icon: Inbox, active: true },
  { label: "Intelligence", icon: Sparkles },
  { label: "Properties", icon: Building2 },
  { label: "Routing", icon: Route },
  { label: "Campaigns", icon: Megaphone },
  { label: "Analytics", icon: LayoutDashboard },
  { label: "Settings", icon: Settings }
];

function cx(...classes: Array<string | false | null | undefined>) {
  return classes.filter(Boolean).join(" ");
}

function scoreColor(score: number) {
  if (score >= 8) return "#0d9488";
  if (score >= 5) return "#d97706";
  return "#e11d48";
}

function useChartWidth() {
  const ref = useRef<HTMLDivElement | null>(null);
  const [width, setWidth] = useState(0);

  useEffect(() => {
    if (!ref.current) return;
    const observer = new ResizeObserver(([entry]) => {
      setWidth(Math.floor(entry.contentRect.width));
    });
    observer.observe(ref.current);
    return () => observer.disconnect();
  }, []);

  return { ref, width };
}

function routeCount(leads: Lead[], route: Lead["route"]) {
  return leads.filter((lead) => lead.route === route).length;
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
  icon: typeof Activity;
  tone: "teal" | "amber" | "rose" | "navy";
}) {
  const toneClass = {
    teal: "bg-teal-50 text-teal-700 border-teal-100",
    amber: "bg-amber-50 text-amber-700 border-amber-100",
    rose: "bg-rose-50 text-rose-700 border-rose-100",
    navy: "bg-slate-100 text-navy border-slate-200"
  }[tone];

  return (
    <section className="rounded-lg border border-line bg-white p-4 shadow-panel">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase text-slate tracking-normal">{label}</p>
          <p className="mt-2 text-2xl font-semibold text-ink">{value}</p>
        </div>
        <div className={cx("rounded-md border p-2", toneClass)}>
          <Icon size={18} strokeWidth={2} />
        </div>
      </div>
      <p className="mt-3 text-xs leading-5 text-slate">{detail}</p>
    </section>
  );
}

function Sidebar() {
  return (
    <aside className="hidden min-h-screen w-[244px] shrink-0 bg-navy px-4 py-5 text-white lg:block">
      <div className="flex items-center gap-3 px-2">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-teal text-white">
          <Home size={20} strokeWidth={2.4} />
        </div>
        <div>
          <p className="text-sm font-semibold">Lead Intelligence OS</p>
          <p className="text-xs text-slate-300">Real Estate AI Ops</p>
        </div>
      </div>

      <nav className="mt-8 space-y-1">
        {navItems.map((item) => (
          <button
            key={item.label}
            className={cx(
              "flex h-10 w-full items-center gap-3 rounded-md px-3 text-sm transition",
              item.active ? "bg-white text-navy" : "text-slate-300 hover:bg-white/8 hover:text-white"
            )}
          >
            <item.icon size={17} strokeWidth={2} />
            {item.label}
          </button>
        ))}
      </nav>

      <div className="mt-8 rounded-lg border border-white/10 bg-white/5 p-4">
        <div className="flex items-center gap-2 text-sm font-semibold">
          <Bot size={16} />
          AI Guardrails
        </div>
        <p className="mt-2 text-xs leading-5 text-slate-300">
          No mock leads are generated. CRM and notification fanout require real provider configuration.
        </p>
      </div>
    </aside>
  );
}

function Topbar({
  source,
  setSource
}: {
  source: string;
  setSource: (source: string) => void;
}) {
  return (
    <header className="sticky top-0 z-20 border-b border-line bg-mist/95 px-4 py-4 backdrop-blur md:px-6">
      <div className="flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-ink">Lead Intelligence Command Center</h1>
          <p className="text-sm text-slate">Ingestion, validation, AI scoring, property matching, and sales routing.</p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <label className="flex h-10 min-w-[230px] items-center gap-2 rounded-lg border border-line bg-white px-3 text-sm text-slate">
            <Search size={16} />
            <input className="w-full border-0 bg-transparent text-sm outline-none" placeholder="Search leads, phone, area" />
          </label>
          <label className="flex h-10 items-center gap-2 rounded-lg border border-line bg-white px-3 text-sm text-slate">
            <Filter size={16} />
            <select
              value={source}
              onChange={(event) => setSource(event.target.value)}
              className="bg-transparent text-sm font-medium text-ink outline-none"
            >
              <option value="all">All sources</option>
              <option value="google_ads">Google Ads</option>
              <option value="meta_ads">Meta Ads</option>
              <option value="website">Website</option>
              <option value="whatsapp">WhatsApp</option>
              <option value="landing_page">Landing Page</option>
            </select>
          </label>
          <button className="flex h-10 items-center gap-2 rounded-lg border border-line bg-white px-3 text-sm font-medium text-ink">
            Last 30 days
            <ChevronDown size={15} />
          </button>
          <button className="flex h-10 w-10 items-center justify-center rounded-lg border border-line bg-white text-ink" aria-label="Notifications">
            <Bell size={17} />
          </button>
        </div>
      </div>
    </header>
  );
}

function AnalyticsRow({ analytics, leads }: { analytics: Analytics; leads: Lead[] }) {
  return (
    <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
      <KpiCard label="Total leads" value={analytics.total_leads.toLocaleString()} detail="Real ingested leads only" icon={UsersRound} tone="navy" />
      <KpiCard label="Spam rate" value={`${Math.round(analytics.spam_rate * 1000) / 10}%`} detail="Calculated from stored validation results" icon={ShieldAlert} tone="rose" />
      <KpiCard label="Hot leads" value={analytics.hot_leads.toLocaleString()} detail={`${routeCount(leads, "hot")} visible high-priority leads now`} icon={Flame} tone="teal" />
      <KpiCard label="AI confidence" value={analytics.avg_confidence.toFixed(2)} detail="Zero means no real analyzed leads yet" icon={Radar} tone="amber" />
    </div>
  );
}

function ChartCard({ title, children }: { title: string; children: (width: number, height: number) => React.ReactNode }) {
  const { ref, width } = useChartWidth();
  const height = 224;

  return (
    <section className="rounded-lg border border-line bg-white p-4 shadow-panel">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-sm font-semibold text-ink">{title}</h2>
        <button className="text-xs font-medium text-teal">View detail</button>
      </div>
      <div ref={ref} className="h-56 min-h-56 min-w-0">{width > 0 ? children(width, height) : <div className="h-full rounded-md bg-slate-50" />}</div>
    </section>
  );
}

function IntelligenceCharts({ analytics }: { analytics: Analytics }) {
  const sourceQualityData = Object.entries(analytics.source_quality).map(([source, record]) => ({
    source: sourceLabels[source as keyof typeof sourceLabels] ?? source,
    score: record.avg_score,
    volume: record.count
  }));
  const sourceChartData = sourceQualityData.length ? sourceQualityData : [{ source: "No leads", score: 0, volume: 0 }];

  return (
    <div className="grid gap-3 xl:grid-cols-[1.15fr_0.85fr]">
      <ChartCard title="Lead Funnel">
        {(width, height) => (
          <AreaChart width={width} height={height} data={analytics.funnel} margin={{ left: -28, right: 8, top: 12, bottom: 0 }}>
            <defs>
              <linearGradient id="funnel" x1="0" x2="0" y1="0" y2="1">
                <stop offset="5%" stopColor="#0d9488" stopOpacity={0.32} />
                <stop offset="95%" stopColor="#0d9488" stopOpacity={0.03} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="#e8eef1" vertical={false} />
            <XAxis dataKey="stage" tick={{ fontSize: 11, fill: "#53616b" }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fontSize: 11, fill: "#53616b" }} axisLine={false} tickLine={false} />
            <Tooltip />
            <Area type="monotone" dataKey="value" stroke="#0d9488" fill="url(#funnel)" strokeWidth={2.5} isAnimationActive={false} />
          </AreaChart>
        )}
      </ChartCard>
      <ChartCard title="Source Quality">
        {(width, height) => (
          <BarChart width={width} height={height} data={sourceChartData} margin={{ left: -28, right: 8, top: 8, bottom: 0 }}>
            <CartesianGrid stroke="#e8eef1" vertical={false} />
            <XAxis dataKey="source" tick={{ fontSize: 11, fill: "#53616b" }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fontSize: 11, fill: "#53616b" }} axisLine={false} tickLine={false} />
            <Tooltip />
            <Bar dataKey="score" radius={[5, 5, 0, 0]} isAnimationActive={false}>
              {sourceChartData.map((entry) => (
                <Cell key={entry.source} fill={entry.score >= 7 ? "#0d9488" : entry.score >= 5 ? "#d97706" : "#e11d48"} />
              ))}
            </Bar>
          </BarChart>
        )}
      </ChartCard>
    </div>
  );
}

function LeadFeed({
  selectedLead,
  setSelectedLead,
  filteredLeads
}: {
  selectedLead: Lead | null;
  setSelectedLead: (lead: Lead) => void;
  filteredLeads: Lead[];
}) {
  return (
    <section className="rounded-lg border border-line bg-white shadow-panel">
      <div className="flex items-center justify-between border-b border-line px-4 py-3">
        <div>
          <h2 className="text-sm font-semibold text-ink">Live Lead Feed</h2>
          <p className="text-xs text-slate">Real ingested leads only</p>
        </div>
        <button disabled className="flex items-center gap-2 rounded-md bg-navy/70 px-3 py-2 text-xs font-semibold text-white">
          <Send size={14} />
          CRM disabled
        </button>
      </div>
      <div className="overflow-x-auto scrollbar-thin">
        <table className="w-full min-w-[720px] border-collapse text-left">
          <thead className="bg-slate-50 text-xs uppercase text-slate">
            <tr>
              <th className="px-3 py-3 font-semibold">Lead</th>
              <th className="px-3 py-3 font-semibold">Need</th>
              <th className="px-3 py-3 font-semibold">Source</th>
              <th className="px-3 py-3 font-semibold">Score</th>
              <th className="px-3 py-3 font-semibold">Route</th>
              <th className="px-3 py-3 font-semibold">Owner</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-line">
            {filteredLeads.map((lead) => (
              <tr
                key={lead.id}
                onClick={() => setSelectedLead(lead)}
                className={cx("cursor-pointer transition hover:bg-slate-50", selectedLead?.id === lead.id && "bg-teal-50/60")}
              >
                <td className="px-3 py-3">
                  <div className="flex items-center gap-3">
                    <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-slate-100 text-sm font-semibold text-ink">
                      {lead.name.slice(0, 1).toUpperCase()}
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-ink">{lead.name}</p>
                      <p className="text-xs text-slate">{lead.id} · {lead.timestamp}</p>
                    </div>
                  </div>
                </td>
                <td className="px-3 py-3">
                  <p className="text-sm font-medium text-ink">{lead.propertyType} · {lead.budget}</p>
                  <p className="max-w-[190px] truncate text-xs text-slate">{lead.location}</p>
                </td>
                <td className="px-3 py-3 text-sm text-slate">{sourceLabels[lead.source]}</td>
                <td className="px-3 py-3">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold" style={{ color: scoreColor(lead.score) }}>{lead.score.toFixed(1)}</span>
                    <div className="h-2 w-14 rounded-full bg-slate-100">
                      <div className="h-2 rounded-full" style={{ width: `${lead.score * 10}%`, background: scoreColor(lead.score) }} />
                    </div>
                  </div>
                </td>
                <td className="px-3 py-3">
                  <span className={cx("rounded-md border px-2 py-1 text-xs font-semibold", routeStyles[lead.route])}>
                    {routeLabels[lead.route]}
                  </span>
                </td>
                <td className="px-3 py-3">
                  <p className="text-sm font-medium text-ink">{lead.salesperson}</p>
                  <p className="text-xs text-slate">{lead.team}</p>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {!filteredLeads.length ? (
          <div className="border-t border-line p-8 text-center">
            <p className="text-sm font-semibold text-ink">No real leads ingested yet</p>
            <p className="mt-1 text-sm text-slate">Submit a lead to the backend API; the dashboard will stay empty until real records exist.</p>
          </div>
        ) : null}
      </div>
    </section>
  );
}

function SelectedLeadPanel({ lead }: { lead: Lead }) {
  const criticalSignals = lead.validation.filter((signal) => signal.severity !== "info");

  return (
    <aside className="space-y-3">
      <section className="rounded-lg border border-line bg-white p-4 shadow-panel">
        <div className="flex items-start justify-between gap-3">
          <div>
            <p className="text-xs font-semibold uppercase text-slate">Selected lead</p>
            <h2 className="mt-1 text-xl font-semibold text-ink">{lead.name}</h2>
            <p className="mt-1 text-sm text-slate">{lead.propertyType} in {lead.location}</p>
          </div>
          <div className="flex h-14 w-14 items-center justify-center rounded-lg border border-teal-200 bg-teal-50 text-xl font-semibold text-teal">
            {lead.score.toFixed(1)}
          </div>
        </div>
        <div className="mt-4 grid grid-cols-2 gap-2 text-sm">
          <InfoLine icon={Mail} label="Email" value={lead.email} />
          <InfoLine icon={MessageCircle} label="Phone" value={lead.phone} />
          <InfoLine icon={MapPin} label="Area" value={lead.location} />
          <InfoLine icon={CircleDollarSign} label="Budget" value={lead.budget} />
        </div>
      </section>

      <section className="rounded-lg border border-line bg-white p-4 shadow-panel">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-ink">AI Explainability</h2>
          <span className="text-xs font-semibold text-teal">{Math.round(lead.confidence * 100)}% confidence</span>
        </div>
        <ul className="mt-3 space-y-2">
          {lead.reasons.map((reason) => (
            <li key={reason} className="flex gap-2 text-sm text-slate">
              <CheckCircle2 className="mt-0.5 shrink-0 text-teal" size={15} />
              <span>{reason}</span>
            </li>
          ))}
        </ul>
        <div className="mt-4 grid grid-cols-2 gap-2">
          {Object.entries(lead.intent).map(([key, value]) => (
            <div key={key} className="rounded-md border border-line bg-slate-50 p-2">
              <p className="text-[11px] font-semibold uppercase text-slate">{key.replace(/([A-Z])/g, " $1")}</p>
              <p className="mt-1 text-sm font-semibold capitalize text-ink">{value}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="rounded-lg border border-line bg-white p-4 shadow-panel">
        <h2 className="text-sm font-semibold text-ink">Fraud & Validation</h2>
        <div className="mt-3 space-y-2">
          {(criticalSignals.length ? criticalSignals : lead.validation).map((signal) => (
            <div key={signal.key} className="rounded-md border border-line bg-slate-50 p-3">
              <div className="flex items-center gap-2">
                <ShieldAlert size={15} className={signal.severity === "critical" ? "text-rose-600" : "text-teal"} />
                <p className="text-sm font-semibold capitalize text-ink">{signal.key.replaceAll("_", " ")}</p>
              </div>
              <p className="mt-1 text-xs leading-5 text-slate">{signal.message}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="rounded-lg border border-line bg-white p-4 shadow-panel">
        <h2 className="text-sm font-semibold text-ink">Property Matches</h2>
        <div className="mt-3 space-y-3">
          {lead.propertyMatches.length ? (
            lead.propertyMatches.map((match) => (
              <div key={match.name} className="rounded-md border border-line p-3">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="text-sm font-semibold text-ink">{match.name}</p>
                    <p className="text-xs text-slate">{match.location} · {match.type}</p>
                  </div>
                  <span className="text-sm font-semibold text-teal">{Math.round(match.score * 100)}%</span>
                </div>
                <p className="mt-2 text-xs font-medium text-ink">{match.price}</p>
                <p className="mt-1 text-xs leading-5 text-slate">{match.reasons.join(" · ")}</p>
              </div>
            ))
          ) : (
            <p className="rounded-md border border-rose-100 bg-rose-50 p-3 text-sm text-rose-700">No inventory recommended until review clears fraud signals.</p>
          )}
        </div>
      </section>

      <section className="rounded-lg border border-line bg-white p-4 shadow-panel">
        <h2 className="text-sm font-semibold text-ink">Route Decision</h2>
        <div className="mt-3 rounded-md bg-navy p-3 text-white">
          <div className="flex items-center justify-between">
            <span className="text-sm font-semibold">{lead.salesperson}</span>
            <span className="rounded-md bg-white/10 px-2 py-1 text-xs">{routeLabels[lead.route]}</span>
          </div>
          <p className="mt-2 text-xs leading-5 text-slate-200">{lead.nextAction}</p>
        </div>
      </section>
    </aside>
  );
}

function InfoLine({ icon: Icon, label, value }: { icon: typeof Mail; label: string; value: string }) {
  return (
    <div className="min-w-0 rounded-md border border-line bg-slate-50 p-2">
      <div className="flex items-center gap-1.5 text-[11px] font-semibold uppercase text-slate">
        <Icon size={12} />
        {label}
      </div>
      <p className="mt-1 truncate text-xs font-semibold text-ink">{value}</p>
    </div>
  );
}

function AutomationTimeline() {
  return (
    <section className="rounded-lg border border-line bg-white p-4 shadow-panel">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-ink">Automation Pipeline</h2>
        <span className="flex items-center gap-1 text-xs font-semibold text-teal">
          <Zap size={14} />
          n8n + LangChain
        </span>
      </div>
      <div className="mt-4 grid gap-3 md:grid-cols-5">
        {automationSteps.map((step, index) => (
          <div key={step.title} className="relative rounded-md border border-line bg-slate-50 p-3">
            {index < automationSteps.length - 1 ? <div className="absolute right-[-14px] top-6 hidden h-px w-6 bg-line md:block" /> : null}
            <div className="flex items-center gap-2">
              <span className={cx("h-2.5 w-2.5 rounded-full", step.status === "queued" ? "bg-amber" : "bg-teal")} />
              <p className="text-sm font-semibold text-ink">{step.title}</p>
            </div>
            <p className="mt-2 text-xs leading-5 text-slate">{step.detail}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

function DistributionPanel({ analytics }: { analytics: Analytics }) {
  const { ref, width } = useChartWidth();
  const height = 160;

  return (
    <section className="rounded-lg border border-line bg-white p-4 shadow-panel">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-sm font-semibold text-ink">Scoring Distribution</h2>
        <Clock3 size={16} className="text-slate" />
      </div>
      <div ref={ref} className="h-40 min-w-0">
        {width > 0 ? (
          <LineChart width={width} height={height} data={analytics.scoring_distribution} margin={{ left: -22, right: 8, top: 8, bottom: 0 }}>
            <CartesianGrid stroke="#e8eef1" vertical={false} />
            <XAxis dataKey="band" tick={{ fontSize: 11, fill: "#53616b" }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fontSize: 11, fill: "#53616b" }} axisLine={false} tickLine={false} />
            <Tooltip />
            <Line type="monotone" dataKey="leads" stroke="#13283b" strokeWidth={2.4} dot={{ r: 3, fill: "#0d9488" }} isAnimationActive={false} />
          </LineChart>
        ) : (
          <div className="h-full rounded-md bg-slate-50" />
        )}
      </div>
    </section>
  );
}

export function Dashboard() {
  const [source, setSource] = useState("all");
  const [leads, setLeads] = useState<Lead[]>([]);
  const [analytics, setAnalytics] = useState<Analytics>(emptyAnalytics);
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    async function loadRealData() {
      try {
        const [leadData, analyticsData] = await Promise.all([fetchLeads(), fetchAnalytics()]);
        if (!active) return;
        setLeads(leadData);
        setAnalytics(analyticsData);
        setSelectedLead((current) => current && leadData.some((lead) => lead.id === current.id) ? current : leadData[0] ?? null);
        setError(null);
      } catch (caught) {
        if (!active) return;
        setError(caught instanceof Error ? caught.message : "Unable to load real lead data");
      }
    }

    loadRealData();
    const interval = window.setInterval(loadRealData, 15000);
    return () => {
      active = false;
      window.clearInterval(interval);
    };
  }, []);

  const filteredLeads = useMemo(() => {
    return source === "all" ? leads : leads.filter((lead) => lead.source === source);
  }, [leads, source]);

  const visibleSelectedLead = selectedLead && filteredLeads.some((lead) => lead.id === selectedLead.id) ? selectedLead : filteredLeads[0] ?? null;

  return (
    <div className="min-h-screen bg-mist text-ink">
      <div className="flex">
        <Sidebar />
        <main className="min-w-0 flex-1">
          <Topbar source={source} setSource={setSource} />
          <div className="space-y-3 p-4 md:p-6">
            {error ? (
              <div className="rounded-lg border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">
                Real data API unavailable: {error}. No mock fallback is used.
              </div>
            ) : null}
            <AnalyticsRow analytics={analytics} leads={leads} />
            <div className="grid gap-3 xl:grid-cols-[minmax(0,1fr)_360px]">
              <div className="space-y-3">
                <IntelligenceCharts analytics={analytics} />
                <AutomationTimeline />
                <LeadFeed selectedLead={visibleSelectedLead} setSelectedLead={setSelectedLead} filteredLeads={filteredLeads} />
              </div>
              <div className="space-y-3">
                {visibleSelectedLead ? (
                  <SelectedLeadPanel lead={visibleSelectedLead} />
                ) : (
                  <section className="rounded-lg border border-line bg-white p-6 shadow-panel">
                    <h2 className="text-sm font-semibold text-ink">Selected Lead</h2>
                    <p className="mt-2 text-sm leading-6 text-slate">No real lead is available. This panel intentionally stays empty until ingestion receives real data.</p>
                  </section>
                )}
                <DistributionPanel analytics={analytics} />
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
