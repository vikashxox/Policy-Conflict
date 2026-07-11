import type * as React from "react"
import { cn } from "@/lib/utils"
import type { Severity } from "@/lib/data"

export function GlassCard({
  className,
  hover,
  strong,
  ...props
}: React.HTMLAttributes<HTMLDivElement> & { hover?: boolean; strong?: boolean }) {
  return (
    <div
      className={cn(
        strong ? "glass-strong" : "glass",
        hover && "glass-hover",
        "rounded-3xl",
        className,
      )}
      {...props}
    />
  )
}

const severityStyles: Record<Severity, string> = {
  critical: "bg-critical/15 text-critical border-critical/30",
  warning: "bg-warning/15 text-warning border-warning/30",
  healthy: "bg-success/15 text-success border-success/30",
}

export function SeverityBadge({
  severity,
  children,
  className,
}: {
  severity: Severity
  children: React.ReactNode
  className?: string
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium capitalize",
        severityStyles[severity],
        className,
      )}
    >
      <span
        className={cn(
          "size-1.5 rounded-full",
          severity === "critical" && "bg-critical",
          severity === "warning" && "bg-warning",
          severity === "healthy" && "bg-success",
        )}
      />
      {children}
    </span>
  )
}

export function Chip({
  children,
  className,
}: {
  children: React.ReactNode
  className?: string
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border border-border bg-white/5 px-2.5 py-0.5 text-xs font-medium text-muted-foreground",
        className,
      )}
    >
      {children}
    </span>
  )
}
