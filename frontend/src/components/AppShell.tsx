import MainNavigation from "./MainNavigation";

interface AppShellProps {
  children: React.ReactNode;
}

export default function AppShell({ children }: AppShellProps) {
  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      <MainNavigation />
      <main className="mx-auto max-w-6xl px-4 py-8">{children}</main>
    </div>
  );
}
