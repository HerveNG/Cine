"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { FundingMatch } from "@/lib/types";

function CriterionBadge({ ok, label }: { ok: boolean; label: string }) {
  return (
    <span className={ok ? "text-gold-soft" : "text-muted/60"}>
      {ok ? "✓" : "✗"} {label}
    </span>
  );
}

export default function FundingMatchesPanel({
  token,
  projectId,
}: {
  token: string;
  projectId: number;
}) {
  const [matches, setMatches] = useState<FundingMatch[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .getFundingMatches(token, projectId)
      .then(setMatches)
      .catch(() => setError("Impossible de charger les financements compatibles."));
  }, [token, projectId]);

  if (error) return <p className="text-sm text-danger">{error}</p>;
  if (!matches) return <p className="text-sm text-muted">Chargement…</p>;
  if (matches.length === 0) {
    return <p className="text-sm text-muted">Aucun financement référencé pour l&apos;instant.</p>;
  }

  return (
    <div className="space-y-3">
      {matches.map((m) => (
        <div
          key={m.opportunity.id}
          className="rounded-xl border border-border-subtle bg-surface p-5"
        >
          <div className="flex items-start justify-between gap-4">
            <div>
              <a
                href={m.opportunity.url}
                target="_blank"
                rel="noopener noreferrer"
                className="font-display text-lg hover:text-gold-soft hover:underline"
              >
                {m.opportunity.name}
              </a>
              <p className="text-sm text-muted">{m.opportunity.organization}</p>
            </div>
            <span className="shrink-0 rounded-full border border-border-subtle px-2.5 py-1 text-xs font-medium text-gold-soft">
              {m.score}/100
            </span>
          </div>

          <p className="mt-2 text-sm text-foreground/80">{m.opportunity.description}</p>
          <p className="mt-2 text-sm text-muted">{m.opportunity.amount_label}</p>

          <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-xs">
            <CriterionBadge ok={m.project_type_match} label="Type de projet" />
            <CriterionBadge ok={m.country_match} label="Pays" />
            <CriterionBadge ok={m.stage_match} label="Étape du projet" />
          </div>

          <p className="mt-3 text-xs text-muted/70">{m.opportunity.application_info}</p>
        </div>
      ))}
    </div>
  );
}
