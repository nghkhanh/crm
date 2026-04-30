import { ProtectedShell } from "@/components/ui/protected-shell";
import { Sidebar } from "@/components/ui/sidebar";
import { Topbar } from "@/components/ui/topbar";

export default function AuthenticatedLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <ProtectedShell>
      <main className="min-h-screen p-4 md:p-6">
        <div className="mx-auto grid max-w-[1680px] gap-5 lg:grid-cols-[292px_1fr]">
          <div className="lg:sticky lg:top-6 lg:h-[calc(100vh-3rem)]">
            <Sidebar />
          </div>
          <div className="space-y-4">
            <Topbar />
            <div>{children}</div>
          </div>
        </div>
      </main>
    </ProtectedShell>
  );
}
