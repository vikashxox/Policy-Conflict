# Policy Guardian Backend API Contract

This document describes the backend API contract required to power the current frontend without changing the UI.

Scope:
- The frontend currently uses static demo data from [frontend/lib/data.ts](frontend/lib/data.ts), but the API contract below is designed to replace those values with live backend responses while preserving the existing page structure.
- No backend code is included in this document.

## 1. Frontend page inventory

### Public pages
- [frontend/app/login/page.tsx](frontend/app/login/page.tsx)
  - Login form with email and password.
  - Expected auth flow: submit credentials, receive JWT, and navigate to the app shell.

### Authenticated app pages
- [frontend/app/(app)/page.tsx](frontend/app/(app)/page.tsx)
  - Dashboard page.
  - Displays KPI cards, AI insights, gauges, charts, recent findings, uploads, and activity.
- [frontend/app/(app)/policies/page.tsx](frontend/app/(app)/policies/page.tsx)
  - Policy list page.
  - Displays policy table with health bars and status badges.
- [frontend/app/(app)/policies/[id]/page.tsx](frontend/app/(app)/policies/[id]/page.tsx)
  - Policy detail page.
  - Displays metadata, health score, obligations, findings, and recommendations.
- [frontend/app/(app)/findings/page.tsx](frontend/app/(app)/findings/page.tsx)
  - Findings page with search/filter controls.
- [frontend/app/(app)/reports/page.tsx](frontend/app/(app)/reports/page.tsx)
  - Report cards for PDF, JSON, and Excel exports.
- [frontend/app/(app)/upload/page.tsx](frontend/app/(app)/upload/page.tsx)
  - Upload and processing UI for policy files.
- [frontend/app/(app)/settings/page.tsx](frontend/app/(app)/settings/page.tsx)
  - Settings form UI.
  - Currently static; no API is required by the present frontend.

## 2. Frontend component inventory

### App shell and navigation
- [frontend/components/app-shell.tsx](frontend/components/app-shell.tsx)
  - Global navigation
  - Global search
  - Notification center
  - User profile chip

### Dashboard components
- [frontend/components/welcome-hero.tsx](frontend/components/welcome-hero.tsx)
- [frontend/components/kpi-grid.tsx](frontend/components/kpi-grid.tsx)
- [frontend/components/ai-insights.tsx](frontend/components/ai-insights.tsx)
- [frontend/components/charts.tsx](frontend/components/charts.tsx)
- [frontend/components/compliance-widget.tsx](frontend/components/compliance-widget.tsx)

### Shared UI components
- [frontend/components/glass.tsx](frontend/components/glass.tsx)
- [frontend/components/page-header.tsx](frontend/components/page-header.tsx)
- [frontend/components/primitives.tsx](frontend/components/primitives.tsx)

## 3. Frontend data expectations by page

### Login page
- Expects auth endpoint to accept email/password and return a JWT + user object.

### Dashboard page
- Expects a dashboard payload containing:
  - KPI summary
  - health breakdown
  - trend series
  - compliance distribution
  - recent findings
  - recent uploads
  - activity timeline
  - relationship graph nodes/links
  - AI insights
  - compliance frameworks
  - organization metadata

### Policies page
- Expects a list of policy objects.

### Policy detail page
- Expects a policy object plus obligations and related findings.

### Findings page
- Expects a list of finding objects.
- The UI supports filtering by severity, category, status, and search query.

### Reports page
- Expects a list of report objects with format metadata and download information.

### Upload page
- Expects upload submission and processing results.
- The UI shows file name, type, size, status, and progress.

## 4. Common enums and shared types

```ts
export type Severity = "critical" | "warning" | "healthy"
export type FindingStatus = "open" | "in-review" | "resolved"
export type PolicyStatus = "active" | "draft" | "archived"
export type UploadStatus = "complete" | "processing" | "queued"
```

## 5. API contract

Base URL: `/api`

Authentication: JWT bearer token in `Authorization: Bearer <token>` for protected routes.

### 5.1 Authentication

#### POST /api/auth/login
Request:
```json
{
  "email": "user@company.com",
  "password": "secret123"
}
```

Response:
```json
{
  "access_token": "jwt-token",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@company.com",
    "name": "Alex Morgan",
    "role": "admin"
  }
}
```

#### GET /api/auth/me
Response:
```json
{
  "user": {
    "id": 1,
    "email": "user@company.com",
    "name": "Alex Morgan",
    "role": "admin"
  }
}
```

---

### 5.2 Dashboard

