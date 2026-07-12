"use client"

import { useId } from "react"
import type { GraphNode, GraphLink } from "@/lib/data"

function ratingFor(value: number) {
  if (value >= 90) return { label: "Excellent", color: "var(--color-success)" }
  if (value >= 75) return { label: "Healthy", color: "var(--color-success)" }
  if (value >= 55) return { label: "Warning", color: "var(--color-warning)" }
  return { label: "Critical", color: "var(--color-critical)" }
}

export function HealthGauge({ value, size = 240 }: { value: number; size?: number }) {
  const radius = 80
  const circumference = Math.PI * radius // half circle
  const offset = circumference - (value / 100) * circumference
  const rating = ratingFor(value)
  const gid = useId()

  return (
    <div className="relative flex flex-col items-center">
      <svg viewBox="0 0 200 120" className="w-full" style={{ maxWidth: size }}>
        <defs>
          <linearGradient id={`g-${gid}`} x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="var(--color-primary)" />
            <stop offset="100%" stopColor={rating.color} />
          </linearGradient>
        </defs>
        <path
          d="M 20 110 A 80 80 0 0 1 180 110"
          fill="none"
          stroke="oklch(1 0 0 / 0.1)"
          strokeWidth="16"
          strokeLinecap="round"
        />
        <path
          d="M 20 110 A 80 80 0 0 1 180 110"
          fill="none"
          stroke={`url(#g-${gid})`}
          strokeWidth="16"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{ transition: "stroke-dashoffset 1.1s cubic-bezier(0.22,1,0.36,1)" }}
        />
      </svg>
      <div className="-mt-16 flex flex-col items-center">
        <span className="text-4xl font-semibold tabular-nums">{value}</span>
        <span
          className="mt-1 rounded-full px-2.5 py-0.5 text-xs font-medium"
          style={{ color: rating.color, background: `color-mix(in oklch, ${rating.color} 18%, transparent)` }}
        >
          {rating.label}
        </span>
      </div>
    </div>
  )
}

