import { AppShell } from "@/components/app-shell"
import { ToastProvider } from "@/components/primitives"

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <ToastProvider>
      <AppShell>{children}</AppShell>
    </ToastProvider>
  )
}