#### GET /api/dashboard
Response:
```json
{
  "organization": {
    "name": "Northwind Security Corp",
    "admin": "Alex Morgan",
    "lastAnalysis": "Today, 09:35 AM",
    "lastUpload": "Access-Control-Standard-2026.pdf"
  },
  "kpis": {
    "totalPolicies": 248,
    "activePolicies": 213,
    "conflicts": 17,
    "duplicates": 9,
    "stale": 24,
    "healthScore": 82,
    "complianceScore": 88
  },
  "kpiMetrics": [
    {
      "label": "Total Policies",
      "value": 248,
      "icon": "FileText",
      "tint": "text-primary bg-primary/15",
      "trend": "up",
      "change": "+12",
      "good": "up",
      "spark": [210, 218, 222, 229, 233, 240, 244, 248]
    }
  ],
  "healthBreakdown": [
    { "label": "Healthy", "value": 187, "color": "var(--color-success)" },
    { "label": "Conflict", "value": 37, "color": "var(--color-critical)" },
    { "label": "Stale", "value": 24, "color": "var(--color-warning)" }
  ],
  "policiesByCategory": [
    { "category": "Access Control", "count": 52 }
  ],
  "healthTrend": [
    { "label": "Jan", "value": 68 }
  ],
  "conflictTrend": [
    { "label": "Jan", "value": 31 }
  ],
  "complianceDistribution": [
    { "label": "Compliant", "value": 172, "color": "var(--color-success)" },
    { "label": "Partial", "value": 54, "color": "var(--color-warning)" },
    { "label": "Non-Compliant", "value": 22, "color": "var(--color-critical)" }
  ],
  "complianceFrameworks": [
    { "name": "ISO 27001", "score": 92, "controls": "114 controls" }
  ],
  "aiInsights": [
    {
      "id": "AI-1",
      "severity": "critical",
      "text": "3 critical policy conflicts detected across Access Control",
      "icon": "GitCompareArrows"
    }
  ],
  "aiRecommendation": "Update the Password Rotation Policy to align with NIST 800-63B before the next audit window.",
  "findings": [
    {
      "id": "F-1042",
      "severity": "critical",
      "type": "Direct Conflict",
      "policyA": "Password Rotation Policy v4.2",
      "policyB": "Zero-Trust Access Standard v2.0",
      "section": "§4.1 Credential Lifecycle",
      "confidence": 96,
      "description": "Password rotation mandates 30-day cycles while the zero-trust standard prohibits periodic rotation without cause.",
      "recommendation": "Align rotation cadence with NIST 800-63B; remove forced periodic rotation.",
      "compliance": "NIST 800-63B, ISO 27001 A.9",
      "status": "open",
      "category": "Access Control"
    }
  ],
  "recentUploads": [
    {
      "id": "U-1",
      "name": "Access-Control-Standard-2026.pdf",
      "size": "2.4 MB",
      "type": "PDF",
      "status": "complete",
      "progress": 100,
      "time": "2m ago"
    }
  ],
  "activity": [
    {
      "id": "A-1",
      "actor": "Scan Engine",
      "action": "detected a direct conflict in",
      "target": "Password Rotation Policy",
      "time": "09:33 AM",
      "severity": "critical"
    }
  ],
  "graphNodes": [
    { "id": "P-001", "label": "Zero-Trust", "x": 50, "y": 18, "severity": "healthy" }
  ],
  "graphLinks": [
    { "from": "P-002", "to": "P-001", "kind": "conflict" }
  ]
}
```

---

### 5.3 Policies

#### GET /api/policies
Response:
```json
{
  "items": [
    {
      "id": "P-001",
      "name": "Zero-Trust Access Standard",
      "category": "Access Control",
      "owner": "Dana Whitmore",
      "department": "Security Engineering",
      "version": "v2.0",
      "effectiveDate": "2026-01-10",
      "lastReviewed": "2026-05-14",
      "health": 94,
      "severity": "healthy",
      "status": "active",
      "summary": "Establishes continuous verification for all access requests."
    }
  ]
}
```

#### GET /api/policies/{id}
Response:
```json
{
  "policy": {
    "id": "P-001",
    "name": "Zero-Trust Access Standard",
    "category": "Access Control",
    "owner": "Dana Whitmore",
    "department": "Security Engineering",
    "version": "v2.0",
    "effectiveDate": "2026-01-10",
    "lastReviewed": "2026-05-14",
    "health": 94,
    "severity": "healthy",
    "status": "active",
    "summary": "Establishes continuous verification for all access requests."
  },
  "obligations": [
    "Enforce MFA for all privileged accounts across production systems.",
    "Encrypt all customer PII at rest using FIPS 140-3 validated modules."
  ],
  "relatedFindings": [
    {
      "id": "F-1042",
      "severity": "critical",
      "type": "Direct Conflict",
      "description": "Password rotation mandates 30-day cycles while the zero-trust standard prohibits periodic rotation without cause.",
      "recommendation": "Align rotation cadence with NIST 800-63B; remove forced periodic rotation.",
      "compliance": "NIST 800-63B, ISO 27001 A.9"
    }
  ]
}
```

