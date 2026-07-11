"use client"

import { useEffect, useRef, useState } from "react"
import Link from "next/link"
import { useRouter, usePathname } from "next/navigation"
import {
  LayoutDashboard,
  FileText,
  UploadCloud,
  AlertTriangle,
  FileBarChart,
  Settings,
  Search,
  Bell,
  ShieldCheck,
  Menu,
  X,
  Sun,
  GitCompareArrows,
  CalendarClock,
  CornerDownLeft,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { searchIndex, notifications as seedNotifications, type Severity } from "@/lib/data"

const nav = [
  { label: "Dashboard", href: "/", icon: LayoutDashboard },
  { label: "Policies", href: "/policies", icon: FileText },
  { label: "Upload", href: "/upload", icon: UploadCloud },
  { label: "Findings", href: "/findings", icon: AlertTriangle },
  { label: "Reports", href: "/reports", icon: FileBarChart },
  { label: "Settings", href: "/settings", icon: Settings },
]

function NavItems({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = usePathname()
  return (
    <nav className="flex flex-col gap-1">
      {nav.map((item) => {
        const active =
          item.href === "/" ? pathname === "/" : pathname.startsWith(item.href)
        const Icon = item.icon
        return (
          <Link
            key={item.href}
            href={item.href}
            onClick={onNavigate}
            className={cn(
              "flex items-center gap-3 rounded-2xl px-3 py-2.5 text-sm font-medium transition-colors",
              active
                ? "glass-strong text-foreground"
                : "text-muted-foreground hover:bg-white/5 hover:text-foreground",
            )}
          >
            <Icon className="size-[18px] shrink-0" />
            {item.label}
          </Link>
        )
      })}
    </nav>
  )
}

function Brand() {
  return (
    <div className="flex items-center gap-3">
      <div className="flex size-10 items-center justify-center rounded-2xl bg-primary/20 text-primary ring-1 ring-primary/30">
        <ShieldCheck className="size-5" />
      </div>
      <div className="leading-tight">
        <p className="text-sm font-semibold">Policy Guardian</p>
        <p className="text-[11px] text-muted-foreground">Conflict Detector</p>
      </div>
    </div>
  )
}

const typeTint: Record<string, string> = {
  Policy: "text-primary bg-primary/15",
  Finding: "text-critical bg-critical/15",
  Owner: "text-success bg-success/15",
  Department: "text-warning bg-warning/15",
  Recommendation: "text-primary bg-primary/15",
}

function GlobalSearch() {
  const router = useRouter()
  const [query, setQuery] = useState("")
  const [open, setOpen] = useState(false)
  const wrapRef = useRef<HTMLDivElement>(null)

  const results = query
    ? searchIndex
        .filter(
          (r) =>
            r.label.toLowerCase().includes(query.toLowerCase()) ||
            r.type.toLowerCase().includes(query.toLowerCase()) ||
            r.meta.toLowerCase().includes(query.toLowerCase()),
        )
        .slice(0, 7)
    : []

  useEffect(() => {
    function onClick(e: MouseEvent) {
      if (wrapRef.current && !wrapRef.current.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener("mousedown", onClick)
    return () => document.removeEventListener("mousedown", onClick)
  }, [])

  const go = (href: string) => {
    setOpen(false)
    setQuery("")
    router.push(href)
  }

  return (
    <div ref={wrapRef} className="relative flex-1">
      <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
      <input
        type="search"
        value={query}
        onChange={(e) => {
          setQuery(e.target.value)
          setOpen(true)
        }}
        onFocus={() => query && setOpen(true)}
        onKeyDown={(e) => {
          if (e.key === "Escape") setOpen(false)
          if (e.key === "Enter" && results[0]) go(results[0].href)
        }}
        placeholder="Search policies, findings, owners, departments…"
        className="h-10 w-full rounded-2xl border border-border bg-white/5 pl-10 pr-4 text-sm outline-none placeholder:text-muted-foreground focus:border-primary/50 focus:bg-white/10"
      />
      {open && query && (
        <div className="glass-strong animate-rise absolute left-0 right-0 top-12 z-50 max-h-96 overflow-auto rounded-2xl p-2">
          {results.length === 0 ? (
            <p className="px-3 py-6 text-center text-sm text-muted-foreground">
              No results for &ldquo;{query}&rdquo;
            </p>
          ) : (
            <ul>
              {results.map((r, i) => (
                <li key={i}>
                  <button
                    onClick={() => go(r.href)}
                    className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left hover:bg-white/10"
                  >
                    <span
                      className={cn(
                        "rounded-lg px-2 py-0.5 text-[10px] font-semibold",
                        typeTint[r.type] ?? "text-muted-foreground bg-white/10",
                      )}
                    >
                      {r.type}
                    </span>
                    <span className="min-w-0 flex-1">
                      <span className="block truncate text-sm font-medium">{r.label}</span>
                      <span className="block truncate text-xs text-muted-foreground">{r.meta}</span>
                    </span>
                    <CornerDownLeft className="size-3.5 text-muted-foreground opacity-0 group-hover:opacity-100" />
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  )
}

const notifIcon = { GitCompareArrows, UploadCloud, CalendarClock, FileBarChart } as const
const notifDot: Record<Severity, string> = {
  critical: "text-critical bg-critical/15",
  warning: "text-warning bg-warning/15",
  healthy: "text-success bg-success/15",
}

function NotificationCenter() {
  const [open, setOpen] = useState(false)
  const [items, setItems] = useState(seedNotifications)
  const wrapRef = useRef<HTMLDivElement>(null)
  const unread = items.filter((n) => n.unread).length

  useEffect(() => {
    function onClick(e: MouseEvent) {
      if (wrapRef.current && !wrapRef.current.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener("mousedown", onClick)
    return () => document.removeEventListener("mousedown", onClick)
  }, [])

  return (
    <div ref={wrapRef} className="relative">
      <button
        onClick={() => setOpen((o) => !o)}
        className="relative rounded-full p-2 text-muted-foreground hover:bg-white/10"
        aria-label="Notifications"
      >
        <Bell className="size-5" />
        {unread > 0 && (
          <span className="absolute right-1 top-1 flex size-4 items-center justify-center rounded-full bg-critical text-[9px] font-bold text-white ring-2 ring-background">
            {unread}
          </span>
        )}
      </button>
      {open && (
        <div className="glass-strong animate-rise absolute right-0 top-12 z-50 w-80 rounded-2xl p-2">
          <div className="flex items-center justify-between px-3 py-2">
            <p className="text-sm font-semibold">Notifications</p>
            <button
              onClick={() => setItems((prev) => prev.map((n) => ({ ...n, unread: false })))}
              className="text-xs font-medium text-primary hover:underline"
            >
              Mark all read
            </button>
          </div>
          <ul className="max-h-96 overflow-auto">
            {items.map((n) => {
              const Icon = notifIcon[n.icon as keyof typeof notifIcon] ?? Bell
              return (
                <li key={n.id}>
                  <div
                    className={cn(
                      "flex items-start gap-3 rounded-xl px-3 py-3 hover:bg-white/5",
                      n.unread && "bg-white/5",
                    )}
                  >
                    <span className={cn("flex size-8 shrink-0 items-center justify-center rounded-xl", notifDot[n.severity])}>
                      <Icon className="size-4" />
                    </span>
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium">{n.title}</p>
                      <p className="truncate text-xs text-muted-foreground">{n.desc}</p>
                      <p className="mt-0.5 text-[11px] text-muted-foreground/70">{n.time}</p>
                    </div>
                    {n.unread && <span className="mt-1 size-2 shrink-0 rounded-full bg-primary" />}
                  </div>
                </li>
              )
            })}
          </ul>
        </div>
      )}
    </div>
  )
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const [mobileOpen, setMobileOpen] = useState(false)

  return (
    <div className="flex min-h-screen">
      {/* Desktop sidebar */}
      <aside className="sticky top-0 hidden h-screen w-64 shrink-0 flex-col gap-6 p-4 lg:flex">
        <div className="glass flex h-full flex-col gap-6 rounded-3xl p-4">
          <div className="px-1 pt-2">
            <Brand />
          </div>
          <NavItems />
          <div className="mt-auto glass-subtle rounded-2xl p-3">
            <p className="text-xs font-medium">Next scan</p>
            <p className="text-[11px] text-muted-foreground">Full audit in 3h 42m</p>
          </div>
        </div>
      </aside>

      {/* Mobile drawer */}
      {mobileOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div
            className="absolute inset-0 bg-black/50 backdrop-blur-sm"
            onClick={() => setMobileOpen(false)}
          />
          <aside className="glass-strong absolute left-0 top-0 h-full w-72 flex-col gap-6 p-5">
            <div className="mb-6 flex items-center justify-between">
              <Brand />
              <button
                onClick={() => setMobileOpen(false)}
                className="rounded-full p-1.5 text-muted-foreground hover:bg-white/10"
                aria-label="Close menu"
              >
                <X className="size-5" />
              </button>
            </div>
            <NavItems onNavigate={() => setMobileOpen(false)} />
          </aside>
        </div>
      )}

      {/* Main column */}
      <div className="flex min-w-0 flex-1 flex-col">
        {/* Top navbar */}
        <header className="sticky top-0 z-40 p-4">
          <div className="glass flex items-center gap-3 rounded-3xl px-3 py-2.5 sm:px-4">
            <button
              onClick={() => setMobileOpen(true)}
              className="rounded-full p-2 text-muted-foreground hover:bg-white/10 lg:hidden"
              aria-label="Open menu"
            >
              <Menu className="size-5" />
            </button>

            <GlobalSearch />

            <button
              className="rounded-full p-2 text-muted-foreground hover:bg-white/10"
              aria-label="Toggle theme"
            >
              <Sun className="size-5" />
            </button>
            <NotificationCenter />
            <button
              className="flex items-center gap-2 rounded-2xl border border-border bg-white/5 py-1 pl-1 pr-3 hover:bg-white/10"
              aria-label="Profile"
            >
              <span className="flex size-8 items-center justify-center rounded-xl bg-primary/25 text-xs font-semibold text-primary">
                AM
              </span>
              <span className="hidden text-sm font-medium sm:block">Alex Morgan</span>
            </button>
          </div>
        </header>

        <main className="flex-1 px-4 pb-10">{children}</main>
      </div>
    </div>
  )
}
