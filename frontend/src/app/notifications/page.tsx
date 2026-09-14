"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import AppShell from "@/components/AppShell";
import { useAuth } from "@/lib/auth-context";
import { api } from "@/lib/api";
import type { Notification } from "@/lib/types";

export default function NotificationsPage() {
  const { token } = useAuth();
  const [notifications, setNotifications] = useState<Notification[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  function reload() {
    if (!token) return;
    api
      .listNotifications(token)
      .then(setNotifications)
      .catch(() => setError("Impossible de charger les notifications."));
  }

  useEffect(reload, [token]);

  async function markRead(id: number) {
    if (!token) return;
    await api.markNotificationRead(token, id);
    reload();
  }

  async function markAllRead() {
    if (!token) return;
    await api.markAllNotificationsRead(token);
    reload();
  }

  const hasUnread = notifications?.some((n) => !n.is_read);

  return (
    <AppShell>
      <div className="flex items-center justify-between">
        <h1 className="font-display text-2xl">Notifications</h1>
        {hasUnread && (
          <button
            onClick={markAllRead}
            className="rounded-md border border-border-subtle px-3 py-1.5 text-sm hover:border-gold hover:text-gold-soft"
          >
            Tout marquer comme lu
          </button>
        )}
      </div>
      <p className="mt-1 text-sm text-muted">
        Alertes envoyées quand un financement que vous suivez est mis à jour (Phase 6 —
        automatisation).
      </p>

      {error && <p className="mt-4 text-sm text-danger">{error}</p>}

      {!notifications ? (
        <p className="mt-6 text-sm text-muted">Chargement…</p>
      ) : notifications.length === 0 ? (
        <p className="mt-6 text-sm text-muted">
          Aucune notification pour l&apos;instant. Suivez un financement depuis la page{" "}
          <Link href="/financements" className="text-gold-soft hover:underline">
            Financements
          </Link>{" "}
          pour être alerté de ses mises à jour.
        </p>
      ) : (
        <div className="mt-6 space-y-3">
          {notifications.map((n) => (
            <div
              key={n.id}
              className={`rounded-xl border p-5 ${
                n.is_read ? "border-border-subtle bg-surface" : "border-gold/40 bg-surface"
              }`}
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="font-display text-lg">{n.title}</p>
                  <p className="mt-1 text-sm text-foreground/80">{n.body}</p>
                  {n.url && (
                    <a
                      href={n.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="mt-2 inline-block text-sm text-gold-soft hover:underline"
                    >
                      Voir le site officiel
                    </a>
                  )}
                  <p className="mt-2 text-xs text-muted/70">
                    {new Date(n.created_at).toLocaleString("fr-FR")}
                  </p>
                </div>
                {!n.is_read && (
                  <button
                    onClick={() => markRead(n.id)}
                    className="shrink-0 rounded-md border border-border-subtle px-3 py-1.5 text-xs hover:border-gold hover:text-gold-soft"
                  >
                    Marquer comme lu
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </AppShell>
  );
}
