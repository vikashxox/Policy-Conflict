import Link from "next/link"
import {
  Activity as ActivityIcon,
  Network,
  TrendingDown,
  Share2,
} from "lucide-react"
import { GlassCard, SeverityBadge } from "@/components/glass"
import { HealthGauge, DonutChart, BarChart, TrendChart, RelationshipGraph } from "@/components/charts"
import { WelcomeHero } from "@/components/welcome-hero"
import { AiInsights } from "@/components/ai-insights"
import { KpiGrid } from "@/components/kpi-grid"
import { ComplianceWidget } from "@/components/compliance-widget"
import {
  kpis,
  healthBreakdown,
  policiesByCategory,
  complianceDistribution,
  healthTrend,
  conflictTrend,
  findings,
  recentUploads,
  activity,
  graphNodes,
  graphLinks,
} from "@/lib/data"

export default function DashboardPage() {
  return (
    <div className="space-y-4">
      <WelcomeHero />

      {/* KPI cards with sparklines */}
      <KpiGrid />

      {/* AI insights + health gauge */}
      <div className="grid gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <AiInsights />
        </div>
        <GlassCard className="flex flex-col items-center justify-center p-6">
          <h3 className="self-start text-sm font-medium">Overall Policy Health</h3>
          <div className="flex flex-1 items-center">
            <HealthGauge value={kpis.healthScore} />
          </div>
          <p className="text-center text-xs text-muted-foreground">
            Weighted across conflicts, staleness &amp; coverage
          </p>
        </GlassCard>
      </div>

      {/* Trend charts */}
      <div className="grid gap-4 lg:grid-cols-2">
        <GlassCard className="p-6">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="text-sm font-medium">Policy Health Trend</h3>
            <span className="inline-flex items-center gap-1 text-xs text-success">
              +14 pts YTD
            </span>
          </div>
          <TrendChart data={healthTrend} color="var(--color-success)" />
        </GlassCard>
        <GlassCard className="p-6">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="text-sm font-medium">Conflict Trend</h3>
            <span className="inline-flex items-center gap-1 text-xs text-success">
              <TrendingDown className="size-3.5" /> Down 45%
            </span>
          </div>
          <TrendChart data={conflictTrend} color="var(--color-critical)" />
        </GlassCard>
      </div>

      {/* Distribution charts */}
      <div className="grid gap-4 lg:grid-cols-3">
        <GlassCard className="p-6">
          <h3 className="mb-4 text-sm font-medium">Policy Categories</h3>
          <BarChart data={policiesByCategory} />
        </GlassCard>
        <GlassCard className="p-6">
          <h3 className="mb-4 text-sm font-medium">Policy Distribution</h3>
          <DonutChart data={healthBreakdown} />
        </GlassCard>
        <GlassCard className="p-6">
          <h3 className="mb-4 text-sm font-medium">Compliance Distribution</h3>
          <DonutChart data={complianceDistribution} />
        </GlassCard>
      </div>

      {/* Relationship graph + compliance widget */}
      <div className="grid gap-4 lg:grid-cols-3">
        <GlassCard className="p-6 lg:col-span-2">
          <div className="mb-2 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Network className="size-4 text-primary" />
              <h3 className="text-sm font-medium">Policy Relationship Graph</h3>
            </div>
            <div className="flex items-center gap-4 text-[11px] text-muted-foreground">
              <span className="flex items-center gap-1.5">
                <span className="h-0.5 w-4 bg-critical" /> Conflict
              </span>
              <span className="flex items-center gap-1.5">
                <span className="h-0.5 w-4 border-t border-dashed border-primary" /> Recommendation
              </span>
            </div>
          </div>
          <RelationshipGraph nodes={graphNodes} links={graphLinks} />
        </GlassCard>
        <ComplianceWidget />
      </div>

      {/* Findings + side column */}
      <div className="grid gap-4 lg:grid-cols-3">
        <GlassCard className="p-6 lg:col-span-2">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="text-sm font-medium">Recent Findings</h3>
            <Link href="/findings" className="text-xs font-medium text-primary hover:underline">
              View all
            </Link>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border text-left text-xs text-muted-foreground">
                  <th className="pb-2 font-medium">Severity</th>
                  <th className="pb-2 font-medium">Type</th>
                  <th className="pb-2 font-medium">Policies</th>
                  <th className="pb-2 font-medium">Confidence</th>
                  <th className="pb-2 font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {findings.slice(0, 5).map((f) => (
                  <tr key={f.id} className="border-b border-border/60 last:border-0">
                    <td className="py-3 pr-3">
                      <SeverityBadge severity={f.severity}>{f.severity}</SeverityBadge>
                    </td>
                    <td className="py-3 pr-3 font-medium">{f.type}</td>
                    <td className="max-w-[200px] truncate py-3 pr-3 text-muted-foreground">
                      {f.policyA}
                      {f.policyB !== "—" && <span> ↔ {f.policyB}</span>}
                    </td>
                    <td className="py-3 pr-3 tabular-nums text-muted-foreground">{f.confidence}%</td>
                    <td className="py-3 capitalize text-muted-foreground">
                      {f.status.replace("-", " ")}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </GlassCard>

        <div className="flex flex-col gap-4">
          <GlassCard className="p-6">
            <div className="mb-4 flex items-center gap-2">
              <Share2 className="size-4 text-primary" />
              <h3 className="text-sm font-medium">Recent Uploads</h3>
            </div>
            <ul className="space-y-3">
              {recentUploads.slice(0, 4).map((u) => (
                <li key={u.id} className="flex items-center gap-3">
                  <span className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-white/5 text-[10px] font-semibold text-muted-foreground">
                    {u.type}
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium">{u.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {u.size} · {u.time}
                    </p>
                  </div>
                  <span
                    className={
                      u.status === "complete"
                        ? "text-xs text-success"
                        : u.status === "processing"
                          ? "text-xs text-warning"
                          : "text-xs text-muted-foreground"
                    }
                  >
                    {u.status}
                  </span>
                </li>
              ))}
            </ul>
          </GlassCard>

          <GlassCard className="p-6">
            <div className="mb-4 flex items-center gap-2">
              <ActivityIcon className="size-4 text-primary" />
              <h3 className="text-sm font-medium">Activity Timeline</h3>
            </div>
            <ol className="relative space-y-4 border-l border-border pl-4">
              {activity.map((a) => (
                <li key={a.id} className="relative">
                  <span
                    className={`absolute -left-[21px] top-1 size-2.5 rounded-full ring-4 ring-background ${
                      a.severity === "critical"
                        ? "bg-critical"
                        : a.severity === "warning"
                          ? "bg-warning"
                          : "bg-success"
                    }`}
                  />
                  <p className="text-sm leading-snug">
                    <span className="font-medium">{a.actor}</span>{" "}
                    <span className="text-muted-foreground">{a.action}</span>{" "}
                    <span className="font-medium">{a.target}</span>
                  </p>
                  <p className="text-xs text-muted-foreground">{a.time}</p>
                </li>
              ))}
            </ol>
          </GlassCard>
        </div>
      </div>
    </div>
  )
}
