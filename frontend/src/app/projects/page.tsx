"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import AppShell from "@/components/AppShell";
import { useAuth } from "@/lib/auth-context";
import { api } from "@/lib/api";
import type { Project } from "@/lib/types";
import { PROJECT_STATUS_LABELS, PROJECT_TYPE_LABELS } from "@/lib/types";

export default function ProjectsPage() {
  const { user } = useAuth();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user) return;
    api
      .listProjects()
      .then(setProjects)
      .catch(() => setError("Impossible de charger vos projets."))
      .finally(() => setLoading(false));
  }, [user]);

  return (
    <AppShell>
      <div className="flex items-center justify-between">
        <h1 className="font-display text-2xl">Mes projets</h1>
        <Link
          href="/projects/new"
          className="rounded-md bg-gold px-4 py-2 text-sm font-medium text-[#14140f] hover:opacity-90"
        >
          Nouveau projet
        </Link>
      </div>

      {error && <p className="mt-4 text-sm text-danger">{error}</p>}
      {loading && <p className="mt-4 text-sm text-muted">Chargement…</p>}

      {!loading && projects.length === 0 && (
        <p className="mt-6 text-sm text-muted">
          Vous n&apos;avez pas encore de projet.{" "}
          <Link href="/projects/new" className="text-gold-soft hover:underline">
            Créez votre premier projet
          </Link>
          .
        </p>
      )}

      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {projects.map((project) => (
          <Link
            key={project.id}
            href={`/projects/${project.id}`}
            className="rounded-xl border border-border-subtle bg-surface p-5 transition-colors hover:border-gold"
          >
            <p className="font-display text-lg">{project.title}</p>
            <p className="mt-1 text-sm text-muted">{PROJECT_TYPE_LABELS[project.project_type]}</p>
            {project.logline && (
              <p className="mt-3 line-clamp-2 text-sm text-foreground/80">{project.logline}</p>
            )}
            <div className="mt-4 flex items-center justify-between text-xs text-muted">
              <span className="rounded-full border border-border-subtle px-2 py-0.5 text-gold-soft">
                {PROJECT_STATUS_LABELS[project.status]}
              </span>
              <span>{new Date(project.updated_at).toLocaleDateString("fr-FR")}</span>
            </div>
          </Link>
        ))}
      </div>
    </AppShell>
  );
}
