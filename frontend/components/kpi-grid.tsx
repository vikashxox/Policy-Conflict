"use client"

import {
  FileText,
  ShieldCheck,
  GitCompareArrows,
  Copy,
  Clock,
  BadgeCheck,
  TrendingUp,
  TrendingDown,
} from "lucide-react"
import { GlassCard } from "@/components/glass"
import { AnimatedCounter } from "@/components/primitives"
import { Sparkline } from "@/components/charts"
import { kpiMetrics } from "@/lib/data"

const iconMap = { FileText, ShieldCheck, GitCompareArrows, Copy, Clock, BadgeCheck } as const

export function KpiGrid() {
  return (
    <div className="grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-6">
      {kpiMetrics.map((k, i) => {
        const Icon = iconMap[k.icon as keyof typeof iconMap] ?? FileText
        const positive = k.trend === k.good
        const TrendIcon = k.trend === "up" ? TrendingUp : TrendingDown
        const sparkColor = positive ? "var(--color-success)" : "var(--color-critical)"
        return (
          <GlassCard
            key={k.label}
            hover
            className="animate-rise flex flex-col p-4"
            style={{ animationDelay: `${i * 60}ms` }}
          >
            <div className="flex items-start justify-between">
              <div className={`flex size-9 items-center justify-center rounded-xl ${k.tint}`}>
                <Icon className="size-[18px]" />
              </div>
              <span
                className={`inline-flex items-center gap-0.5 text-[11px] font-semibold ${
                  positive ? "text-success" : "text-critical"
                }`}
              >
                <TrendIcon className="size-3" />
                {k.change}
              </span>
            </div>
            <p className="mt-3 text-2xl font-semibold">
              <AnimatedCounter value={k.value} suffix={k.suffix ?? ""} />
            </p>
            <p className="text-xs text-muted-foreground">{k.label}</p>
            <div className="mt-2">
              <Sparkline data={k.spark} color={sparkColor} width={120} height={28} />
            </div>
          </GlassCard>
        )
      })}
    </div>
  )
}
