"use client"

import { useState, useEffect, type FormEvent } from "react"
import Link from "next/link"
import Image from "next/image"
import { ShieldCheck, Mail, Lock, ArrowRight, CheckCircle2, Loader2, AlertCircle } from "lucide-react"
import { GlassCard } from "@/components/glass"
import { useAuth, useLogin } from "@/lib/auth-context"
import { useRouter } from "next/navigation"

const highlights = [
  "Automated conflict & staleness detection",
  "Compliance mapping for ISO, SOC 2, GDPR & NIST",
  "Audit-ready reporting in one click",
]

export default function LoginPage() {
  const { login, loading } = useLogin()
  const { user, ready } = useAuth()
  const router = useRouter()

  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [rememberMe, setRememberMe] = useState(false)
  const [fieldErrors, setFieldErrors] = useState<{ email?: string; password?: string }>({})
  const [serverError, setServerError] = useState<string | null>(null)

  // If already authenticated, redirect to dashboard
  useEffect(() => {
    if (ready && user) {
      router.replace("/")
    }
  }, [ready, user, router])

  function validate(): boolean {
    const errors: { email?: string; password?: string } = {}
    if (!email.trim()) {
      errors.email = "Email is required."
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) {
      errors.email = "Enter a valid email address."
    }
    if (!password) {
      errors.password = "Password is required."
    } else if (password.length < 6) {
      errors.password = "Password must be at least 6 characters."
    }
    setFieldErrors(errors)
    return Object.keys(errors).length === 0
  }

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setServerError(null)

    if (!validate()) return

    try {
      await login({ email: email.trim(), password })
      // AuthContext.login handles the redirect to "/"
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "An unexpected error occurred."
      setServerError(msg)
    }
  }

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

          {/* Server / backend error banner */}
          {serverError && (
            <div className="mt-5 flex items-start gap-2 rounded-2xl border border-critical/30 bg-critical/10 px-4 py-3 text-sm text-critical">
              <AlertCircle className="mt-0.5 size-4 shrink-0" />
              <span>{serverError}</span>
            </div>
          )}

          <form className="mt-8 space-y-5" onSubmit={handleSubmit} noValidate>
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
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value)
                    if (fieldErrors.email) setFieldErrors((f) => ({ ...f, email: undefined }))
                    setServerError(null)
                  }}
                  disabled={loading}
                  aria-invalid={!!fieldErrors.email}
                  aria-describedby={fieldErrors.email ? "email-error" : undefined}
                  className={`h-11 w-full rounded-2xl border bg-white/5 pl-10 pr-4 text-sm outline-none placeholder:text-muted-foreground focus:bg-white/10 disabled:cursor-not-allowed disabled:opacity-50 ${
                    fieldErrors.email
                      ? "border-critical/50 focus:border-critical/70"
                      : "border-border focus:border-primary/50"
                  }`}
                />
              </div>
              {fieldErrors.email && (
                <p id="email-error" className="flex items-center gap-1 text-xs text-critical">
                  <AlertCircle className="size-3 shrink-0" />
                  {fieldErrors.email}
                </p>
              )}
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
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value)
                    if (fieldErrors.password) setFieldErrors((f) => ({ ...f, password: undefined }))
                    setServerError(null)
                  }}
                  disabled={loading}
                  aria-invalid={!!fieldErrors.password}
                  aria-describedby={fieldErrors.password ? "password-error" : undefined}
                  className={`h-11 w-full rounded-2xl border bg-white/5 pl-10 pr-4 text-sm outline-none placeholder:text-muted-foreground focus:bg-white/10 disabled:cursor-not-allowed disabled:opacity-50 ${
                    fieldErrors.password
                      ? "border-critical/50 focus:border-critical/70"
                      : "border-border focus:border-primary/50"
                  }`}
                />
              </div>
              {fieldErrors.password && (
                <p id="password-error" className="flex items-center gap-1 text-xs text-critical">
                  <AlertCircle className="size-3 shrink-0" />
                  {fieldErrors.password}
                </p>
              )}
            </div>

            <label className="flex cursor-pointer items-center gap-2 text-sm text-muted-foreground">
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                disabled={loading}
                className="size-4 rounded-md border-border bg-white/5 accent-primary disabled:cursor-not-allowed"
              />
              Remember me for 30 days
            </label>

            <button
              type="submit"
              disabled={loading}
              className="flex h-11 w-full items-center justify-center gap-2 rounded-2xl bg-primary text-sm font-semibold text-primary-foreground shadow-lg shadow-primary/30 transition-colors hover:bg-primary/90 disabled:cursor-not-allowed disabled:opacity-70"
            >
              {loading ? (
                <>
                  <Loader2 className="size-4 animate-spin" />
                  Signing in…
                </>
              ) : (
                <>
                  Sign in
                  <ArrowRight className="size-4" />
                </>
              )}
            </button>
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
