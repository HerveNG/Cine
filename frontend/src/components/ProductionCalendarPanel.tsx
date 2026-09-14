"use client";

import { useEffect, useState } from "react";
import { api, ApiError } from "@/lib/api";
import type { ProductionMilestone } from "@/lib/types";

function formatDate(value: string) {
  return new Date(value).toLocaleDateString("fr-FR", { year: "numeric", month: "long", day: "numeric" });
}

export default function ProductionCalendarPanel({ projectId }: { projectId: number }) {
  const [milestones, setMilestones] = useState<ProductionMilestone[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [title, setTitle] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [saving, setSaving] = useState(false);

  function reload() {
    api
      .listMilestones(projectId)
      .then(setMilestones)
      .catch(() => setError("Impossible de charger le calendrier."));
  }

  useEffect(reload, [projectId]);

  async function addMilestone() {
    if (!title.trim() || !startDate) return;
    setSaving(true);
    setError(null);
    try {
      await api.createMilestone(projectId, {
        title,
        start_date: startDate,
        end_date: endDate || undefined,
      });
      setTitle("");
      setStartDate("");
      setEndDate("");
      reload();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Impossible d'ajouter le jalon.");
    } finally {
      setSaving(false);
    }
  }

  async function deleteMilestone(id: number) {
    await api.deleteMilestone(projectId, id);
    reload();
  }

  if (error) return <p className="text-sm text-danger">{error}</p>;
  if (!milestones) return <p className="text-sm text-muted">Chargement…</p>;

  return (
    <div className="space-y-3">
      {milestones.length === 0 ? (
        <p className="text-sm text-muted">Aucun jalon pour l&apos;instant.</p>
      ) : (
        <ol className="space-y-3">
          {milestones.map((m) => (
            <li
              key={m.id}
              className="flex items-start justify-between gap-4 rounded-xl border border-border-subtle bg-surface p-4"
            >
              <div>
                <p className="font-medium">{m.title}</p>
                <p className="text-sm text-muted">
                  {formatDate(m.start_date)}
                  {m.end_date ? ` → ${formatDate(m.end_date)}` : ""}
                </p>
                {m.notes && <p className="mt-1 text-sm text-foreground/70">{m.notes}</p>}
              </div>
              <button
                onClick={() => deleteMilestone(m.id)}
                className="shrink-0 text-xs text-muted hover:text-danger"
              >
                Retirer
              </button>
            </li>
          ))}
        </ol>
      )}

      <div className="flex flex-wrap items-end gap-2 rounded-xl border border-border-subtle bg-surface p-4">
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Jalon (ex. Tournage)"
          className="min-w-[160px] flex-1 rounded-md border border-border-subtle bg-background px-3 py-2 text-sm outline-none focus:border-gold"
        />
        <input
          type="date"
          value={startDate}
          onChange={(e) => setStartDate(e.target.value)}
          className="rounded-md border border-border-subtle bg-background px-3 py-2 text-sm outline-none focus:border-gold"
        />
        <input
          type="date"
          value={endDate}
          onChange={(e) => setEndDate(e.target.value)}
          className="rounded-md border border-border-subtle bg-background px-3 py-2 text-sm outline-none focus:border-gold"
        />
        <button
          onClick={addMilestone}
          disabled={saving}
          className="rounded-md border border-border-subtle px-3 py-2 text-sm hover:border-gold hover:text-gold-soft disabled:opacity-50"
        >
          Ajouter
        </button>
      </div>
    </div>
  );
}
