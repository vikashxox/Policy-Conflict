// ─── Shared types ────────────────────────────────────────────────────────────
export type Severity = "critical" | "warning" | "healthy"
export type FindingStatus = "open" | "in-review" | "resolved"
export type Trend = "up" | "down"

// ─── KPI metrics ─────────────────────────────────────────────────────────────
export const kpis = {
  totalPolicies: 0,
  activePolicies: 0,
  conflicts: 0,
  duplicates: 0,
  stale: 0,
  healthScore: 0,
  complianceScore: 0,
}

export const org = {
  name: "",
  admin: "",
  lastAnalysis: "—",
  lastUpload: "—",
}

export type KpiMetric = {
  label: string
  value: number
  suffix?: string
  icon: string
  tint: string
  trend: Trend
  change: string
  good: Trend
  spark: number[]
}
export const kpiMetrics: KpiMetric[] = []

// ─── Chart data ───────────────────────────────────────────────────────────────
export const healthBreakdown: { label: string; value: number; color: string }[] = []
export const policiesByCategory: { category: string; count: number }[] = []
export const healthTrend: { label: string; value: number }[] = []
export const conflictTrend: { label: string; value: number }[] = []
export const complianceDistribution: { label: string; value: number; color: string }[] = []

export type Framework = { name: string; score: number; controls: string }
export const complianceFrameworks: Framework[] = []

// ─── AI insights ─────────────────────────────────────────────────────────────
export type AiInsight = {
  id: string
  severity: Severity
  text: string
  icon: string
}
export const aiInsights: AiInsight[] = []
export const aiRecommendation = ""

// ─── Findings ────────────────────────────────────────────────────────────────
export type Finding = {
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
export const findings: Finding[] = []

// ─── Policies ────────────────────────────────────────────────────────────────
export type Policy = {
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
  status: "active" | "draft" | "archived"
  summary: string
}
export const policies: Policy[] = []

export type PolicyEvent = { time: string; label: string; detail: string; severity: Severity }
export const policyTimeline: PolicyEvent[] = []

// ─── Uploads ─────────────────────────────────────────────────────────────────
export type Upload = {
  id: string
  name: string
  size: string
  type: "PDF" | "DOCX" | "TXT" | "MD"
  status: "complete" | "processing" | "queued"
  progress: number
  time: string
}
export const recentUploads: Upload[] = []

export const pipelineStages = [
  { key: "parsing",    label: "Parsing document",         icon: "FileSearch" },
  { key: "extracting", label: "Extracting obligations",   icon: "ListChecks" },
  { key: "conflict",   label: "Conflict detection",       icon: "GitCompareArrows" },
  { key: "report",     label: "Generating report",        icon: "FileBarChart" },
]

// ─── Activity ────────────────────────────────────────────────────────────────
export type Activity = {
  id: string
  actor: string
  action: string
  target: string
  time: string
  severity: Severity
}
export const activity: Activity[] = []

export const uploadTimeline: { time: string; label: string; severity: Severity }[] = []

// ─── Notifications ───────────────────────────────────────────────────────────
export type Notification = {
  id: string
  title: string
  desc: string
  time: string
  severity: Severity
  icon: string
  unread: boolean
}
export const notifications: Notification[] = []

// ─── Obligations ─────────────────────────────────────────────────────────────
export const obligations: string[] = []

// ─── Reports ─────────────────────────────────────────────────────────────────
export const reports: {
  id: string
  title: string
  desc: string
  accent: string
  updated: string
  pages: number
}[] = []

// ─── Policy relationship graph ───────────────────────────────────────────────
export type GraphNode = { id: string; label: string; x: number; y: number; severity: Severity }
export type GraphLink = { from: string; to: string; kind: "conflict" | "recommendation" }

export const graphNodes: GraphNode[] = []
export const graphLinks: GraphLink[] = []

// ─── Search index (derived — empty until data is loaded from backend) ────────
export const searchIndex: {
  type: string
  label: string
  href: string
  meta: string
}[] = []
