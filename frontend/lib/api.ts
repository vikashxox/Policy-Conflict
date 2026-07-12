const TOKEN_KEY = "policy_guardian_token"
const DEFAULT_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000"

export type Severity = "critical" | "warning" | "healthy"
export type FindingStatus = "open" | "in-review" | "resolved"
export type PolicyStatus = "active" | "draft" | "archived"
export type UploadStatus = "complete" | "processing" | "queued"

export interface PolicySummary {
  id: string
  name: string
  category: string
  owner: string
  department: string
  version: string
  effectiveDate: string
  lastReviewed: string
  health: number
  severity: Severity
  status: PolicyStatus
  summary: string
}

export interface FindingSummary {
  id: string
  severity: Severity
  type: string
  policyA: string
  policyB: string
  section: string
  confidence: number
  description: string
  recommendation: string
  compliance: string
  status: FindingStatus
  category: string
}

export interface DashboardResponse {
  organization: {
    name: string
    admin: string
    lastAnalysis: string
    lastUpload: string
  }
  kpis: {
    totalPolicies: number
    activePolicies: number
    conflicts: number
    duplicates: number
    stale: number
    healthScore: number
    complianceScore: number
  }
  kpiMetrics: Array<{
    label: string
    value: number
    suffix?: string
    icon: string
    tint: string
    trend: "up" | "down"
    change: string
    good: "up" | "down"
    spark: number[]
  }>
  healthBreakdown: Array<{ label: string; value: number; color: string }>
  policiesByCategory: Array<{ category: string; count: number }>
  healthTrend: Array<{ label: string; value: number }>
  conflictTrend: Array<{ label: string; value: number }>
  complianceDistribution: Array<{ label: string; value: number; color: string }>
  complianceFrameworks: Array<{ name: string; score: number; controls: string }>
  aiInsights: Array<{ id: string; severity: Severity; text: string; icon: string }>
  aiRecommendation: string
  findings: FindingSummary[]
  recentUploads: UploadItem[]
  activity: Array<{
    id: string
    actor: string
    action: string
    target: string
    time: string
    severity: Severity
  }>
  graphNodes: GraphNode[]
  graphLinks: GraphLink[]
}

export interface PolicyDetailResponse extends PolicySummary {
  obligations: string[]
  relatedFindings: FindingSummary[]
}

export interface UploadItem {
  id: string
  name: string
  size: string
  type: "PDF" | "DOCX" | "TXT" | "MD"
  status: UploadStatus
  progress: number
  time: string
}

export interface ReportSummary {
  id: string
  title: string
  desc: string
  format: string
  updated: string
  pages: number
  download_url: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  user: {
    id: number
    username: string
    email?: string | null
    name?: string | null
    role?: string | null
  }
}

export interface GraphNode {
  id: string
  label: string
  x: number
  y: number
  severity: Severity
}

export interface GraphLink {
  from: string
  to: string
  kind: "conflict" | "recommendation"
}

function buildUrl(path: string) {
  const base = DEFAULT_BASE_URL.replace(/\/$/, "")
  return `${base}${path.startsWith("/") ? path : `/${path}`}`
}

function getToken() {
  if (typeof window === "undefined") return null
  return window.localStorage.getItem(TOKEN_KEY)
}

function setToken(token: string) {
  if (typeof window !== "undefined") {
    window.localStorage.setItem(TOKEN_KEY, token)
  }
}

export function clearToken() {
  if (typeof window !== "undefined") {
    window.localStorage.removeItem(TOKEN_KEY)
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers ?? {})
  const token = getToken()

  if (token) {
    headers.set("Authorization", `Bearer ${token}`)
  }

  if (init.body && !(init.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json")
  }

  let response: Response
  try {
    response = await fetch(buildUrl(path), { ...init, headers })
  } catch {
    throw new Error("Network error: unable to reach the server.")
  }

  if (!response.ok) {
    const text = await response.text().catch(() => "")
    // FastAPI returns JSON { detail: string } for most errors
    try {
      const json = JSON.parse(text)
      const detail =
        typeof json?.detail === "string"
          ? json.detail
          : Array.isArray(json?.detail)
            ? json.detail.map((d: { msg: string }) => d.msg).join(", ")
            : text || `Request failed with status ${response.status}`
      throw new Error(detail)
    } catch (e) {
      if (e instanceof Error && e.message !== text) throw e
      throw new Error(text || `Request failed with status ${response.status}`)
    }
  }

  if (response.status === 204) {
    return {} as T
  }

  return (await response.json()) as T
}

export async function login(
  payload:
    | { email: string; password: string }
    | { username: string; password: string },
) {
  const result = await request<TokenResponse>("/api/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
  })
  setToken(result.access_token)
  return result
}

export async function getMe() {
  return request<{ user: TokenResponse["user"] }>("/api/auth/me")
}

export async function getDashboard() {
  return request<DashboardResponse>("/api/dashboard")
}

export async function listPolicies() {
  return request<PolicySummary[]>("/api/policies")
}

export async function getPolicy(policyId: string) {
  return request<PolicyDetailResponse>(`/api/policies/${policyId}`)
}

export async function listFindings() {
  return request<FindingSummary[]>("/api/findings")
}

export async function listReports() {
  return request<{ reports: ReportSummary[] }>("/api/reports")
}

export async function uploadPolicyFile(file: File) {
  const formData = new FormData()
  formData.append("file", file)
  return request<UploadItem>("/api/upload", {
    method: "POST",
    body: formData,
  })
}
