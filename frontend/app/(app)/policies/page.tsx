import Link from "next/link"
import { ChevronRight } from "lucide-react"
import { GlassCard, SeverityBadge } from "@/components/glass"
import { PageHeader } from "@/components/page-header"
import { policies } from "@/lib/data"

export default function PoliciesPage() {
  return (
    <div>
      <PageHeader title="Policies" subtitle="Every policy tracked across your organization." />

      <GlassCard className="overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-left text-xs text-muted-foreground">
                <th className="px-5 py-3 font-medium">Policy</th>
                <th className="px-5 py-3 font-medium">Category</th>
                <th className="px-5 py-3 font-medium">Owner</th>
                <th className="px-5 py-3 font-medium">Version</th>
                <th className="px-5 py-3 font-medium">Health</th>
                <th className="px-5 py-3 font-medium">Status</th>
                <th className="px-5 py-3" />
              </tr>
            </thead>
            <tbody>
              {policies.map((p) => (
                <tr key={p.id} className="border-b border-border/60 last:border-0 hover:bg-white/5">
                  <td className="px-5 py-3">
                    <Link href={`/policies/${p.id}`} className="font-medium hover:text-primary">
                      {p.name}
                    </Link>
                    <p className="text-xs text-muted-foreground">Reviewed {p.lastReviewed}</p>
                  </td>
                  <td className="px-5 py-3 text-muted-foreground">{p.category}</td>
                  <td className="px-5 py-3 text-muted-foreground">{p.owner}</td>
                  <td className="px-5 py-3 font-mono text-xs">{p.version}</td>
                  <td className="px-5 py-3">
                    <div className="flex items-center gap-2">
                      <div className="h-1.5 w-16 overflow-hidden rounded-full bg-white/10">
                        <div
                          className={
                            p.health >= 80
                              ? "h-full rounded-full bg-success"
                              : p.health >= 60
                                ? "h-full rounded-full bg-warning"
                                : "h-full rounded-full bg-critical"
                          }
                          style={{ width: `${p.health}%` }}
                        />
                      </div>
                      <span className="tabular-nums text-xs">{p.health}</span>
                    </div>
                  </td>
                  <td className="px-5 py-3">
                    <SeverityBadge severity={p.severity}>{p.status}</SeverityBadge>
                  </td>
                  <td className="px-5 py-3 text-right">
                    <Link
                      href={`/policies/${p.id}`}
                      className="inline-flex text-muted-foreground hover:text-primary"
                      aria-label={`Open ${p.name}`}
                    >
                      <ChevronRight className="size-4" />
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </GlassCard>
    </div>
  )
}
