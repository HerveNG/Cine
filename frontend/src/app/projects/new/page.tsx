"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import AppShell from "@/components/AppShell";
import { api, ApiError } from "@/lib/api";
import type { ProjectType } from "@/lib/types";
import { PROJECT_TYPE_LABELS } from "@/lib/types";

const PROJECT_TYPES = Object.keys(PROJECT_TYPE_LABELS) as ProjectType[];

export default function NewProjectPage() {
  const router = useRouter();
  const [form, setForm] = useState({
    title: "",
    project_type: "DOCUMENTARY" as ProjectType,
    genre: "",
    country: "",
    logline: "",
    short_synopsis: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  function update<K extends keyof typeof form>(key: K, value: (typeof form)[K]) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const project = await api.createProject(form);
      router.push(`/projects/${project.id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Une erreur est survenue.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <AppShell>
      <h1 className="font-display text-2xl">Nouveau projet</h1>
      <p className="mt-1 text-sm text-muted">
        Renseignez les informations générales. Vous pourrez tout compléter ensuite.
      </p>

      <form onSubmit={handleSubmit} className="mt-8 max-w-2xl space-y-4">
        <div>
          <label className="mb-1 block text-sm text-muted">Titre</label>
          <input
            required
            value={form.title}
            onChange={(e) => update("title", e.target.value)}
            className="w-full rounded-md border border-border-subtle bg-surface px-3 py-2 outline-none focus:border-gold"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="mb-1 block text-sm text-muted">Type de projet</label>
            <select
              value={form.project_type}
              onChange={(e) => update("project_type", e.target.value as ProjectType)}
              className="w-full rounded-md border border-border-subtle bg-surface px-3 py-2 outline-none focus:border-gold"
            >
              {PROJECT_TYPES.map((t) => (
                <option key={t} value={t}>
                  {PROJECT_TYPE_LABELS[t]}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-1 block text-sm text-muted">Genre</label>
            <input
              value={form.genre}
              onChange={(e) => update("genre", e.target.value)}
              placeholder="Social, portrait, enquête…"
              className="w-full rounded-md border border-border-subtle bg-surface px-3 py-2 outline-none focus:border-gold"
            />
          </div>
        </div>

        <div>
          <label className="mb-1 block text-sm text-muted">Pays</label>
          <input
            value={form.country}
            onChange={(e) => update("country", e.target.value)}
            placeholder="Cameroun"
            className="w-full rounded-md border border-border-subtle bg-surface px-3 py-2 outline-none focus:border-gold"
          />
        </div>

        <div>
          <label className="mb-1 block text-sm text-muted">Logline</label>
          <textarea
            value={form.logline}
            onChange={(e) => update("logline", e.target.value)}
            rows={2}
            className="w-full rounded-md border border-border-subtle bg-surface px-3 py-2 outline-none focus:border-gold"
          />
        </div>

        <div>
          <label className="mb-1 block text-sm text-muted">Synopsis court</label>
          <textarea
            value={form.short_synopsis}
            onChange={(e) => update("short_synopsis", e.target.value)}
            rows={4}
            className="w-full rounded-md border border-border-subtle bg-surface px-3 py-2 outline-none focus:border-gold"
          />
        </div>

        {error && <p className="text-sm text-danger">{error}</p>}

        <button
          type="submit"
          disabled={submitting}
          className="rounded-md bg-gold px-5 py-2.5 font-medium text-[#14140f] hover:opacity-90 disabled:opacity-50"
        >
          {submitting ? "Création…" : "Créer mon projet"}
        </button>
      </form>
    </AppShell>
  );
}
