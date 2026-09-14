"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import AppShell from "@/components/AppShell";
import { useAuth } from "@/lib/auth-context";
import { api } from "@/lib/api";
import type { DashboardStats, FundingMatch, Project } from "@/lib/types";
import { PROJECT_STATUS_LABELS, PROJECT_TYPE_LABELS } from "@/lib/types";

const COMPATIBLE_SCORE_THRESHOLD = 60;

interface TopMatch {
  match: FundingMatch;
  project: Project;
}

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
  const { user } = useAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [topMatches, setTopMatches] = useState<TopMatch[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user) return;
    Promise.all([api.dashboardStats(), api.listProjects()])
      .then(async ([s, allProjects]) => {
        setStats(s);
        setProjects(allProjects);

        const matchesByProject = await Promise.all(
          allProjects.map((project) =>
            api
              .getFundingMatches(project.id)
              .then((matches) => ({ project, matches }))
              .catch(() => ({ project, matches: [] as FundingMatch[] }))
          )
        );
        const flattened = matchesByProject.flatMap(({ project, matches }) =>
          matches
            .filter((m) => m.score >= COMPATIBLE_SCORE_THRESHOLD)
            .map((match) => ({ match, project }))
        );
        flattened.sort((a, b) => b.match.score - a.match.score);
        setTopMatches(flattened.slice(0, 4));
      })
      .catch(() => setError("Impossible de charger le tableau de bord."));
  }, [user]);

  const visibleProjects = projects.slice(0, 4);

  return (
    <AppShell>
      <h1 className="font-display text-2xl">
        Bienvenue{user?.prenom ? `, ${user.prenom}` : ""}
      </h1>

      {error && <p className="mt-4 text-sm text-danger">{error}</p>}

      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Mes projets" value={stats?.projects_count ?? 0} />
        <StatCard label="Documents générés" value={stats?.documents_generated ?? 0} />
        <StatCard
          label="Opportunités compatibles"
          value={stats?.compatible_opportunities ?? 0}
        />
        <StatCard
          label="Échéances prochaines"
          value={stats?.upcoming_deadlines ?? 0}
          note="Suivi des dates limites à venir"
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

      {visibleProjects.length === 0 ? (
        <p className="mt-4 text-sm text-muted">
          Aucun projet pour l&apos;instant.{" "}
          <Link href="/projects/new" className="text-gold-soft hover:underline">
            Créez votre premier projet
          </Link>
          .
        </p>
      ) : (
        <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {visibleProjects.map((project) => (
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
        <div className="flex items-center justify-between">
          <h2 className="font-display text-xl">Opportunités recommandées</h2>
          <Link href="/financements" className="text-sm text-gold-soft hover:underline">
            Voir tous les financements
          </Link>
        </div>

        {!topMatches ? (
          <p className="mt-4 text-sm text-muted">Chargement…</p>
        ) : topMatches.length === 0 ? (
          <p className="mt-4 rounded-xl border border-dashed border-border-subtle p-6 text-sm text-muted">
            Aucune opportunité fortement compatible pour l&apos;instant (score ≥{" "}
            {COMPATIBLE_SCORE_THRESHOLD}/100). Complétez le pays et l&apos;étape de vos projets
            pour affiner le matching, ou consultez tous les financements.
          </p>
        ) : (
          <div className="mt-4 space-y-3">
            {topMatches.map(({ match, project }) => (
              <Link
                key={`${project.id}-${match.opportunity.id}`}
                href={`/projects/${project.id}`}
                className="block rounded-xl border border-border-subtle bg-surface p-5 transition-colors hover:border-gold"
              >
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="font-display text-lg">{match.opportunity.name}</p>
                    <p className="text-sm text-muted">
                      Pour « {project.title} » · {match.opportunity.amount_label}
                    </p>
                  </div>
                  <span className="shrink-0 rounded-full border border-border-subtle px-2.5 py-1 text-xs font-medium text-gold-soft">
                    {match.score}/100
                  </span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </AppShell>
  );
}
