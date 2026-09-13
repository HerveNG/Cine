"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import AppShell from "@/components/AppShell";
import { useAuth } from "@/lib/auth-context";
import { api } from "@/lib/api";
import type { DashboardStats, Project } from "@/lib/types";
import { PROJECT_STATUS_LABELS, PROJECT_TYPE_LABELS } from "@/lib/types";

function StatCard({ label, value, note }: { label: string; value: number; note?: string }) {
  return (
    <div className="rounded-xl border border-border-subtle bg-surface p-5">
      <p className="text-sm text-muted">{label}</p>
      <p className="mt-2 font-display text-3xl text-gold-soft">{value}</p>
      {note && <p className="mt-1 text-xs text-muted/70">{note}</p>}
    </div>
  );
}

export default function DashboardPage() {
  const { user, token } = useAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;
    Promise.all([api.dashboardStats(token), api.listProjects(token)])
      .then(([s, p]) => {
        setStats(s);
        setProjects(p.slice(0, 4));
      })
      .catch(() => setError("Impossible de charger le tableau de bord."));
  }, [token]);

  return (
    <AppShell>
      <h1 className="font-display text-2xl">
        Bienvenue{user?.prenom ? `, ${user.prenom}` : ""}
      </h1>

      {error && <p className="mt-4 text-sm text-danger">{error}</p>}

      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Mes projets" value={stats?.projects_count ?? 0} />
        <StatCard
          label="Documents générés"
          value={stats?.documents_generated ?? 0}
          note="Module AI Writer à venir"
        />
        <StatCard
          label="Opportunités compatibles"
          value={stats?.compatible_opportunities ?? 0}
          note="Module Financements à venir"
        />
        <StatCard
          label="Échéances prochaines"
          value={stats?.upcoming_deadlines ?? 0}
          note="Module Financements à venir"
        />
      </div>

      <div className="mt-10 flex items-center justify-between">
        <h2 className="font-display text-xl">Mes projets</h2>
        <Link
          href="/projects/new"
          className="rounded-md bg-gold px-4 py-2 text-sm font-medium text-[#14140f] hover:opacity-90"
        >
          Nouveau projet
        </Link>
      </div>

      {projects.length === 0 ? (
        <p className="mt-4 text-sm text-muted">
          Aucun projet pour l&apos;instant.{" "}
          <Link href="/projects/new" className="text-gold-soft hover:underline">
            Créez votre premier projet
          </Link>
          .
        </p>
      ) : (
        <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {projects.map((project) => (
            <Link
              key={project.id}
              href={`/projects/${project.id}`}
              className="rounded-xl border border-border-subtle bg-surface p-5 transition-colors hover:border-gold"
            >
              <p className="font-display text-lg">{project.title}</p>
              <p className="mt-1 text-sm text-muted">{PROJECT_TYPE_LABELS[project.project_type]}</p>
              <p className="mt-3 inline-block rounded-full border border-border-subtle px-2 py-0.5 text-xs text-gold-soft">
                {PROJECT_STATUS_LABELS[project.status]}
              </p>
            </Link>
          ))}
        </div>
      )}

      <div className="mt-10">
        <h2 className="font-display text-xl">Opportunités recommandées</h2>
        <p className="mt-4 rounded-xl border border-dashed border-border-subtle p-6 text-sm text-muted">
          Le module Funding Intelligence &amp; Matching n&apos;est pas encore implémenté dans ce
          MVP (Phase 3 de la feuille de route). Aucune opportunité fictive n&apos;est affichée ici.
        </p>
      </div>
    </AppShell>
  );
}