export function DonutChart({
  data,
}: {
  data: { label: string; value: number; color: string }[]
}) {
  if (data.length === 0) {
    return (
      <div className="flex h-40 items-center justify-center text-xs text-muted-foreground">
        No data
      </div>
    )
  }

  const total = data.reduce((sum, d) => sum + d.value, 0)
  const radius = 60
  const circumference = 2 * Math.PI * radius
  let acc = 0

  return (
    <div className="flex flex-col items-center gap-5 sm:flex-row sm:justify-center">
      <div className="relative">
        <svg viewBox="0 0 160 160" className="size-40 -rotate-90">
          {data.map((d) => {
            const fraction = d.value / total
            const dash = fraction * circumference
            const seg = (
              <circle
                key={d.label}
                cx="80"
                cy="80"
                r={radius}
                fill="none"
                stroke={d.color}
                strokeWidth="18"
                strokeDasharray={`${dash} ${circumference - dash}`}
                strokeDashoffset={-acc * circumference}
                strokeLinecap="butt"
              />
            )
            acc += fraction
            return seg
          })}
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-2xl font-semibold tabular-nums">{total}</span>
          <span className="text-[11px] text-muted-foreground">Total</span>
        </div>
      </div>
      <ul className="space-y-2">
        {data.map((d) => (
          <li key={d.label} className="flex items-center gap-2 text-sm">
            <span className="size-2.5 rounded-full" style={{ background: d.color }} />
            <span className="text-muted-foreground">{d.label}</span>
            <span className="font-medium tabular-nums">{d.value}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}

export function BarChart({
  data,
}: {
  data: { category: string; count: number }[]
}) {
  if (data.length === 0) {
    return <div className="flex h-52 items-center justify-center text-xs text-muted-foreground">No data</div>
  }
  const max = Math.max(...data.map((d) => d.count))

  return (
    <div className="flex h-52 items-end gap-3">
      {data.map((d) => (
        <div key={d.category} className="group flex flex-1 flex-col items-center gap-2">
          <div className="flex h-40 w-full items-end">
            <div
              className="w-full rounded-t-lg bg-gradient-to-t from-primary/40 to-primary transition-all duration-700 group-hover:from-primary/60 group-hover:to-primary"
              style={{ height: `${(d.count / max) * 100}%` }}
              title={`${d.category}: ${d.count}`}
            />
          </div>
          <span className="text-center text-[10px] leading-tight text-muted-foreground">
            {d.category}
          </span>
        </div>
      ))}
    </div>
  )
}

/* -------------------- Sparkline (KPI cards) -------------------- */
export function Sparkline({
  data,
  color = "var(--color-primary)",
  width = 96,
  height = 32,
}: {
  data: number[]
  color?: string
  width?: number
  height?: number
}) {
  const gid = useId()

  if (data.length < 2) {
    return <svg viewBox={`0 0 ${width} ${height}`} width={width} height={height} />
  }

  const min = Math.min(...data)
  const max = Math.max(...data)
  const range = max - min || 1
  const step = width / (data.length - 1)
  const points = data.map((v, i) => [i * step, height - ((v - min) / range) * (height - 4) - 2])
  const line = points.map((p, i) => `${i === 0 ? "M" : "L"} ${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join(" ")
  const area = `${line} L ${width} ${height} L 0 ${height} Z`

  return (
    <svg viewBox={`0 0 ${width} ${height}`} width={width} height={height} className="overflow-visible">
      <defs>
        <linearGradient id={`spark-${gid}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.35" />
          <stop offset="100%" stopColor={color} stopOpacity="0" />
        </linearGradient>
      </defs>
      <path d={area} fill={`url(#spark-${gid})`} />
      <path d={line} fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

/* -------------------- Line / area trend chart -------------------- */
export function TrendChart({
  data,
  color = "var(--color-primary)",
  height = 200,
}: {
  data: { label: string; value: number }[]
  color?: string
  height?: number
}) {
  const gid = useId()
  const width = 520
  const pad = 28

  // ── Guard: need at least 2 points to draw a meaningful line ──────────────
  if (data.length < 2) {
    return (
      <svg viewBox={`0 0 ${width} ${height}`} className="w-full" style={{ maxHeight: height }}>
        <text
          x={width / 2}
          y={height / 2}
          textAnchor="middle"
          dominantBaseline="middle"
          className="fill-muted-foreground text-[11px]"
        >
          No data
        </text>
      </svg>
    )
  }

  const values = data.map((d) => d.value)
  const min = Math.min(...values)
  const max = Math.max(...values)
  const range = max - min || 1
  const stepX = (width - pad * 2) / (data.length - 1)
  const pts = data.map((d, i) => [
    pad + i * stepX,
    height - pad - ((d.value - min) / range) * (height - pad * 2),
  ])
  const line = pts.map((p, i) => `${i === 0 ? "M" : "L"} ${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join(" ")
  const area = `${line} L ${pts[pts.length - 1][0]} ${height - pad} L ${pts[0][0]} ${height - pad} Z`

  return (
    <svg viewBox={`0 0 ${width} ${height}`} className="w-full" style={{ maxHeight: height }}>
      <defs>
        <linearGradient id={`trend-${gid}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.3" />
          <stop offset="100%" stopColor={color} stopOpacity="0" />
        </linearGradient>
      </defs>
      {[0.25, 0.5, 0.75].map((f) => (
        <line
          key={f}
          x1={pad}
          x2={width - pad}
          y1={pad + f * (height - pad * 2)}
          y2={pad + f * (height - pad * 2)}
          stroke="oklch(1 0 0 / 0.06)"
          strokeWidth="1"
        />
      ))}
      <path d={area} fill={`url(#trend-${gid})`} />
      <path d={line} fill="none" stroke={color} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
      {pts.map((p, i) => (
        <g key={i}>
          <circle cx={p[0]} cy={p[1]} r="3.5" fill="var(--color-background)" stroke={color} strokeWidth="2" />
          <text x={p[0]} y={height - 8} textAnchor="middle" className="fill-muted-foreground text-[10px]">
            {data[i].label}
          </text>
        </g>
      ))}
    </svg>
  )
}

/* -------------------- Policy relationship graph -------------------- */
export function RelationshipGraph({
  nodes,
  links,
}: {
  nodes: GraphNode[]
  links: GraphLink[]
}) {
  const color = (s: GraphNode["severity"]) =>
    s === "critical" ? "var(--color-critical)" : s === "warning" ? "var(--color-warning)" : "var(--color-success)"
  const byId = Object.fromEntries(nodes.map((n) => [n.id, n]))

  return (
    <div className="relative aspect-[16/10] w-full">
      <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="absolute inset-0 h-full w-full">
        {links.map((l, i) => {
          const a = byId[l.from]
          const b = byId[l.to]
          if (!a || !b) return null
          const stroke = l.kind === "conflict" ? "var(--color-critical)" : "var(--color-primary)"
          return (
            <line
              key={i}
              x1={a.x}
              y1={a.y}
              x2={b.x}
              y2={b.y}
              stroke={stroke}
              strokeWidth="0.5"
              strokeDasharray={l.kind === "recommendation" ? "1.5 1.5" : undefined}
              strokeOpacity="0.6"
              vectorEffect="non-scaling-stroke"
            />
          )
        })}
      </svg>
      {nodes.map((n) => (
        <div
          key={n.id}
          className="glass-hover absolute flex -translate-x-1/2 -translate-y-1/2 flex-col items-center gap-1"
          style={{ left: `${n.x}%`, top: `${n.y}%` }}
        >
          <span
            className="flex size-10 items-center justify-center rounded-2xl text-[10px] font-semibold"
            style={{ background: `color-mix(in oklch, ${color(n.severity)} 22%, transparent)`, color: color(n.severity) }}
          >
            <span className="size-2.5 rounded-full" style={{ background: color(n.severity) }} />
          </span>
          <span className="whitespace-nowrap text-[10px] text-muted-foreground">{n.label}</span>
        </div>
      ))}
    </div>
  )
}
