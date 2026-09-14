"use client";

import { useEffect, useState } from "react";
import AppShell from "@/components/AppShell";
import { useAuth } from "@/lib/auth-context";
import { api } from "@/lib/api";
import type { FundingOpportunity, ProjectType } from "@/lib/types";
import { PROJECT_TYPE_LABELS } from "@/lib/types";

const PROJECT_TYPES = Object.keys(PROJECT_TYPE_LABELS) as ProjectType[];

export default function FinancementsPage() {
  const { token } = useAuth();
  const [opportunities, setOpportunities] = useState<FundingOpportunity[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [projectType, setProjectType] = useState("");
  const [country, setCountry] = useState("");
  const [search, setSearch] = useState("");

  useEffect(() => {
    if (!token) return;
    api
      .listFundingOpportunities(token, {
        project_type: projectType || undefined,
        country: country || undefined,
        search: search || undefined,
      })
      .then(setOpportunities)
      .catch(() => setError("Impossible de charger les financements."));
  }, [token, projectType, country, search]);

  return (
    <AppShell>
      <h1 className="font-display text-2xl">Financements</h1>
      <p className="mt-1 text-sm text-muted">
        Fonds et bourses réels pour le cinéma africain — vérifiez toujours les critères et
        dates limites sur le site officiel de chaque financement.
      </p>

      <div className="mt-6 flex flex-wrap gap-3">
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Rechercher un financement…"
          className="min-w-[220px] flex-1 rounded-md border border-border-subtle bg-surface px-3 py-2 text-sm outline-none focus:border-gold"
        />
        <select
          value={projectType}
          onChange={(e) => setProjectType(e.target.value)}
          className="rounded-md border border-border-subtle bg-surface px-3 py-2 text-sm outline-none focus:border-gold"
        >
          <option value="">Tous les types de projet</option>
          {PROJECT_TYPES.map((t) => (
            <option key={t} value={t}>
              {PROJECT_TYPE_LABELS[t]}
            </option>
          ))}
        </select>
        <input
          value={country}
          onChange={(e) => setCountry(e.target.value)}
          placeholder="Pays (ex. Maroc)"
          className="rounded-md border border-border-subtle bg-surface px-3 py-2 text-sm outline-none focus:border-gold"
        />
      </div>

      {error && <p className="mt-4 text-sm text-danger">{error}</p>}

      {!opportunities ? (
        <p className="mt-6 text-sm text-muted">Chargement…</p>
      ) : opportunities.length === 0 ? (
        <p className="mt-6 text-sm text-muted">Aucun financement ne correspond à ces critères.</p>
      ) : (
        <div className="mt-6 space-y-3">
          {opportunities.map((o) => (
            <div key={o.id} className="rounded-xl border border-border-subtle bg-surface p-5">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <a
                    href={o.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="font-display text-lg hover:text-gold-soft hover:underline"
                  >
                    {o.name}
                  </a>
                  <p className="text-sm text-muted">{o.organization}</p>
                </div>
              </div>
              <p className="mt-2 text-sm text-foreground/80">{o.description}</p>
              <p className="mt-2 text-sm text-muted">{o.amount_label}</p>
              <p className="mt-3 text-xs text-muted/70">{o.application_info}</p>
            </div>
          ))}
        </div>
      )}
    </AppShell>
  );
}