#### DELETE /api/policies/{id}
Response:
```json
{
  "success": true,
  "deletedPolicyId": "P-001"
}
```

---

### 5.4 Findings

#### GET /api/findings
Response:
```json
{
  "items": [
    {
      "id": "F-1042",
      "severity": "critical",
      "type": "Direct Conflict",
      "policyA": "Password Rotation Policy v4.2",
      "policyB": "Zero-Trust Access Standard v2.0",
      "section": "§4.1 Credential Lifecycle",
      "confidence": 96,
      "description": "Password rotation mandates 30-day cycles while the zero-trust standard prohibits periodic rotation without cause.",
      "recommendation": "Align rotation cadence with NIST 800-63B; remove forced periodic rotation.",
      "compliance": "NIST 800-63B, ISO 27001 A.9",
      "status": "open",
      "category": "Access Control"
    }
  ]
}
```

Optional query parameters:
- `severity`
- `status`
- `category`
- `q`

---

### 5.5 Reports

#### GET /api/reports
Response:
```json
{
  "items": [
    {
      "id": "R-1",
      "title": "Executive Report",
      "desc": "High-level policy health overview and risk posture for leadership.",
      "format": "PDF",
      "updated": "Today",
      "pages": 6,
      "downloadUrl": "/reports/executive-report.pdf"
    }
  ]
}
```

---

### 5.6 Upload

#### POST /api/upload
Request:
- Multipart form-data with one or more files under field `files`.

Response:
```json
{
  "uploads": [
    {
      "id": "U-1",
      "name": "Access-Control-Standard-2026.pdf",
      "size": "2.4 MB",
      "type": "PDF",
      "status": "complete",
      "progress": 100,
      "time": "just now",
      "parsed": {
        "policyName": "Access Control Standard",
        "version": "v2026.1",
        "department": "Security Engineering",
        "owner": "Dana Whitmore",
        "effectiveDate": "2026-01-10",
        "lastReviewed": "2026-05-14",
        "sections": 8,
        "rawText": "..."
      }
    }
  ],
  "summary": {
    "accepted": 1,
    "failed": 0,
    "processing": 0
  }
}
```

---

### 5.7 Analysis

#### POST /api/analyze
Request:
```json
{
  "policyIds": ["P-001", "P-002"]
}
```

Response:
```json
{
  "status": "completed",
  "summary": "Policies analyzed successfully",
  "healthScore": 82,
  "criticalFindings": 3,
  "recommendations": [
    "Align password rotation policy",
    "Retire deprecated VPN references"
  ],
  "riskLevel": "high",
  "analysis": {
    "conflicts": [
      {
        "severity": "critical",
        "description": "Password rotation mandates 30-day cycles while the zero-trust standard prohibits periodic rotation without cause.",
        "recommendation": "Align the two policies to a single mandatory requirement."
      }
    ],
    "duplicates": [
      {
        "isDuplicate": true,
        "similarityScore": 0.96,
        "type": "exact"
      }
    ],
    "staleness": [
      {
        "isStale": true,
        "reason": "Policy older than 18 months"
      }
    ]
  }
}
```

---

### 5.8 Settings (optional, not currently used by the UI)

These are not required by the current frontend, but they are the natural extension if the settings page becomes dynamic.

#### PUT /api/settings/profile
Request:
```json
{
  "organizationName": "Northwind Security Corp",
  "primaryContact": "Alex Morgan",
  "contactEmail": "governance@northwind.com",
  "industry": "Financial Services"
}
```

#### PUT /api/settings/preferences
Request:
```json
{
  "notifications": {
    "critical": true,
    "stale": true,
    "weekly": false
  },
  "reviewSchedule": "quarterly",
  "theme": "dark"
}
```

---

## 6. Error envelope

All error responses should follow this shape:

```json
{
  "success": false,
  "error": {
    "code": "INVALID_REQUEST",
    "message": "A human-readable error message"
  }
}
```

Common status codes:
- 200 OK
- 201 Created
- 400 Bad Request
- 401 Unauthorized
- 403 Forbidden
- 404 Not Found
- 409 Conflict
- 422 Validation Error
- 500 Internal Server Error

## 7. Implementation notes for the frontend compatibility

To keep the current UI intact, the backend should preserve the following field names exactly:
- `effectiveDate` and `lastReviewed` on policies
- `policyA`, `policyB`, `section`, `confidence`, `compliance`, `status`, `category` on findings
- `type`, `status`, `progress`, `time` on upload objects
- `format`, `updated`, `pages`, `downloadUrl` on report objects
- `severity`, `action`, `target`, `time` on activity items
