"use client"

import { useMemo, useState } from "react"
import { Search, ChevronDown } from "lucide-react"
import { GlassCard, SeverityBadge } from "@/components/glass"
import { PageHeader } from "@/components/page-header"
import { findings, type Severity, type FindingStatus } from "@/lib/data"
import { cn } from "@/lib/utils"

const severities: (Severity | "all")[] = ["all", "critical", "warning", "healthy"]
const statuses: (FindingStatus | "all")[] = ["all", "open", "in-review", "resolved"]
const categories = ["all", ...Array.from(new Set(findings.map((f) => f.category)))]

function Select({
  label,
  value,
  options,
  onChange,
}: {
  label: string
  value: string
  options: string[]
  onChange: (v: string) => void
}) {
  return (
    <label className="flex flex-col gap-1.5">
      <span className="text-xs text-muted-foreground">{label}</span>
      <div className="relative">
        <select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="h-10 w-full appearance-none rounded-2xl border border-border bg-white/5 pl-3 pr-9 text-sm capitalize outline-none focus:border-primary/50"
        >
          {options.map((o) => (
            <option key={o} value={o} className="bg-popover capitalize">
              {o.replace("-", " ")}
            </option>
          ))}
        </select>
        <ChevronDown className="pointer-events-none absolute right-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
      </div>
    </label>
  )
}

export default function FindingsPage() {
  const [severity, setSeverity] = useState("all")
  const [status, setStatus] = useState("all")
  const [category, setCategory] = useState("all")
  const [query, setQuery] = useState("")
  const [open, setOpen] = useState<string | null>(null)

  const filtered = useMemo(() => {
    return findings.filter((f) => {
      if (severity !== "all" && f.severity !== severity) return false
      if (status !== "all" && f.status !== status) return false
      if (category !== "all" && f.category !== category) return false
      if (query) {
        const q = query.toLowerCase()
        return (
          f.type.toLowerCase().includes(q) ||
          f.policyA.toLowerCase().includes(q) ||
          f.policyB.toLowerCase().includes(q) ||
          f.description.toLowerCase().includes(q)
        )
      }
      return true
    })
  }, [severity, status, category, query])

  return (
    <div>
      <PageHeader
        title="Findings"
        subtitle="All detected conflicts, duplicates and stale policies."
      />

      <GlassCard className="mb-4 p-4">
        <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
          <label className="flex flex-col gap-1.5 lg:col-span-1">
            <span className="text-xs text-muted-foreground">Search</span>
            <div className="relative">
              <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search findings…"
                className="h-10 w-full rounded-2xl border border-border bg-white/5 pl-10 pr-3 text-sm outline-none placeholder:text-muted-foreground focus:border-primary/50"
              />
            </div>
          </label>
          <Select label="Severity" value={severity} options={severities} onChange={setSeverity} />
          <Select label="Category" value={category} options={categories} onChange={setCategory} />
          <Select label="Status" value={status} options={statuses} onChange={setStatus} />
        </div>
      </GlassCard>

      <p className="mb-3 text-xs text-muted-foreground">
        Showing {filtered.length} of {findings.length} findings
      </p>

      <div className="space-y-3">
        {filtered.map((f) => (
          <GlassCard key={f.id} hover className="overflow-hidden">
            <button
              onClick={() => setOpen(open === f.id ? null : f.id)}
              className="flex w-full items-center gap-4 p-4 text-left"
            >
              <SeverityBadge severity={f.severity}>{f.severity}</SeverityBadge>
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium">{f.type}</p>
                <p className="truncate text-xs text-muted-foreground">
                  {f.policyA}
                  {f.policyB !== "—" && <span> ↔ {f.policyB}</span>}
                </p>
              </div>
              <span className="hidden text-xs capitalize text-muted-foreground sm:block">
                {f.status.replace("-", " ")}
              </span>
              <ChevronDown
                className={cn(
                  "size-4 shrink-0 text-muted-foreground transition-transform",
                  open === f.id && "rotate-180",
                )}
              />
            </button>

            {open === f.id && (
              <div className="grid gap-4 border-t border-border p-4 sm:grid-cols-2">
                <div>
                  <p className="text-xs font-medium text-muted-foreground">Description</p>
                  <p className="mt-1 text-sm">{f.description}</p>
                </div>
                <div>
                  <p className="text-xs font-medium text-muted-foreground">Recommendation</p>
                  <p className="mt-1 text-sm">{f.recommendation}</p>
                </div>
                <div>
                  <p className="text-xs font-medium text-muted-foreground">Compliance Mapping</p>
                  <p className="mt-1 text-sm">{f.compliance}</p>
                </div>
                <div className="flex items-end justify-between gap-3">
                  <div>
                    <p className="text-xs font-medium text-muted-foreground">Finding ID</p>
                    <p className="mt-1 font-mono text-sm">{f.id}</p>
                  </div>
                  <button className="h-9 rounded-2xl bg-primary px-4 text-sm font-semibold text-primary-foreground hover:bg-primary/90">
                    Resolve
                  </button>
                </div>
              </div>
            )}
          </GlassCard>
        ))}

        {filtered.length === 0 && (
          <GlassCard className="p-10 text-center text-sm text-muted-foreground">
            No findings match your filters.
          </GlassCard>
        )}
      </div>
    </div>
  )
}
