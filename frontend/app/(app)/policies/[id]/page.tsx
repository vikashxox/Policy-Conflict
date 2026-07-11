import Link from "next/link"
import { notFound } from "next/navigation"
import { ArrowLeft, User, GitBranch, CalendarClock, Tag, CheckCircle2 } from "lucide-react"
import { GlassCard, SeverityBadge, Chip } from "@/components/glass"
import { HealthGauge } from "@/components/charts"
import { policies, findings, obligations } from "@/lib/data"

export default async function PolicyDetailsPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  const policy = policies.find((p) => p.id === id)
  if (!policy) notFound()

  const related = findings.filter((f) => f.category === policy.category)

  const meta = [
    { icon: User, label: "Owner", value: policy.owner },
    { icon: GitBranch, label: "Version", value: policy.version },
    { icon: CalendarClock, label: "Last Reviewed", value: policy.lastReviewed },
    { icon: Tag, label: "Category", value: policy.category },
  ]

  return (
    <div>
      <Link
        href="/policies"
        className="mb-4 inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground"
      >
        <ArrowLeft className="size-4" />
        Back to policies
      </Link>

      <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-semibold tracking-tight">{policy.name}</h1>
            <SeverityBadge severity={policy.severity}>{policy.status}</SeverityBadge>
          </div>
          <p className="mt-1 font-mono text-sm text-muted-foreground">{policy.id}</p>
        </div>
        <button className="h-10 rounded-2xl bg-primary px-4 text-sm font-semibold text-primary-foreground shadow-lg shadow-primary/30 hover:bg-primary/90">
          Schedule Review
        </button>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        {/* Metadata */}
        <GlassCard className="p-6 lg:col-span-2">
          <h3 className="mb-4 text-sm font-medium">Metadata</h3>
          <div className="grid gap-4 sm:grid-cols-2">
            {meta.map((m) => {
              const Icon = m.icon
              return (
                <div key={m.label} className="flex items-center gap-3">
                  <span className="flex size-9 items-center justify-center rounded-xl bg-white/5 text-primary">
                    <Icon className="size-[18px]" />
                  </span>
                  <div>
                    <p className="text-xs text-muted-foreground">{m.label}</p>
                    <p className="text-sm font-medium">{m.value}</p>
                  </div>
                </div>
              )
            })}
          </div>
        </GlassCard>

        {/* Health */}
        <GlassCard className="flex flex-col items-center justify-center p-6">
          <h3 className="self-start text-sm font-medium">Health Score</h3>
          <HealthGauge value={policy.health} />
        </GlassCard>
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-2">
        {/* Obligations */}
        <GlassCard className="p-6">
          <h3 className="mb-4 text-sm font-medium">Extracted Obligations</h3>
          <ul className="space-y-3">
            {obligations.map((o, i) => (
              <li key={i} className="flex items-start gap-3 text-sm">
                <CheckCircle2 className="mt-0.5 size-4 shrink-0 text-success" />
                <span className="text-muted-foreground">{o}</span>
              </li>
            ))}
          </ul>
        </GlassCard>

        {/* Findings & recommendations */}
        <GlassCard className="p-6">
          <h3 className="mb-4 text-sm font-medium">Findings & Recommendations</h3>
          {related.length === 0 ? (
            <p className="text-sm text-muted-foreground">No open findings for this policy.</p>
          ) : (
            <ul className="space-y-4">
              {related.map((f) => (
                <li key={f.id} className="rounded-2xl border border-border bg-white/5 p-4">
                  <div className="mb-2 flex items-center justify-between gap-3">
                    <SeverityBadge severity={f.severity}>{f.type}</SeverityBadge>
                    <Chip>{f.compliance}</Chip>
                  </div>
                  <p className="text-sm">{f.description}</p>
                  <p className="mt-2 text-xs text-muted-foreground">
                    <span className="font-medium text-foreground">Recommendation: </span>
                    {f.recommendation}
                  </p>
                </li>
              ))}
            </ul>
          )}
        </GlassCard>
      </div>
    </div>
  )
}
