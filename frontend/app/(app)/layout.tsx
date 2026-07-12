import { AppShell } from "@/components/app-shell"
import { AuthGuard } from "@/components/auth-guard"
import { ToastProvider } from "@/components/primitives"

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <ToastProvider>
      <AuthGuard>
        <AppShell>{children}</AppShell>
      </AuthGuard>
    </ToastProvider>
  )
}
