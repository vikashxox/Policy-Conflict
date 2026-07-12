"use client"

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from "react"
import { useRouter } from "next/navigation"
import {
  login as apiLogin,
  getMe,
  clearToken,
  type TokenResponse,
} from "@/lib/api"

// ─── Types ──────────────────────────────────────────────────────────────────

export type AuthUser = TokenResponse["user"]

export interface AuthState {
  user: AuthUser | null
  /** true while the initial /me check is running */
  loading: boolean
  /** true once the initial check has completed (success or failure) */
  ready: boolean
  error: string | null
}

export interface AuthContextValue extends AuthState {
  login: (credentials: { email?: string; username?: string; password: string }) => Promise<void>
  logout: () => void
}

// ─── Context ─────────────────────────────────────────────────────────────────

const AuthContext = createContext<AuthContextValue | null>(null)

// ─── Provider ────────────────────────────────────────────────────────────────

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const [state, setState] = useState<AuthState>({
    user: null,
    loading: true,
    ready: false,
    error: null,
  })

  // Track mount to avoid setState after unmount
  const mounted = useRef(true)
  useEffect(() => {
    mounted.current = true
    return () => { mounted.current = false }
  }, [])

  // ── Session persistence: check token on app load ─────────────────────────
  useEffect(() => {
    let cancelled = false

    async function checkSession() {
      const token =
        typeof window !== "undefined"
          ? localStorage.getItem("policy_guardian_token")
          : null

      if (!token) {
        if (!cancelled && mounted.current) {
          setState({ user: null, loading: false, ready: true, error: null })
        }
        return
      }

      try {
        const data = await getMe()
        if (!cancelled && mounted.current) {
          setState({ user: data.user, loading: false, ready: true, error: null })
        }
      } catch {
        // Token invalid / expired / 401 -- clear it and treat as logged out
        clearToken()
        if (!cancelled && mounted.current) {
          setState({ user: null, loading: false, ready: true, error: null })
        }
      }
    }

    checkSession()
    return () => { cancelled = true }
  }, [])

  // ── Login ─────────────────────────────────────────────────────────────────
  const login = useCallback(
    async (credentials: { email?: string; username?: string; password: string }) => {
      setState((s) => ({ ...s, loading: true, error: null }))
      try {
        const payload: { email: string; password: string } | { username: string; password: string } =
          credentials.email
            ? { email: credentials.email, password: credentials.password }
            : { username: credentials.username!, password: credentials.password }

        const result = await apiLogin(payload)
        if (mounted.current) {
          setState({ user: result.user, loading: false, ready: true, error: null })
          router.push("/")
        }
      } catch (err: unknown) {
        const raw = err instanceof Error ? err.message : "Login failed"
        let message = raw
        // Try to parse JSON error bodies from FastAPI
        try {
          const parsed = JSON.parse(raw)
          message = parsed?.detail ?? raw
        } catch {
          // not JSON, keep raw
        }
        if (mounted.current) {
          setState((s) => ({ ...s, loading: false, error: message }))
        }
        throw new Error(message)
      }
    },
    [router],
  )

  // ── Logout ────────────────────────────────────────────────────────────────
  const logout = useCallback(() => {
    clearToken()
    setState({ user: null, loading: false, ready: true, error: null })
    router.push("/login")
  }, [router])

  return (
    <AuthContext.Provider value={{ ...state, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

// ─── Hooks ───────────────────────────────────────────────────────────────────

/**
 * Access auth state and actions from any client component.
 */
export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) {
    throw new Error("useAuth must be used inside <AuthProvider>")
  }
  return ctx
}

/**
 * Convenience hook: returns the login function and its in-flight/error state.
 */
export function useLogin() {
  const { login, loading, error } = useAuth()
  return { login, loading, error }
}

/**
 * Convenience hook: returns the logout function.
 */
export function useLogout() {
  const { logout } = useAuth()
  return logout
}
