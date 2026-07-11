"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { Sparkles, ScanSearch, UploadCloud, FileBarChart, Clock, FileText } from "lucide-react"
import { AnimatedCounter, useToast } from "@/components/primitives"
import { org, kpis } from "@/lib/data"

function greeting() {
  const h = new Date().getHours()
  if (h < 12) return "Good morning"
  if (h < 18) return "Good afternoon"
  return "Good evening"
}

export function WelcomeHero() {
  const router = useRouter()
  const { toast } = useToast()
  const [hello, setHello] = useState("Good morning")

  useEffect(() => setHello(greeting()), [])

  return (
    <div className="glass-strong animate-rise relative overflow-hidden rounded-3xl p-6 sm:p-8">
      <div className="pointer-events-none absolute -right-16 -top-16 size-64 rounded-full bg-primary/20 blur-3xl" />
      <div className="relative flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
        <div className="max-w-xl">
          <span className="inline-flex items-center gap-1.5 rounded-full border border-primary/30 bg-primary/10 px-3 py-1 text-xs font-medium text-primary">
            <Sparkles className="size-3.5" />
            AI Governance Console
          </span>
          <h1 className="mt-3 text-2xl font-semibold tracking-tight text-balance sm:text-3xl">
            {hello}, Admin
          </h1>
          <p className="mt-2 text-sm text-muted-foreground text-pretty">
            {org.name} — your organization&apos;s policy landscape is continuously monitored for
            conflicts, duplicates and staleness.
          </p>

          <div className="mt-5 flex flex-wrap gap-2.5">
            <button
              onClick={() => {
                toast({ variant: "info", title: "Analysis started", desc: "Scanning 248 policies for conflicts…" })
                setTimeout(
                  () => toast({ variant: "success", title: "Analysis complete", desc: "3 new critical conflicts found" }),
                  1600,
                )
              }}
              className="flex h-10 items-center gap-2 rounded-2xl bg-primary px-4 text-sm font-semibold text-primary-foreground shadow-lg shadow-primary/30 transition-transform hover:-translate-y-0.5 hover:bg-primary/90"
            >
              <ScanSearch className="size-4" />
              Analyze Policies
            </button>
            <button
              onClick={() => router.push("/upload")}
              className="flex h-10 items-center gap-2 rounded-2xl border border-border bg-white/5 px-4 text-sm font-semibold transition-colors hover:bg-white/10"
            >
              <UploadCloud className="size-4" />
              Upload Policies
            </button>
            <button
              onClick={() => router.push("/reports")}
              className="flex h-10 items-center gap-2 rounded-2xl border border-border bg-white/5 px-4 text-sm font-semibold transition-colors hover:bg-white/10"
            >
              <FileBarChart className="size-4" />
              Generate Report
            </button>
          </div>
        </div>

        {/* Health + meta */}
        <div className="grid shrink-0 grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-1 lg:gap-3">
          <div className="glass rounded-2xl p-4 text-center lg:text-left">
            <p className="text-xs text-muted-foreground">Policy Health</p>
            <p className="text-2xl font-semibold text-success">
              <AnimatedCounter value={kpis.healthScore} suffix="%" />
            </p>
          </div>
          <div className="glass rounded-2xl p-4">
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <Clock className="size-3.5" /> Last Analysis
            </div>
            <p className="mt-1 truncate text-sm font-medium">{org.lastAnalysis}</p>
          </div>
          <div className="glass col-span-2 rounded-2xl p-4 sm:col-span-1 lg:col-span-1">
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <FileText className="size-3.5" /> Last Upload
            </div>
            <p className="mt-1 truncate text-sm font-medium">{org.lastUpload}</p>
          </div>
        </div>
      </div>
    </div>
  )
}
