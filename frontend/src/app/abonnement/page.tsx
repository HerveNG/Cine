"use client";

import { useEffect, useState } from "react";
import AppShell from "@/components/AppShell";
import { useAuth } from "@/lib/auth-context";
import { api } from "@/lib/api";
import type { SubscriptionPlan, UsageSummary } from "@/lib/types";
import { PLAN_CREDIT_LIMITS, PLAN_LABELS } from "@/lib/types";

const PLAN_FEATURES: Record<SubscriptionPlan, string[]> = {
  FREE: ["10 générations AI Writer / mois", "Projets illimités", "Financements & budget illimités"],
  PRO: ["100 générations AI Writer / mois", "Projets illimités", "Financements & budget illimités"],
  STUDIO: [
    "Générations AI Writer illimitées",
    "Projets illimités",
    "Financements & budget illimités",
  ],
};

const PLANS: SubscriptionPlan[] = ["FREE", "PRO", "STUDIO"];

export default function AbonnementPage() {
  const { user } = useAuth();
  const [usage, setUsage] = useState<UsageSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user) return;
    api
      .getUsage()
      .then(setUsage)
      .catch(() => setError("Impossible de charger votre abonnement."));
  }, [user]);

  return (
    <AppShell>
      <h1 className="font-display text-2xl">Abonnement</h1>
      <p className="mt-1 text-sm text-muted">
        Les crédits IA sont réellement appliqués : chaque génération, régénération, amélioration
        ou raccourcissement de document via l&apos;Assistant IA consomme 1 crédit.
      </p>

      {error && <p className="mt-4 text-sm text-danger">{error}</p>}

      {usage && (
        <div className="mt-6 max-w-md rounded-xl border border-gold/40 bg-surface p-5">
          <p className="text-sm text-muted">Plan actuel</p>
          <p className="mt-1 font-display text-xl text-gold-soft">{PLAN_LABELS[usage.plan]}</p>

          <div className="mt-4">
            <div className="flex justify-between text-sm text-muted">
              <span>Crédits IA utilisés ce mois-ci</span>
              <span>
                {usage.credits_used}
                {usage.credits_limit !== null ? ` / ${usage.credits_limit}` : " · illimité"}
              </span>
            </div>
            {usage.credits_limit !== null && (
              <div className="mt-2 h-2 overflow-hidden rounded-full bg-background">
                <div
                  className="h-full bg-gold"
                  style={{
                    width: `${Math.min(
                      100,
                      (usage.credits_used / Math.max(usage.credits_limit, 1)) * 100
                    )}%`,
                  }}
                />
              </div>
            )}
          </div>
        </div>
      )}

      <div className="mt-8 grid gap-4 md:grid-cols-3">
        {PLANS.map((plan) => {
          const isCurrent = usage?.plan === plan;
          const limit = PLAN_CREDIT_LIMITS[plan];
          return (
            <div
              key={plan}
              className={`rounded-xl border p-5 ${
                isCurrent ? "border-gold bg-surface" : "border-border-subtle bg-surface"
              }`}
            >
              <div className="flex items-center justify-between">
                <h2 className="font-display text-lg">{PLAN_LABELS[plan]}</h2>
                {isCurrent && (
                  <span className="rounded-full border border-gold px-2 py-0.5 text-[10px] uppercase tracking-wide text-gold-soft">
                    Plan actuel
                  </span>
                )}
              </div>
              <p className="mt-2 text-2xl font-display text-gold-soft">
                {limit === null ? "Illimité" : `${limit} crédits`}
              </p>
              <ul className="mt-4 space-y-1.5 text-sm text-foreground/80">
                {PLAN_FEATURES[plan].map((feature) => (
                  <li key={feature}>• {feature}</li>
                ))}
              </ul>
              {!isCurrent && (
                <a
                  href="mailto:contact@filmfundafrica.dev?subject=Changement de plan FilmFund Africa"
                  className="mt-4 block rounded-md border border-border-subtle px-3 py-2 text-center text-sm hover:border-gold hover:text-gold-soft"
                >
                  Contactez-nous pour changer de plan
                </a>
              )}
            </div>
          );
        })}
      </div>

      <p className="mt-6 text-xs text-muted/70">
        Le paiement en ligne n&apos;est pas encore disponible dans ce MVP — le changement de plan
        se fait manuellement, sans faux bouton de paiement qui ne débiterait rien.
      </p>
    </AppShell>
  );
}
