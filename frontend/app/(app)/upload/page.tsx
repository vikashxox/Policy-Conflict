"use client"

import { useCallback, useRef, useState } from "react"
import { UploadCloud, FileText, X, CheckCircle2, Loader2 } from "lucide-react"
import { GlassCard } from "@/components/glass"
import { PageHeader } from "@/components/page-header"
import { recentUploads, type Upload } from "@/lib/data"
import { cn } from "@/lib/utils"

function ext(name: string): Upload["type"] {
  const e = name.split(".").pop()?.toLowerCase()
  if (e === "pdf") return "PDF"
  if (e === "docx" || e === "doc") return "DOCX"
  if (e === "md" || e === "markdown") return "MD"
  return "TXT"
}

function fmtSize(bytes: number) {
  if (bytes > 1_000_000) return `${(bytes / 1_000_000).toFixed(1)} MB`
  return `${Math.max(1, Math.round(bytes / 1000))} KB`
}

export default function UploadPage() {
  const [dragging, setDragging] = useState(false)
  const [files, setFiles] = useState<Upload[]>(recentUploads)
  const inputRef = useRef<HTMLInputElement>(null)

  const addFiles = useCallback((list: FileList | null) => {
    if (!list) return
    const next: Upload[] = Array.from(list).map((f, i) => ({
      id: `U-new-${Date.now()}-${i}`,
      name: f.name,
      size: fmtSize(f.size),
      type: ext(f.name),
      status: "processing",
      progress: 40,
      time: "just now",
    }))
    setFiles((prev) => [...next, ...prev])
    // simulate completion
    next.forEach((n) => {
      setTimeout(() => {
        setFiles((prev) =>
          prev.map((p) => (p.id === n.id ? { ...p, status: "complete", progress: 100 } : p)),
        )
      }, 1600)
    })
  }, [])

  const removeFile = (id: string) => setFiles((prev) => prev.filter((p) => p.id !== id))

  return (
    <div>
      <PageHeader
        title="Upload Policies"
        subtitle="Drop policy documents to scan for conflicts, duplicates and staleness."
      />

      <div
        onDragOver={(e) => {
          e.preventDefault()
          setDragging(true)
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault()
          setDragging(false)
          addFiles(e.dataTransfer.files)
        }}
        onClick={() => inputRef.current?.click()}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === "Enter" && inputRef.current?.click()}
        className={cn(
          "glass-hover flex cursor-pointer flex-col items-center justify-center rounded-3xl border-2 border-dashed p-12 text-center transition-colors",
          dragging ? "border-primary bg-primary/10" : "border-border",
        )}
      >
        <div className="mb-4 flex size-16 items-center justify-center rounded-2xl bg-primary/15 text-primary">
          <UploadCloud className="size-7" />
        </div>
        <p className="text-base font-semibold">
          {dragging ? "Release to upload" : "Drag & drop your files here"}
        </p>
        <p className="mt-1 text-sm text-muted-foreground">
          or click to browse — PDF, DOCX, TXT & Markdown supported
        </p>
        <input
          ref={inputRef}
          type="file"
          multiple
          accept=".pdf,.docx,.doc,.txt,.md,.markdown"
          className="hidden"
          onChange={(e) => addFiles(e.target.files)}
        />
        <div className="mt-5 flex gap-2 text-[11px] text-muted-foreground">
          {["PDF", "DOCX", "TXT", "MD"].map((t) => (
            <span key={t} className="rounded-full border border-border bg-white/5 px-2.5 py-1">
              {t}
            </span>
          ))}
        </div>
      </div>

      <h3 className="mb-4 mt-8 text-sm font-medium">Uploaded files ({files.length})</h3>
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {files.map((f) => (
          <GlassCard key={f.id} className="p-4">
            <div className="flex items-start gap-3">
              <span className="flex size-11 shrink-0 items-center justify-center rounded-2xl bg-white/5 text-primary">
                <FileText className="size-5" />
              </span>
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium">{f.name}</p>
                <p className="text-xs text-muted-foreground">
                  {f.type} · {f.size} · {f.time}
                </p>
              </div>
              <button
                onClick={() => removeFile(f.id)}
                className="rounded-full p-1 text-muted-foreground hover:bg-white/10"
                aria-label={`Remove ${f.name}`}
              >
                <X className="size-4" />
              </button>
            </div>

            <div className="mt-4">
              {f.status === "complete" ? (
                <div className="flex items-center gap-1.5 text-xs font-medium text-success">
                  <CheckCircle2 className="size-4" />
                  Scan complete
                </div>
              ) : f.status === "processing" ? (
                <>
                  <div className="mb-1.5 flex items-center gap-1.5 text-xs font-medium text-warning">
                    <Loader2 className="size-3.5 animate-spin" />
                    Processing…
                  </div>
                  <div className="h-1.5 w-full overflow-hidden rounded-full bg-white/10">
                    <div
                      className="h-full rounded-full bg-primary transition-all duration-500"
                      style={{ width: `${f.progress}%` }}
                    />
                  </div>
                </>
              ) : (
                <div className="text-xs text-muted-foreground">Queued</div>
              )}
            </div>
          </GlassCard>
        ))}
      </div>
    </div>
  )
}
