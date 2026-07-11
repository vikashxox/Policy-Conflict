"use client"

import {
  Bot,
  GitCompareArrows,
  Clock,
  Copy,
  ShieldAlert,
  ArrowRight,
  Sparkles,
} from "lucide-react"
import { GlassCard } from "@/components/glass"
import { useToast } from "@/components/primitives"
import { aiInsights, aiRecommendation, type Severity } from "@/lib/data"

const iconMap = { GitCompareArrows, Clock, Copy, ShieldAlert } as const

const dot: Record<Severity, string> = {
  critical: "text-critical bg-critical/15",
  warning: "text-warning bg-warning/15",
  healthy: "text-success bg-success/15",
}

export function AiInsights() {
  const { toast } = useToast()

  return (
    <GlassCard className="flex flex-col p-6">
      <div className="mb-5 flex items-center gap-3">
        <span className="relative flex size-10 items-center justify-center rounded-2xl bg-primary/20 text-primary ring-1 ring-primary/30">
          <Bot className="size-5" />
          <span className="absolute -right-0.5 -top-0.5 flex size-3">
            <span className="absolute inline-flex size-full animate-ping rounded-full bg-primary/60" />
            <span className="relative inline-flex size-3 rounded-full bg-primary" />
          </span>
        </span>
        <div>
          <h3 className="flex items-center gap-1.5 text-sm font-semibold">
            AI Governance Insights
            <Sparkles className="size-3.5 text-primary" />
          </h3>
          <p className="text-xs text-muted-foreground">Generated from your latest full audit</p>
        </div>
      </div>

      <ul className="space-y-2.5">
        {aiInsights.map((ins) => {
          const Icon = iconMap[ins.icon as keyof typeof iconMap] ?? GitCompareArrows
          return (
            <li
              key={ins.id}
              className="glass-hover flex items-start gap-3 rounded-2xl border border-border/60 p-3"
            >
              <span className={`flex size-8 shrink-0 items-center justify-center rounded-xl ${dot[ins.severity]}`}>
                <Icon className="size-4" />
              </span>
              <p className="text-sm leading-snug text-pretty">{ins.text}</p>
            </li>
          )
        })}
      </ul>

      <div className="mt-4 rounded-2xl border border-primary/30 bg-primary/10 p-4">
        <p className="text-xs font-semibold uppercase tracking-wide text-primary">Recommended Action</p>
        <p className="mt-1 text-sm text-pretty">{aiRecommendation}</p>
        <button
          onClick={() => toast({ variant: "success", title: "Remediation queued", desc: "Password Rotation Policy flagged for update" })}
          className="mt-3 inline-flex items-center gap-1.5 text-sm font-semibold text-primary hover:gap-2.5 transition-all"
        >
          Apply recommendation
          <ArrowRight className="size-4" />
        </button>
      </div>
    </GlassCard>
  )
}
