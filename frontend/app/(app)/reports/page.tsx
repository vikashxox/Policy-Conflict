import { FileText, FileSpreadsheet, Braces, Download, Eye } from "lucide-react"
import { GlassCard } from "@/components/glass"
import { PageHeader } from "@/components/page-header"
import { reports } from "@/lib/data"

const formatMeta: Record<string, { icon: typeof FileText; tint: string }> = {
  PDF: { icon: FileText, tint: "text-critical bg-critical/15" },
  Excel: { icon: FileSpreadsheet, tint: "text-success bg-success/15" },
  JSON: { icon: Braces, tint: "text-warning bg-warning/15" },
}

export default function ReportsPage() {
  return (
    <div>
      <PageHeader
        title="Reports"
        subtitle="Generate and download audit-ready policy reports."
      />

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {reports.map((r) => {
          const meta = formatMeta[r.format] ?? formatMeta.PDF
          const Icon = meta.icon
          return (
            <GlassCard key={r.id} hover className="flex flex-col p-6">
              <div className="mb-4 flex items-center justify-between">
                <span className={`flex size-11 items-center justify-center rounded-2xl ${meta.tint}`}>
                  <Icon className="size-5" />
                </span>
                <span className="rounded-full border border-border bg-white/5 px-2.5 py-0.5 text-[11px] font-medium text-muted-foreground">
                  {r.format}
                </span>
              </div>

              <h3 className="text-base font-semibold">{r.title}</h3>
              <p className="mt-1 flex-1 text-sm text-muted-foreground">{r.desc}</p>

              <p className="mt-4 text-xs text-muted-foreground">
                Updated {r.updated}
                {r.pages > 0 && ` · ${r.pages} pages`}
              </p>

              {/* Preview strip */}
              <div className="mt-4 grid grid-cols-4 gap-1.5">
                {Array.from({ length: 4 }).map((_, i) => (
                  <div key={i} className="glass-subtle h-12 rounded-lg" />
                ))}
              </div>

              <div className="mt-5 flex gap-2">
                <button className="flex h-10 flex-1 items-center justify-center gap-2 rounded-2xl bg-primary text-sm font-semibold text-primary-foreground hover:bg-primary/90">
                  <Download className="size-4" />
                  Download
                </button>
                <button
                  className="flex size-10 items-center justify-center rounded-2xl border border-border bg-white/5 text-muted-foreground hover:bg-white/10"
                  aria-label="Preview report"
                >
                  <Eye className="size-4" />
                </button>
              </div>
            </GlassCard>
          )
        })}
      </div>
    </div>
  )
}
