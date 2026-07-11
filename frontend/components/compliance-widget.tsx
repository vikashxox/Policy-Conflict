import { GlassCard } from "@/components/glass"
import { complianceFrameworks } from "@/lib/data"

function tone(score: number) {
  if (score >= 90) return "var(--color-success)"
  if (score >= 80) return "var(--color-primary)"
  if (score >= 70) return "var(--color-warning)"
  return "var(--color-critical)"
}

export function ComplianceWidget() {
  return (
    <GlassCard className="p-6">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-sm font-medium">Compliance Coverage</h3>
        <span className="text-xs text-muted-foreground">4 frameworks</span>
      </div>
      <ul className="space-y-4">
        {complianceFrameworks.map((f) => {
          const color = tone(f.score)
          return (
            <li key={f.name}>
              <div className="mb-1.5 flex items-center justify-between text-sm">
                <span className="font-medium">{f.name}</span>
                <span className="tabular-nums" style={{ color }}>
                  {f.score}%
                </span>
              </div>
              <div className="h-2 w-full overflow-hidden rounded-full bg-white/10">
                <div
                  className="h-full rounded-full transition-all duration-700"
                  style={{ width: `${f.score}%`, background: color }}
                />
              </div>
              <p className="mt-1 text-[11px] text-muted-foreground">{f.controls}</p>
            </li>
          )
        })}
      </ul>
    </GlassCard>
  )
}
