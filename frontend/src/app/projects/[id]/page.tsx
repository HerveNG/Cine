"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import AIWriterPanel from "@/components/AIWriterPanel";
import AppShell from "@/components/AppShell";
import BudgetPanel from "@/components/BudgetPanel";
import FundingMatchesPanel from "@/components/FundingMatchesPanel";
import ProductionCalendarPanel from "@/components/ProductionCalendarPanel";
import { api, ApiError } from "@/lib/api";
import type { Project, ProjectStatus } from "@/lib/types";
import { PROJECT_STATUS_LABELS, PROJECT_TYPE_LABELS } from "@/lib/types";

const STATUSES = Object.keys(PROJECT_STATUS_LABELS) as ProjectStatus[];

export default function ProjectDetailPage() {
  const params = useParams<{ id: string }>();
  const projectId = Number(params.id);
  const router = useRouter();

  const [project, setProject] = useState<Project | null>(null);
  const [notFound, setNotFound] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (Number.isNaN(projectId)) return;
    api
      .getProject(projectId)
      .then(setProject)
      .catch((err) => {
        if (err instanceof ApiError && err.status === 404) setNotFound(true);
        else setError("Impossible de charger ce projet.");
      });
  }, [projectId]);

  async function handleSave() {
    if (!project) return;
    setSaving(true);
    setError(null);
    try {
      const updated = await api.updateProject(project.id, {
        title: project.title,
        logline: project.logline ?? undefined,
        short_synopsis: project.short_synopsis ?? undefined,
        long_synopsis: project.long_synopsis ?? undefined,
        budget_currency: project.budget_currency ?? undefined,
        status: project.status,
      });
      setProject(updated);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Impossible d'enregistrer.");
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete() {
    if (!project) return;
    if (!window.confirm(`Supprimer définitivement « ${project.title} » ?`)) return;
    await api.deleteProject(project.id);
    router.push("/projects");
  }

  if (notFound) {
    return (
      <AppShell>
        <p className="text-sm text-muted">Ce projet est introuvable.</p>
      </AppShell>
    );
  }

  if (!project) {
    return (
      <AppShell>
        <p className="text-sm text-muted">Chargement…</p>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="font-display text-2xl">{project.title}</h1>
          <p className="mt-1 text-sm text-muted">
            {PROJECT_TYPE_LABELS[project.project_type]}
            {project.country ? ` · ${project.country}` : ""}
          </p>
        </div>
        <button
          onClick={handleDelete}
          className="rounded-md border border-danger/40 px-3 py-1.5 text-sm text-danger hover:bg-danger/10"
        >
          Supprimer
        </button>
      </div>

      <div className="mt-8 max-w-2xl space-y-4">
        <div>
          <label className="mb-1 block text-sm text-muted">Titre</label>
          <input
            value={project.title}
            onChange={(e) => setProject({ ...project, title: e.target.value })}
            className="w-full rounded-md border border-border-subtle bg-surface px-3 py-2 outline-none focus:border-gold"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="mb-1 block text-sm text-muted">Statut</label>
            <select
              value={project.status}
              onChange={(e) => setProject({ ...project, status: e.target.value as ProjectStatus })}
              className="w-full rounded-md border border-border-subtle bg-surface px-3 py-2 outline-none focus:border-gold"
            >
              {STATUSES.map((s) => (
                <option key={s} value={s}>
                  {PROJECT_STATUS_LABELS[s]}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-1 block text-sm text-muted">Devise (budget)</label>
            <input
              value={project.budget_currency ?? ""}
              onChange={(e) => setProject({ ...project, budget_currency: e.target.value })}
              placeholder="XOF, EUR, USD…"
              className="w-full rounded-md border border-border-subtle bg-surface px-3 py-2 outline-none focus:border-gold"
            />
          </div>
        </div>

        <div>
          <label className="mb-1 block text-sm text-muted">Logline</label>
          <textarea
            value={project.logline ?? ""}
            onChange={(e) => setProject({ ...project, logline: e.target.value })}
            rows={2}
            className="w-full rounded-md border border-border-subtle bg-surface px-3 py-2 outline-none focus:border-gold"
          />
        </div>

        <div>
          <label className="mb-1 block text-sm text-muted">Synopsis court</label>
          <textarea
            value={project.short_synopsis ?? ""}
            onChange={(e) => setProject({ ...project, short_synopsis: e.target.value })}
            rows={4}
            className="w-full rounded-md border border-border-subtle bg-surface px-3 py-2 outline-none focus:border-gold"
          />
        </div>

        <div>
          <label className="mb-1 block text-sm text-muted">Synopsis long</label>
          <textarea
            value={project.long_synopsis ?? ""}
            onChange={(e) => setProject({ ...project, long_synopsis: e.target.value })}
            rows={6}
            className="w-full rounded-md border border-border-subtle bg-surface px-3 py-2 outline-none focus:border-gold"
          />
        </div>

        {error && <p className="text-sm text-danger">{error}</p>}

        <button
          onClick={handleSave}
          disabled={saving}
          className="rounded-md bg-gold px-5 py-2.5 font-medium text-[#14140f] hover:opacity-90 disabled:opacity-50"
        >
          {saving ? "Enregistrement…" : "Enregistrer"}
        </button>
      </div>

      <div className="mt-10">
        <h2 className="font-display text-xl">Assistant IA</h2>
        <p className="mt-1 text-sm text-muted">
          Génère, régénère, améliore ou raccourcis les documents de développement de ce
          projet.
        </p>
        <div className="mt-4">
          <AIWriterPanel projectId={project.id} />
        </div>
      </div>

      <div className="mt-10">
        <h2 className="font-display text-xl">Financements compatibles</h2>
        <p className="mt-1 text-sm text-muted">
          Score calculé sur le type de projet, le pays et l&apos;étape de développement.
        </p>
        <div className="mt-4">
          <FundingMatchesPanel projectId={project.id} />
        </div>
      </div>

      <div className="mt-10">
        <h2 className="font-display text-xl">Budget</h2>
        <p className="mt-1 text-sm text-muted">
          Catégories et lignes de budget, sous-totaux calculés automatiquement.
        </p>
        <div className="mt-4">
          <BudgetPanel projectId={project.id} />
        </div>
      </div>

      <div className="mt-10">
        <h2 className="font-display text-xl">Calendrier de production</h2>
        <p className="mt-1 text-sm text-muted">
          Jalons de production, triés chronologiquement.
        </p>
        <div className="mt-4">
          <ProductionCalendarPanel projectId={project.id} />
        </div>
      </div>
    </AppShell>
  );
}
