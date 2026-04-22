import { KanbanBoard } from "@/components/KanbanBoard";
import { AuthGuard } from "@/components/AuthGuard";
import { LogoutButton } from "@/components/LogoutButton";

export default function Home() {
  return (
    <AuthGuard>
      <div className="min-h-screen flex flex-col">
        <header className="flex justify-end p-4 bg-white shadow">
          <LogoutButton />
        </header>
        <main className="flex-1">
          <KanbanBoard />
        </main>
      </div>
    </AuthGuard>
  );
}
