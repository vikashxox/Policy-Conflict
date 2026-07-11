export type Severity = "critical" | "warning" | "healthy"
export type FindingStatus = "open" | "in-review" | "resolved"

export const kpis = {
  totalPolicies: 248,
  activePolicies: 213,
  conflicts: 17,
  duplicates: 9,
  stale: 24,
  healthScore: 82,
  complianceScore: 88,
}

export const org = {
  name: "Northwind Security Corp",
  admin: "Alex Morgan",
  lastAnalysis: "Today, 09:35 AM",
  lastUpload: "Access-Control-Standard-2026.pdf",
}

export type Trend = "up" | "down"

export type KpiMetric = {
  label: string
  value: number
  suffix?: string
  icon: string
  tint: string
  trend: Trend
  change: string
  good: Trend // which trend direction is positive
  spark: number[]
}

// Sparkline series + trend metadata for KPI cards
export const kpiMetrics: KpiMetric[] = [
  {
    label: "Total Policies",
    value: 248,
    icon: "FileText",
    tint: "text-primary bg-primary/15",
    trend: "up",
    change: "+12",
    good: "up",
    spark: [210, 218, 222, 229, 233, 240, 244, 248],
  },
  {
    label: "Healthy Policies",
    value: 187,
    icon: "ShieldCheck",
    tint: "text-success bg-success/15",
    trend: "up",
    change: "+8%",
    good: "up",
    spark: [150, 158, 162, 168, 171, 178, 182, 187],
  },
  {
    label: "Critical Conflicts",
    value: 17,
    icon: "GitCompareArrows",
    tint: "text-critical bg-critical/15",
    trend: "down",
    change: "-4",
    good: "down",
    spark: [28, 26, 24, 23, 21, 20, 18, 17],
  },
  {
    label: "Duplicate Rules",
    value: 9,
    icon: "Copy",
    tint: "text-warning bg-warning/15",
    trend: "down",
    change: "-2",
    good: "down",
    spark: [16, 15, 14, 13, 12, 11, 10, 9],
  },
  {
    label: "Stale Policies",
    value: 24,
    icon: "Clock",
    tint: "text-warning bg-warning/15",
    trend: "down",
    change: "-6",
    good: "down",
    spark: [36, 34, 33, 31, 29, 27, 25, 24],
  },
  {
    label: "Compliance Score",
    value: 88,
    suffix: "%",
    icon: "BadgeCheck",
    tint: "text-primary bg-primary/15",
    trend: "up",
    change: "+3%",
    good: "up",
    spark: [78, 80, 81, 83, 84, 85, 87, 88],
  },
]

export const healthBreakdown = [
  { label: "Healthy", value: 187, color: "var(--color-success)" },
  { label: "Conflict", value: 37, color: "var(--color-critical)" },
  { label: "Stale", value: 24, color: "var(--color-warning)" },
]

export const policiesByCategory = [
  { category: "Access Control", count: 52 },
  { category: "Data Privacy", count: 44 },
  { category: "Incident Resp.", count: 31 },
  { category: "Network", count: 38 },
  { category: "HR & Conduct", count: 27 },
  { category: "Vendor Risk", count: 21 },
  { category: "Encryption", count: 35 },
]

// Monthly trend series
export const healthTrend = [
  { label: "Jan", value: 68 },
  { label: "Feb", value: 71 },
  { label: "Mar", value: 70 },
  { label: "Apr", value: 74 },
  { label: "May", value: 78 },
  { label: "Jun", value: 80 },
  { label: "Jul", value: 82 },
]

export const conflictTrend = [
  { label: "Jan", value: 31 },
  { label: "Feb", value: 28 },
  { label: "Mar", value: 26 },
  { label: "Apr", value: 24 },
  { label: "May", value: 21 },
  { label: "Jun", value: 19 },
  { label: "Jul", value: 17 },
]

export const complianceDistribution = [
  { label: "Compliant", value: 172, color: "var(--color-success)" },
  { label: "Partial", value: 54, color: "var(--color-warning)" },
  { label: "Non-Compliant", value: 22, color: "var(--color-critical)" },
]

export type Framework = { name: string; score: number; controls: string }
export const complianceFrameworks: Framework[] = [
  { name: "ISO 27001", score: 92, controls: "114 controls" },
  { name: "GDPR", score: 84, controls: "99 articles" },
  { name: "NIST CSF", score: 78, controls: "108 subcategories" },
  { name: "SOC 2", score: 90, controls: "64 criteria" },
]

