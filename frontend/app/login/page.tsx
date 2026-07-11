import Link from "next/link"
import Image from "next/image"
import { ShieldCheck, Mail, Lock, ArrowRight, CheckCircle2 } from "lucide-react"
import { GlassCard } from "@/components/glass"

const highlights = [
  "Automated conflict & staleness detection",
  "Compliance mapping for ISO, SOC 2, GDPR & NIST",
  "Audit-ready reporting in one click",
]

export default function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <GlassCard strong className="grid w-full max-w-5xl overflow-hidden lg:grid-cols-2">
        {/* Hero side */}
        <div className="relative hidden flex-col justify-between p-10 lg:flex">
          <div className="flex items-center gap-3">
            <div className="flex size-10 items-center justify-center rounded-2xl bg-primary/20 text-primary ring-1 ring-primary/30">
              <ShieldCheck className="size-5" />
            </div>
            <span className="text-sm font-semibold">Policy Guardian</span>
          </div>

          <div className="relative my-6 aspect-square w-full">
            <Image
              src="/security-hero.png"
              alt="Illustration of a glowing shield protecting connected policy documents"
              fill
              className="rounded-3xl object-cover"
              priority
            />
          </div>

          <div>
            <h2 className="text-balance text-2xl font-semibold leading-tight">
              Govern every policy with confidence.
            </h2>
            <ul className="mt-4 space-y-2">
              {highlights.map((h) => (
                <li key={h} className="flex items-center gap-2 text-sm text-muted-foreground">
                  <CheckCircle2 className="size-4 shrink-0 text-success" />
                  {h}
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Form side */}
        <div className="flex flex-col justify-center p-8 sm:p-12">
          <div className="mb-8 flex items-center gap-3 lg:hidden">
            <div className="flex size-10 items-center justify-center rounded-2xl bg-primary/20 text-primary ring-1 ring-primary/30">
              <ShieldCheck className="size-5" />
            </div>
            <span className="text-sm font-semibold">Policy Guardian</span>
          </div>

          <h1 className="text-2xl font-semibold">Welcome back</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Sign in to your organization workspace.
          </p>

          <form className="mt-8 space-y-5">
            <div className="space-y-2">
              <label htmlFor="email" className="text-sm font-medium">
                Email address
              </label>
              <div className="relative">
                <Mail className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
                <input
                  id="email"
                  type="email"
                  autoComplete="email"
                  placeholder="you@company.com"
                  className="h-11 w-full rounded-2xl border border-border bg-white/5 pl-10 pr-4 text-sm outline-none placeholder:text-muted-foreground focus:border-primary/50 focus:bg-white/10"
                />
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label htmlFor="password" className="text-sm font-medium">
                  Password
                </label>
                <Link href="#" className="text-xs font-medium text-primary hover:underline">
                  Forgot password?
                </Link>
              </div>
              <div className="relative">
                <Lock className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
                <input
                  id="password"
                  type="password"
                  autoComplete="current-password"
                  placeholder="••••••••"
                  className="h-11 w-full rounded-2xl border border-border bg-white/5 pl-10 pr-4 text-sm outline-none placeholder:text-muted-foreground focus:border-primary/50 focus:bg-white/10"
                />
              </div>
            </div>

            <label className="flex cursor-pointer items-center gap-2 text-sm text-muted-foreground">
              <input
                type="checkbox"
                className="size-4 rounded-md border-border bg-white/5 accent-primary"
              />
              Remember me for 30 days
            </label>

            <Link
              href="/"
              className="flex h-11 w-full items-center justify-center gap-2 rounded-2xl bg-primary text-sm font-semibold text-primary-foreground shadow-lg shadow-primary/30 transition-colors hover:bg-primary/90"
            >
              Sign in
              <ArrowRight className="size-4" />
            </Link>
          </form>

          <p className="mt-6 text-center text-sm text-muted-foreground">
            Need an account?{" "}
            <Link href="#" className="font-medium text-primary hover:underline">
              Contact your administrator
            </Link>
          </p>
        </div>
      </GlassCard>
    </div>
  )
}
