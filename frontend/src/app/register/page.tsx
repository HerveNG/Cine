"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import { useAuth } from "@/lib/auth-context";
import { ApiError } from "@/lib/api";
import type { UserType } from "@/lib/types";

const USER_TYPES: { value: UserType; label: string }[] = [
  { value: "AUTHOR", label: "Auteur" },
  { value: "DIRECTOR", label: "Réalisateur" },
  { value: "PRODUCER", label: "Producteur" },
  { value: "INSTITUTION", label: "Institution" },
];

export default function RegisterPage() {
  const { register } = useAuth();
  const router = useRouter();
  const [form, setForm] = useState({
    prenom: "",
    nom: "",
    email: "",
    password: "",
    pays: "",
    user_type: "AUTHOR" as UserType,
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
      await register(form);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Une erreur est survenue.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-6 py-12 text-foreground">
      <div className="w-full max-w-md">
        <Link href="/" className="font-display text-lg text-gold-soft">
          FilmFund Africa
        </Link>
        <h1 className="mt-6 font-display text-2xl">Créer votre compte</h1>

        <form onSubmit={handleSubmit} className="mt-8 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="mb-1 block text-sm text-muted">Prénom</label>
              <input
                value={form.prenom}
                onChange={(e) => update("prenom", e.target.value)}
                className="w-full rounded-md border border-border-subtle bg-surface px-3 py-2 outline-none focus:border-gold"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm text-muted">Nom</label>
              <input
                value={form.nom}
                onChange={(e) => update("nom", e.target.value)}
                className="w-full rounded-md border border-border-subtle bg-surface px-3 py-2 outline-none focus:border-gold"
              />
            </div>
          </div>

          <div>
            <label className="mb-1 block text-sm text-muted">Email</label>
            <input
              type="email"
              required
              value={form.email}
              onChange={(e) => update("email", e.target.value)}
              className="w-full rounded-md border border-border-subtle bg-surface px-3 py-2 outline-none focus:border-gold"
            />
          </div>

          <div>
            <label className="mb-1 block text-sm text-muted">Mot de passe</label>
            <input
              type="password"
              required
              minLength={8}
              value={form.password}
              onChange={(e) => update("password", e.target.value)}
              className="w-full rounded-md border border-border-subtle bg-surface px-3 py-2 outline-none focus:border-gold"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="mb-1 block text-sm text-muted">Pays</label>
              <input
                value={form.pays}
                onChange={(e) => update("pays", e.target.value)}
                placeholder="Cameroun"
                className="w-full rounded-md border border-border-subtle bg-surface px-3 py-2 outline-none focus:border-gold"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm text-muted">Profil</label>
              <select
                value={form.user_type}
                onChange={(e) => update("user_type", e.target.value as UserType)}
                className="w-full rounded-md border border-border-subtle bg-surface px-3 py-2 outline-none focus:border-gold"
              >
                {USER_TYPES.map((t) => (
                  <option key={t.value} value={t.value}>
                    {t.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {error && <p className="text-sm text-danger">{error}</p>}

          <button
            type="submit"
            disabled={submitting}
            className="w-full rounded-md bg-gold px-4 py-2 font-medium text-[#14140f] transition-opacity hover:opacity-90 disabled:opacity-50"
          >
            {submitting ? "Création…" : "Créer mon compte"}
          </button>
        </form>

        <p className="mt-6 text-sm text-muted">
          Déjà un compte ?{" "}
          <Link href="/login" className="text-gold-soft hover:underline">
            Se connecter
          </Link>
        </p>
      </div>
    </div>
  );
}