export type AiInsight = {
  id: string
  severity: Severity
  text: string
  icon: string
}
export const aiInsights: AiInsight[] = [
  { id: "AI-1", severity: "critical", text: "3 critical policy conflicts detected across Access Control", icon: "GitCompareArrows" },
  { id: "AI-2", severity: "warning", text: "2 policies are older than 24 months and reference deprecated tooling", icon: "Clock" },
  { id: "AI-3", severity: "warning", text: "5 duplicate obligations found spanning Vendor Risk policies", icon: "Copy" },
  { id: "AI-4", severity: "critical", text: "1 high-risk compliance issue affecting GDPR breach disclosure", icon: "ShieldAlert" },
]
export const aiRecommendation =
  "Update the Password Rotation Policy to align with NIST 800-63B before the next audit window."

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

export const findings: Finding[] = [
  {
    id: "F-1042",
    severity: "critical",
    type: "Direct Conflict",
    policyA: "Password Rotation Policy v4.2",
    policyB: "Zero-Trust Access Standard v2.0",
    section: "§4.1 Credential Lifecycle",
    confidence: 96,
    description:
      "Password rotation mandates 30-day cycles while the zero-trust standard prohibits periodic rotation without cause.",
    recommendation: "Align rotation cadence with NIST 800-63B; remove forced periodic rotation.",
    compliance: "NIST 800-63B, ISO 27001 A.9",
    status: "open",
    category: "Access Control",
  },
  {
    id: "F-1039",
    severity: "critical",
    type: "Obligation Overlap",
    policyA: "Data Retention Policy v3.1",
    policyB: "GDPR Data Handling v1.8",
    section: "§2.3 Retention Windows",
    confidence: 91,
    description: "Retention windows differ (7 years vs. 'minimum necessary') for EU customer PII.",
    recommendation: "Adopt shortest compliant retention window for EU-resident data.",
    compliance: "GDPR Art. 5, ISO 27701",
    status: "in-review",
    category: "Data Privacy",
  },
  {
    id: "F-1031",
    severity: "warning",
    type: "Stale Policy",
    policyA: "Remote Work Security v1.2",
    policyB: "—",
    section: "§6 Endpoint Requirements",
    confidence: 88,
    description: "Policy last reviewed 19 months ago; references deprecated VPN client.",
    recommendation: "Schedule review and update endpoint requirements.",
    compliance: "SOC 2 CC6.6",
    status: "open",
    category: "Network",
  },
  {
    id: "F-1028",
    severity: "warning",
    type: "Duplicate Obligation",
    policyA: "Vendor Onboarding v2.4",
    policyB: "Third-Party Risk Mgmt v1.1",
    section: "§3.2 Security Questionnaire",
    confidence: 82,
    description: "Both policies define identical vendor security questionnaire requirements.",
    recommendation: "Consolidate into a single authoritative source.",
    compliance: "ISO 27036",
    status: "in-review",
    category: "Vendor Risk",
  },
  {
    id: "F-1019",
    severity: "healthy",
    type: "Resolved Conflict",
    policyA: "Encryption at Rest v5.0",
    policyB: "Key Management Standard v3.2",
    section: "§5.1 Key Rotation",
    confidence: 99,
    description: "Previously mismatched key rotation intervals, now aligned to 90 days.",
    recommendation: "No action required. Monitor at next review cycle.",
    compliance: "FIPS 140-3, ISO 27001 A.10",
    status: "resolved",
    category: "Encryption",
  },
  {
    id: "F-1014",
    severity: "critical",
    type: "Direct Conflict",
    policyA: "Incident Notification v2.2",
    policyB: "Breach Disclosure Policy v1.5",
    section: "§1.4 Regulator Notice",
    confidence: 94,
    description: "Notification windows conflict: 24 hours vs. 72 hours for regulator disclosure.",
    recommendation: "Standardize to the strictest regulatory requirement (24h).",
    compliance: "GDPR Art. 33, HIPAA",
    status: "open",
    category: "Incident Resp.",
  },
  {
    id: "F-1008",
    severity: "warning",
    type: "Stale Policy",
    policyA: "Acceptable Use Policy v1.0",
    policyB: "—",
    section: "§1 Scope",
    confidence: 79,
    description: "No review in 24 months; predates current SaaS toolset.",
    recommendation: "Full rewrite recommended.",
    compliance: "SOC 2 CC1.1",
    status: "open",
    category: "HR & Conduct",
  },
]

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

