"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/lib/auth-context"

/**
 * Wraps authenticated routes. While the session check is pending it renders
 * nothing (avoids flash of protected content). Once ready, unauthenticated
 * users are redirected to /login.
 */
export function AuthGuard({ children }: { children: React.ReactNode }) {
  const { ready, user } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (ready && !user) {
      router.replace("/login")
    }
  }, [ready, user, router])

  // While checking session, render nothing (no flash)
  if (!ready) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <span className="size-8 animate-spin rounded-full border-2 border-primary border-t-transparent" />
      </div>
    )
  }

  // Not authenticated — render nothing while redirect happens
  if (!user) return null

  return <>{children}</>
}
