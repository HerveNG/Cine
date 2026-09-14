"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, type ReactNode } from "react";
import { useAuth } from "@/lib/auth-context";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard", ready: true },
  { href: "/projects", label: "Mes projets", ready: true },
  { href: "/financements", label: "Financements", ready: true },
  { href: "/documents", label: "Documents", ready: false },
  { href: "/profil", label: "Profil", ready: false },
];

export default function AppShell({ children }: { children: ReactNode }) {
  const { user, isLoading, logout } = useAuth();
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !user) {
      router.replace("/login");
    }
  }, [isLoading, user, router]);

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background text-muted">
        Chargement…
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="flex min-h-screen">
        <aside className="hidden w-64 shrink-0 border-r border-border-subtle bg-surface md:block">
          <div className="flex h-16 items-center gap-2 border-b border-border-subtle px-6">
            <span className="font-display text-lg tracking-wide text-gold-soft">
              FilmFund Africa
            </span>
          </div>
          <nav className="flex flex-col gap-1 p-4">
            {NAV_ITEMS.map((item) => {
              const active = pathname?.startsWith(item.href);
              if (!item.ready) {
                return (
                  <span
                    key={item.href}
                    className="flex items-center justify-between rounded-lg px-3 py-2 text-sm text-muted/50"
                    title="Module à venir"
                  >
                    {item.label}
                    <span className="rounded-full border border-border-subtle px-2 py-0.5 text-[10px] uppercase tracking-wide">
                      Bientôt
                    </span>
                  </span>
                );
              }
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`rounded-lg px-3 py-2 text-sm transition-colors ${
                    active
                      ? "bg-surface-raised text-gold-soft"
                      : "text-foreground/80 hover:bg-surface-raised hover:text-foreground"
                  }`}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </aside>

        <div className="flex flex-1 flex-col">
          <header className="flex h-16 items-center justify-between border-b border-border-subtle bg-surface px-6">
            <span className="font-display text-lg text-gold-soft md:hidden">FilmFund Africa</span>
            <div className="ml-auto flex items-center gap-4">
              <span className="text-sm text-muted">
                {user.prenom ? `Bienvenue, ${user.prenom}` : user.email}
              </span>
              <button
                onClick={logout}
                className="rounded-md border border-border-subtle px-3 py-1.5 text-sm text-foreground/80 transition-colors hover:border-gold hover:text-gold-soft"
              >
                Déconnexion
              </button>
            </div>
          </header>
          <main className="flex-1 px-6 py-8">{children}</main>
        </div>
      </div>
    </div>
  );
}