export const policies: Policy[] = [
  {
    id: "P-001",
    name: "Zero-Trust Access Standard",
    category: "Access Control",
    owner: "Dana Whitmore",
    department: "Security Engineering",
    version: "v2.0",
    effectiveDate: "2026-01-10",
    lastReviewed: "2026-05-14",
    health: 94,
    severity: "healthy",
    status: "active",
    summary:
      "Establishes continuous verification for all access requests, removing implicit trust from the corporate network and enforcing least-privilege by default.",
  },
  {
    id: "P-002",
    name: "Password Rotation Policy",
    category: "Access Control",
    owner: "Dana Whitmore",
    department: "Security Engineering",
    version: "v4.2",
    effectiveDate: "2024-06-01",
    lastReviewed: "2025-11-02",
    health: 48,
    severity: "critical",
    status: "active",
    summary:
      "Defines credential rotation cadence and complexity requirements. Currently conflicts with the Zero-Trust Access Standard on periodic rotation.",
  },
  {
    id: "P-003",
    name: "GDPR Data Handling",
    category: "Data Privacy",
    owner: "Priya Raman",
    department: "Legal & Compliance",
    version: "v1.8",
    effectiveDate: "2025-09-15",
    lastReviewed: "2026-03-20",
    health: 71,
    severity: "warning",
    status: "active",
    summary:
      "Governs collection, processing and retention of EU-resident personal data in line with GDPR principles of data minimization and purpose limitation.",
  },
  {
    id: "P-004",
    name: "Remote Work Security",
    category: "Network",
    owner: "Marcus Lee",
    department: "IT Operations",
    version: "v1.2",
    effectiveDate: "2023-08-01",
    lastReviewed: "2024-10-11",
    health: 58,
    severity: "warning",
    status: "active",
    summary:
      "Sets minimum security controls for employees working outside the corporate perimeter. Flagged as stale with deprecated VPN client references.",
  },
  {
    id: "P-005",
    name: "Encryption at Rest",
    category: "Encryption",
    owner: "Sofia Alvarez",
    department: "Security Engineering",
    version: "v5.0",
    effectiveDate: "2026-02-01",
    lastReviewed: "2026-06-01",
    health: 96,
    severity: "healthy",
    status: "active",
    summary:
      "Mandates FIPS 140-3 validated encryption for all data at rest with a harmonized 90-day key rotation cycle aligned to the Key Management Standard.",
  },
  {
    id: "P-006",
    name: "Incident Notification",
    category: "Incident Resp.",
    owner: "Marcus Lee",
    department: "IT Operations",
    version: "v2.2",
    effectiveDate: "2025-12-01",
    lastReviewed: "2026-01-18",
    health: 52,
    severity: "critical",
    status: "active",
    summary:
      "Specifies regulator and data-subject notification timelines after a confirmed incident. Conflicts with the Breach Disclosure Policy on notice windows.",
  },
]

export type PolicyEvent = { time: string; label: string; detail: string; severity: Severity }
export const policyTimeline: PolicyEvent[] = [
  { time: "2026-06-01", label: "Reviewed", detail: "Annual review completed by owner", severity: "healthy" },
  { time: "2026-03-14", label: "Conflict flagged", detail: "AI engine detected a direct conflict", severity: "critical" },
  { time: "2026-01-10", label: "Published", detail: "Version activated org-wide", severity: "healthy" },
  { time: "2025-11-02", label: "Draft updated", detail: "Section 4 revised for clarity", severity: "warning" },
]

export type Upload = {
  id: string
  name: string
  size: string
  type: "PDF" | "DOCX" | "TXT" | "MD"
  status: "complete" | "processing" | "queued"
  progress: number
  time: string
}

export const recentUploads: Upload[] = [
  { id: "U-1", name: "Access-Control-Standard-2026.pdf", size: "2.4 MB", type: "PDF", status: "complete", progress: 100, time: "2m ago" },
  { id: "U-2", name: "Data-Retention-Policy.docx", size: "812 KB", type: "DOCX", status: "processing", progress: 64, time: "5m ago" },
  { id: "U-3", name: "incident-response.md", size: "44 KB", type: "MD", status: "complete", progress: 100, time: "1h ago" },
  { id: "U-4", name: "vendor-risk-notes.txt", size: "18 KB", type: "TXT", status: "queued", progress: 0, time: "1h ago" },
]

export const pipelineStages = [
  { key: "parsing", label: "Parsing document", icon: "FileSearch" },
  { key: "extracting", label: "Extracting obligations", icon: "ListChecks" },
  { key: "conflict", label: "Conflict detection", icon: "GitCompareArrows" },
  { key: "report", label: "Generating report", icon: "FileBarChart" },
]

export type Activity = {
  id: string
  actor: string
  action: string
  target: string
  time: string
  severity: Severity
}

