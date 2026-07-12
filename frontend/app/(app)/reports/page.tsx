"use client"

import { useEffect, useState } from "react"
import { FileText, FileSpreadsheet, Braces, Download, Eye } from "lucide-react"
import { GlassCard } from "@/components/glass"
import { PageHeader } from "@/components/page-header"
import { listReports, type ReportSummary } from "@/lib/api"

const formatMeta: Record<string, { icon: any; tint: string }> = {
  PDF: { icon: FileText, tint: "text-critical bg-critical/15" },
  Excel: { icon: FileSpreadsheet, tint: "text-success bg-success/15" },
  JSON: { icon: Braces, tint: "text-warning bg-warning/15" },
}

export default function ReportsPage() {
  const [reportsList, setReportsList] = useState<ReportSummary[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      try {
        const data = await listReports()
        // Support both {"items": [...]} and {"reports": [...]} formats
        const items = (data as any).items || data.reports || []
        setReportsList(items)
      } catch (err) {
        console.error("Failed to load reports", err)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const handleDownload = async (r: ReportSummary) => {
    const token = typeof window !== "undefined" ? localStorage.getItem("policy_guardian_token") : null
    const headers: Record<string, string> = {}
    if (token) {
      headers["Authorization"] = `Bearer ${token}`
    }

    // Determine backend base URL
    const baseUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000"
    const downloadUrl = `${baseUrl.replace(/\/$/, "")}${r.download_url}`

    try {
      const response = await fetch(downloadUrl, { headers })
      if (!response.ok) {
        throw new Error(`Server returned status ${response.status}`)
      }
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      // Use clean filename
      const ext = r.format.toLowerCase() === "excel" ? "xlsx" : r.format.toLowerCase()
      a.download = `${r.title.toLowerCase().replace(/\s+/g, "_")}_report.${ext}`
      document.body.appendChild(a)
      a.click()
      a.remove()
      window.URL.revokeObjectURL(url)
    } catch (err) {
      alert(`Failed to download report: ${err instanceof Error ? err.message : String(err)}`)
    }
  }

  const handlePreview = async (r: ReportSummary) => {
    // For preview, if it's JSON, alert a quick summary or download it.
    // PDF/Excel will be downloaded.
    if (r.format === "JSON") {
      const token = typeof window !== "undefined" ? localStorage.getItem("policy_guardian_token") : null
      const headers: Record<string, string> = {}
      if (token) {
        headers["Authorization"] = `Bearer ${token}`
      }
      const baseUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000"
      const downloadUrl = `${baseUrl.replace(/\/$/, "")}${r.download_url}`
      try {
        const response = await fetch(downloadUrl, { headers })
        const json = await response.json()
        alert(`JSON Report Preview:\n\n${JSON.stringify(json.summary || json, null, 2).slice(0, 500)}...`)
      } catch (err) {
        handleDownload(r)
      }
    } else {
      handleDownload(r)
    }
  }

  return (
    <div>
      <PageHeader
        title="Reports"
        subtitle="Generate and download audit-ready policy reports."
      />

      {loading ? (
        <div className="flex h-64 items-center justify-center">
          <p className="text-sm text-muted-foreground">Loading reports...</p>
        </div>
      ) : reportsList.length === 0 ? (
        <GlassCard className="p-10 text-center text-sm text-muted-foreground">
          No reports found. Please analyze policies first to generate reports.
        </GlassCard>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {reportsList.map((r) => {
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
                  {r.pages > 0 && ` · ${r.pages} ${r.format === "JSON" ? "records" : "pages"}`}
                </p>

                {/* Preview strip */}
                <div className="mt-4 grid grid-cols-4 gap-1.5">
                  {Array.from({ length: 4 }).map((_, i) => (
                    <div key={i} className="glass-subtle h-12 rounded-lg" />
                  ))}
                </div>

                <div className="mt-5 flex gap-2">
                  <button
                    onClick={() => handleDownload(r)}
                    className="flex h-10 flex-1 items-center justify-center gap-2 rounded-2xl bg-primary text-sm font-semibold text-primary-foreground hover:bg-primary/90"
                  >
                    <Download className="size-4" />
                    Download
                  </button>
                  <button
                    onClick={() => handlePreview(r)}
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
      )}
    </div>
  )
}

