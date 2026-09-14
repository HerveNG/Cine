"use client";

import { useEffect, useState } from "react";
import { api, ApiError } from "@/lib/api";
import type { BudgetCategory, BudgetSummary } from "@/lib/types";

function formatAmount(value: string, currency: string | null) {
  return currency ? `${value} ${currency}` : value;
}

function CategoryCard({
  token,
  projectId,
  category,
  currency,
  onChanged,
}: {
  token: string;
  projectId: number;
  category: BudgetCategory;
  currency: string | null;
  onChanged: () => void;
}) {
  const [label, setLabel] = useState("");
  const [quantity, setQuantity] = useState("1");
  const [unitCost, setUnitCost] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  async function addItem() {
    if (!label.trim() || !unitCost.trim()) return;
    setSaving(true);
    setError(null);
    try {
      await api.createBudgetLineItem(token, projectId, category.id, {
        label,
        quantity,
        unit_cost: unitCost,
      });
      setLabel("");
      setQuantity("1");
      setUnitCost("");
      onChanged();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Impossible d'ajouter la ligne.");
    } finally {
      setSaving(false);
    }
  }

  async function deleteItem(itemId: number) {
    await api.deleteBudgetLineItem(token, projectId, itemId);
    onChanged();
  }

  async function deleteCategory() {
    if (!window.confirm(`Supprimer la catégorie « ${category.name} » et ses lignes ?`)) return;
    await api.deleteBudgetCategory(token, projectId, category.id);
    onChanged();
  }

  return (
    <div className="rounded-xl border border-border-subtle bg-surface p-5">
      <div className="flex items-center justify-between">
        <h3 className="font-display text-lg">{category.name}</h3>
        <div className="flex items-center gap-3">
          <span className="text-sm text-gold-soft">
            {formatAmount(category.subtotal, currency)}
          </span>
          <button
            onClick={deleteCategory}
            className="text-xs text-muted hover:text-danger"
          >
            Supprimer
          </button>
        </div>
      </div>

      {category.line_items.length > 0 && (
        <table className="mt-3 w-full text-sm">
          <thead>
            <tr className="text-left text-xs uppercase tracking-wide text-muted">
              <th className="pb-2 font-normal">Libellé</th>
              <th className="pb-2 font-normal">Qté</th>
              <th className="pb-2 font-normal">Coût unitaire</th>
              <th className="pb-2 font-normal">Sous-total</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {category.line_items.map((item) => (
              <tr key={item.id} className="border-t border-border-subtle/60">
                <td className="py-2">{item.label}</td>
                <td className="py-2">{item.quantity}</td>
                <td className="py-2">{formatAmount(item.unit_cost, currency)}</td>
                <td className="py-2 text-gold-soft">{formatAmount(item.subtotal, currency)}</td>
                <td className="py-2 text-right">
                  <button
                    onClick={() => deleteItem(item.id)}
                    className="text-xs text-muted hover:text-danger"
                  >
                    Retirer
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <div className="mt-4 flex flex-wrap items-end gap-2">
        <input
          value={label}
          onChange={(e) => setLabel(e.target.value)}
          placeholder="Libellé (ex. Cadreur)"
          className="min-w-[160px] flex-1 rounded-md border border-border-subtle bg-background px-3 py-2 text-sm outline-none focus:border-gold"
        />
        <input
          value={quantity}
          onChange={(e) => setQuantity(e.target.value)}
          placeholder="Qté"
          className="w-20 rounded-md border border-border-subtle bg-background px-3 py-2 text-sm outline-none focus:border-gold"
        />
        <input
          value={unitCost}
          onChange={(e) => setUnitCost(e.target.value)}
          placeholder="Coût unitaire"
          className="w-32 rounded-md border border-border-subtle bg-background px-3 py-2 text-sm outline-none focus:border-gold"
        />
        <button
          onClick={addItem}
          disabled={saving}
          className="rounded-md border border-border-subtle px-3 py-2 text-sm hover:border-gold hover:text-gold-soft disabled:opacity-50"
        >
          Ajouter
        </button>
      </div>
      {error && <p className="mt-2 text-sm text-danger">{error}</p>}
    </div>
  );
}

export default function BudgetPanel({ token, projectId }: { token: string; projectId: number }) {
  const [summary, setSummary] = useState<BudgetSummary | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [newCategoryName, setNewCategoryName] = useState("");

  function reload() {
    api
      .getBudget(token, projectId)
      .then(setSummary)
      .catch(() => setError("Impossible de charger le budget."));
  }

  useEffect(reload, [token, projectId]);

  async function addCategory() {
    if (!newCategoryName.trim()) return;
    await api.createBudgetCategory(token, projectId, newCategoryName);
    setNewCategoryName("");
    reload();
  }

  if (error) return <p className="text-sm text-danger">{error}</p>;
  if (!summary) return <p className="text-sm text-muted">Chargement…</p>;

  return (
    <div className="space-y-4">
      {!summary.currency && (
        <p className="rounded-md border border-dashed border-border-subtle p-3 text-sm text-muted">
          Aucune devise définie pour ce projet — renseignez-la ci-dessus (champ « Devise ») pour
          un affichage plus clair des montants.
        </p>
      )}

      {summary.categories.map((category) => (
        <CategoryCard
          key={category.id}
          token={token}
          projectId={projectId}
          category={category}
          currency={summary.currency}
          onChanged={reload}
        />
      ))}

      <div className="flex items-end gap-2">
        <input
          value={newCategoryName}
          onChange={(e) => setNewCategoryName(e.target.value)}
          placeholder="Nouvelle catégorie (ex. Tournage)"
          className="min-w-[220px] flex-1 rounded-md border border-border-subtle bg-surface px-3 py-2 text-sm outline-none focus:border-gold"
        />
        <button
          onClick={addCategory}
          className="rounded-md border border-border-subtle px-3 py-2 text-sm hover:border-gold hover:text-gold-soft"
        >
          Ajouter une catégorie
        </button>
      </div>

      <div className="flex items-center justify-between rounded-xl border border-gold/40 bg-surface p-5">
        <span className="font-display text-lg">Total</span>
        <span className="font-display text-xl text-gold-soft">
          {formatAmount(summary.total, summary.currency)}
        </span>
      </div>
    </div>
  );
}