export const activity: Activity[] = [
  { id: "A-1", actor: "Scan Engine", action: "detected a direct conflict in", target: "Password Rotation Policy", time: "09:33 AM", severity: "critical" },
  { id: "A-2", actor: "Priya Raman", action: "resolved a duplicate obligation in", target: "Vendor Onboarding", time: "09:20 AM", severity: "healthy" },
  { id: "A-3", actor: "Scan Engine", action: "flagged a stale policy", target: "Acceptable Use Policy", time: "08:47 AM", severity: "warning" },
  { id: "A-4", actor: "Marcus Lee", action: "uploaded", target: "Incident Notification v2.2", time: "08:15 AM", severity: "healthy" },
  { id: "A-5", actor: "Scan Engine", action: "completed a full audit of", target: "248 policies", time: "07:02 AM", severity: "healthy" },
]

export const uploadTimeline = [
  { time: "09:31", label: "Upload received", severity: "healthy" as Severity },
  { time: "09:32", label: "Parsing & extraction", severity: "healthy" as Severity },
  { time: "09:33", label: "Conflict found", severity: "critical" as Severity },
  { time: "09:35", label: "Report generated", severity: "healthy" as Severity },
]

export type Notification = {
  id: string
  title: string
  desc: string
  time: string
  severity: Severity
  icon: string
  unread: boolean
}
export const notifications: Notification[] = [
  { id: "N-1", title: "Conflict detected", desc: "Password Rotation vs Zero-Trust Access", time: "2m ago", severity: "critical", icon: "GitCompareArrows", unread: true },
  { id: "N-2", title: "Policy uploaded", desc: "Access-Control-Standard-2026.pdf processed", time: "5m ago", severity: "healthy", icon: "UploadCloud", unread: true },
  { id: "N-3", title: "Review due", desc: "Remote Work Security exceeds review window", time: "1h ago", severity: "warning", icon: "CalendarClock", unread: true },
  { id: "N-4", title: "Report generated", desc: "Executive Summary is ready to download", time: "3h ago", severity: "healthy", icon: "FileBarChart", unread: false },
]

export const obligations = [
  "Enforce MFA for all privileged accounts across production systems.",
  "Encrypt all customer PII at rest using FIPS 140-3 validated modules.",
  "Review vendor security posture annually before contract renewal.",
  "Notify affected data subjects within 72 hours of a confirmed breach.",
  "Log and retain access events for a minimum of 12 months.",
]

export const reports = [
  {
    id: "R-1",
    title: "Executive Report",
    desc: "High-level policy health overview and risk posture for leadership.",
    accent: "primary",
    updated: "Today",
    pages: 6,
  },
  {
    id: "R-2",
    title: "Technical Report",
    desc: "Detailed conflict analysis with section-level remediation guidance.",
    accent: "critical",
    updated: "Today",
    pages: 42,
  },
  {
    id: "R-3",
    title: "Audit Report",
    desc: "Chronological evidence trail suitable for external auditors.",
    accent: "warning",
    updated: "Yesterday",
    pages: 24,
  },
  {
    id: "R-4",
    title: "Compliance Report",
    desc: "Obligations mapped to ISO 27001, SOC 2, GDPR and NIST CSF.",
    accent: "success",
    updated: "Yesterday",
    pages: 18,
  },
]

// Relationship graph — policy nodes and conflict/recommendation links
export type GraphNode = { id: string; label: string; x: number; y: number; severity: Severity }
export type GraphLink = { from: string; to: string; kind: "conflict" | "recommendation" }

export const graphNodes: GraphNode[] = [
  { id: "P-001", label: "Zero-Trust", x: 50, y: 18, severity: "healthy" },
  { id: "P-002", label: "Password", x: 20, y: 50, severity: "critical" },
  { id: "P-003", label: "GDPR", x: 80, y: 42, severity: "warning" },
  { id: "P-005", label: "Encryption", x: 68, y: 78, severity: "healthy" },
  { id: "P-006", label: "Incident", x: 32, y: 82, severity: "critical" },
]

export const graphLinks: GraphLink[] = [
  { from: "P-002", to: "P-001", kind: "conflict" },
  { from: "P-006", to: "P-003", kind: "conflict" },
  { from: "P-005", to: "P-001", kind: "recommendation" },
  { from: "P-003", to: "P-001", kind: "recommendation" },
]

export const searchIndex = [
  ...policies.map((p) => ({ type: "Policy", label: p.name, href: `/policies/${p.id}`, meta: p.category })),
  ...findings.map((f) => ({ type: "Finding", label: `${f.type} · ${f.id}`, href: "/findings", meta: f.policyA })),
  ...Array.from(new Set(policies.map((p) => p.owner))).map((o) => ({ type: "Owner", label: o, href: "/policies", meta: "Policy owner" })),
  ...Array.from(new Set(policies.map((p) => p.department))).map((d) => ({ type: "Department", label: d, href: "/policies", meta: "Department" })),
  { type: "Recommendation", label: "Align rotation cadence with NIST 800-63B", href: "/findings", meta: "F-1042" },
]
