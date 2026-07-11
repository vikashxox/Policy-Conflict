"use client"

import { useState } from "react"
import { Building2, Bell, CalendarClock, Palette, Check } from "lucide-react"
import { GlassCard } from "@/components/glass"
import { PageHeader } from "@/components/page-header"
import { cn } from "@/lib/utils"

function Toggle({ on, onToggle }: { on: boolean; onToggle: () => void }) {
  return (
    <button
      onClick={onToggle}
      role="switch"
      aria-checked={on}
      className={cn(
        "relative h-6 w-11 shrink-0 rounded-full transition-colors",
        on ? "bg-primary" : "bg-white/15",
      )}
    >
      <span
        className={cn(
          "absolute top-0.5 size-5 rounded-full bg-white transition-transform",
          on ? "translate-x-[22px]" : "translate-x-0.5",
        )}
      />
    </button>
  )
}

function Field({ label, defaultValue }: { label: string; defaultValue: string }) {
  return (
    <label className="flex flex-col gap-1.5">
      <span className="text-xs text-muted-foreground">{label}</span>
      <input
        defaultValue={defaultValue}
        className="h-10 rounded-2xl border border-border bg-white/5 px-3 text-sm outline-none focus:border-primary/50 focus:bg-white/10"
      />
    </label>
  )
}

const notifPrefs = [
  { key: "critical", label: "Critical conflicts", desc: "Immediate alert when a critical conflict is found." },
  { key: "stale", label: "Stale policy reminders", desc: "Notify when a policy exceeds its review window." },
  { key: "weekly", label: "Weekly digest", desc: "Summary of new findings every Monday." },
]

const themes = [
  { key: "dark", label: "Frosted Dark", swatch: "from-[#0b1020] to-[#1b2447]" },
  { key: "midnight", label: "Midnight Blue", swatch: "from-[#050914] to-[#122a4d]" },
  { key: "aurora", label: "Aurora", swatch: "from-[#0b1020] to-[#1a3a3a]" },
]

export default function SettingsPage() {
  const [notifs, setNotifs] = useState<Record<string, boolean>>({
    critical: true,
    stale: true,
    weekly: false,
  })
  const [schedule, setSchedule] = useState("quarterly")
  const [theme, setTheme] = useState("dark")

  return (
    <div className="max-w-4xl">
      <PageHeader title="Settings" subtitle="Manage your organization and preferences." />

      <div className="space-y-4">
        {/* Organization profile */}
        <GlassCard className="p-6">
          <div className="mb-5 flex items-center gap-2">
            <Building2 className="size-4 text-primary" />
            <h3 className="text-sm font-medium">Organization Profile</h3>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="Organization name" defaultValue="Northwind Security Corp" />
            <Field label="Primary contact" defaultValue="Alex Morgan" />
            <Field label="Contact email" defaultValue="governance@northwind.com" />
            <Field label="Industry" defaultValue="Financial Services" />
          </div>
        </GlassCard>

        {/* Notifications */}
        <GlassCard className="p-6">
          <div className="mb-5 flex items-center gap-2">
            <Bell className="size-4 text-primary" />
            <h3 className="text-sm font-medium">Notification Preferences</h3>
          </div>
          <ul className="space-y-4">
            {notifPrefs.map((p) => (
              <li key={p.key} className="flex items-center justify-between gap-4">
                <div>
                  <p className="text-sm font-medium">{p.label}</p>
                  <p className="text-xs text-muted-foreground">{p.desc}</p>
                </div>
                <Toggle
                  on={notifs[p.key]}
                  onToggle={() => setNotifs((s) => ({ ...s, [p.key]: !s[p.key] }))}
                />
              </li>
            ))}
          </ul>
        </GlassCard>

        {/* Review schedule */}
        <GlassCard className="p-6">
          <div className="mb-5 flex items-center gap-2">
            <CalendarClock className="size-4 text-primary" />
            <h3 className="text-sm font-medium">Review Schedule</h3>
          </div>
          <div className="flex flex-wrap gap-2">
            {["monthly", "quarterly", "biannual", "annual"].map((s) => (
              <button
                key={s}
                onClick={() => setSchedule(s)}
                className={cn(
                  "rounded-2xl border px-4 py-2 text-sm font-medium capitalize transition-colors",
                  schedule === s
                    ? "border-primary/50 bg-primary/15 text-primary"
                    : "border-border bg-white/5 text-muted-foreground hover:bg-white/10",
                )}
              >
                {s}
              </button>
            ))}
          </div>
        </GlassCard>

        {/* Theme selector */}
        <GlassCard className="p-6">
          <div className="mb-5 flex items-center gap-2">
            <Palette className="size-4 text-primary" />
            <h3 className="text-sm font-medium">Theme</h3>
          </div>
          <div className="grid gap-3 sm:grid-cols-3">
            {themes.map((t) => (
              <button
                key={t.key}
                onClick={() => setTheme(t.key)}
                className={cn(
                  "relative overflow-hidden rounded-2xl border p-1 text-left transition-colors",
                  theme === t.key ? "border-primary" : "border-border hover:border-white/30",
                )}
              >
                <div className={cn("h-20 rounded-xl bg-gradient-to-br", t.swatch)} />
                <p className="px-2 py-2 text-sm font-medium">{t.label}</p>
                {theme === t.key && (
                  <span className="absolute right-2 top-2 flex size-5 items-center justify-center rounded-full bg-primary text-primary-foreground">
                    <Check className="size-3" />
                  </span>
                )}
              </button>
            ))}
          </div>
        </GlassCard>

        <div className="flex justify-end">
          <button className="h-10 rounded-2xl bg-primary px-6 text-sm font-semibold text-primary-foreground shadow-lg shadow-primary/30 hover:bg-primary/90">
            Save changes
          </button>
        </div>
      </div>
    </div>
  )
}
