"use client"

import * as React from "react"
import { createContext, useCallback, useContext, useEffect, useRef, useState } from "react"
import { CheckCircle2, AlertTriangle, Info, X } from "lucide-react"
import { cn } from "@/lib/utils"

/* -------------------- Animated counter -------------------- */
export function AnimatedCounter({
  value,
  suffix = "",
  duration = 1100,
  className,
}: {
  value: number
  suffix?: string
  duration?: number
  className?: string
}) {
  const [display, setDisplay] = useState(0)
  const ref = useRef<HTMLSpanElement>(null)
  const started = useRef(false)

  useEffect(() => {
    const el = ref.current
    if (!el) return
    const io = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && !started.current) {
          started.current = true
          const start = performance.now()
          const tick = (now: number) => {
            const p = Math.min((now - start) / duration, 1)
            const eased = 1 - Math.pow(1 - p, 3)
            setDisplay(Math.round(eased * value))
            if (p < 1) requestAnimationFrame(tick)
          }
          requestAnimationFrame(tick)
        }
      },
      { threshold: 0.4 },
    )
    io.observe(el)
    return () => io.disconnect()
  }, [value, duration])

  return (
    <span ref={ref} className={cn("tabular-nums", className)}>
      {display}
      {suffix}
    </span>
  )
}

/* -------------------- Skeleton -------------------- */
export function Skeleton({ className }: { className?: string }) {
  return <div className={cn("skeleton rounded-2xl", className)} />
}

/* -------------------- Toasts -------------------- */
type ToastVariant = "success" | "warning" | "info"
type Toast = { id: number; title: string; desc?: string; variant: ToastVariant }
type ToastCtx = { toast: (t: Omit<Toast, "id">) => void }

const ToastContext = createContext<ToastCtx | null>(null)

export function useToast() {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error("useToast must be used within ToastProvider")
  return ctx
}

const icons = {
  success: CheckCircle2,
  warning: AlertTriangle,
  info: Info,
}
const tints = {
  success: "text-success",
  warning: "text-warning",
  info: "text-primary",
}

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([])

  const toast = useCallback((t: Omit<Toast, "id">) => {
    const id = Date.now() + Math.random()
    setToasts((prev) => [...prev, { ...t, id }])
    setTimeout(() => setToasts((prev) => prev.filter((x) => x.id !== id)), 3800)
  }, [])

  const dismiss = (id: number) => setToasts((prev) => prev.filter((x) => x.id !== id))

  return (
    <ToastContext.Provider value={{ toast }}>
      {children}
      <div className="pointer-events-none fixed bottom-4 right-4 z-[100] flex w-[calc(100%-2rem)] max-w-sm flex-col gap-2">
        {toasts.map((t) => {
          const Icon = icons[t.variant]
          return (
            <div
              key={t.id}
              className="glass-strong animate-rise pointer-events-auto flex items-start gap-3 rounded-2xl p-4"
              role="status"
            >
              <Icon className={cn("mt-0.5 size-5 shrink-0", tints[t.variant])} />
              <div className="min-w-0 flex-1">
                <p className="text-sm font-semibold">{t.title}</p>
                {t.desc && <p className="text-xs text-muted-foreground">{t.desc}</p>}
              </div>
              <button
                onClick={() => dismiss(t.id)}
                className="rounded-full p-1 text-muted-foreground hover:bg-white/10"
                aria-label="Dismiss notification"
              >
                <X className="size-4" />
              </button>
            </div>
          )
        })}
      </div>
    </ToastContext.Provider>
  )
}
