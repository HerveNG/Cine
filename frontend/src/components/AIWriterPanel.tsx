"use client";

import { useEffect, useState } from "react";
import { api, ApiError } from "@/lib/api";
import type { AIDocument, DocumentType } from "@/lib/types";
import { DOCUMENT_TYPE_LABELS, DOCUMENT_TYPES } from "@/lib/types";

function DocumentCard({
  token,
  projectId,
  documentType,
  document,
  onChanged,
}: {
  token: string;
  projectId: number;
  documentType: DocumentType;
  document: AIDocument | undefined;
  onChanged: (doc: AIDocument) => void;
}) {
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showImprove, setShowImprove] = useState(false);
  const [instruction, setInstruction] = useState("");
  const [showHistory, setShowHistory] = useState(false);
  const [history, setHistory] = useState<AIDocument[] | null>(null);

  async function run(action: string, fn: () => Promise<AIDocument>) {
    setLoading(action);
    setError(null);
    try {
      const doc = await fn();
      onChanged(doc);
      setShowImprove(false);
      setInstruction("");
      setHistory(null);
      setShowHistory(false);
    } catch (err) {
      if (err instanceof ApiError && err.status === 503) {
        setError("Module IA non configuré côté serveur (AI_PROVIDER).");
      } else {
        setError(err instanceof ApiError ? err.message : "Échec de la génération.");
      }
    } finally {
      setLoading(null);
    }
  }

  async function toggleHistory() {
    if (showHistory) {
      setShowHistory(false);
      return;
    }
    setShowHistory(true);
    if (!history) {
      const versions = await api.listDocumentVersions(token, projectId, documentType);
      setHistory(versions);
    }
  }

  return (
    <div className="rounded-xl border border-border-subtle bg-surface p-5">
      <div className="flex items-center justify-between">
        <h3 className="font-display text-lg">{DOCUMENT_TYPE_LABELS[documentType]}</h3>
        {document && (
          <span className="rounded-full border border-border-subtle px-2 py-0.5 text-[11px] uppercase tracking-wide text-muted">
            v{document.version}
          </span>
        )}
      </div>

      {document ? (
        <p className="mt-3 whitespace-pre-wrap text-sm text-foreground/90">{document.content}</p>
      ) : (
        <p className="mt-3 text-sm text-muted">Pas encore généré.</p>
      )}

      {error && <p className="mt-3 text-sm text-danger">{error}</p>}

      <div className="mt-4 flex flex-wrap gap-2">
        {!document && (
          <button
            onClick={() => run("generate", () => api.generateDocument(token, projectId, documentType))}
            disabled={loading !== null}
            className="rounded-md bg-gold px-3 py-1.5 text-sm font-medium text-[#14140f] hover:opacity-90 disabled:opacity-50"
          >
            {loading === "generate" ? "Génération…" : "Générer"}
          </button>
        )}

        {document && (
          <>
            <button
              onClick={() =>
                run("regenerate", () => api.regenerateDocument(token, projectId, document.id))
              }
              disabled={loading !== null}
              className="rounded-md border border-border-subtle px-3 py-1.5 text-sm hover:border-gold hover:text-gold-soft disabled:opacity-50"
            >
              {loading === "regenerate" ? "Régénération…" : "Régénérer"}
            </button>
            <button
              onClick={() => setShowImprove((v) => !v)}
              disabled={loading !== null}
              className="rounded-md border border-border-subtle px-3 py-1.5 text-sm hover:border-gold hover:text-gold-soft disabled:opacity-50"
            >
              Améliorer
            </button>
            <button
              onClick={() =>
                run("shorten", () => api.shortenDocument(token, projectId, document.id))
              }
              disabled={loading !== null}
              className="rounded-md border border-border-subtle px-3 py-1.5 text-sm hover:border-gold hover:text-gold-soft disabled:opacity-50"
            >
              {loading === "shorten" ? "Raccourcissement…" : "Raccourcir"}
            </button>
            {document.version > 1 && (
              <button
                onClick={toggleHistory}
                className="rounded-md px-3 py-1.5 text-sm text-muted hover:text-foreground"
              >
                {showHistory ? "Masquer l'historique" : "Historique"}
              </button>
            )}
          </>
        )}
      </div>

      {showImprove && document && (
        <div className="mt-3 flex gap-2">
          <input
            value={instruction}
            onChange={(e) => setInstruction(e.target.value)}
            placeholder="Ex. : rends le ton plus intimiste"
            className="flex-1 rounded-md border border-border-subtle bg-background px-3 py-2 text-sm outline-none focus:border-gold"
          />
          <button
            onClick={() =>
              run("improve", () =>
                api.improveDocument(token, projectId, document.id, instruction)
              )
            }
            disabled={loading !== null || !instruction.trim()}
            className="rounded-md bg-gold px-3 py-1.5 text-sm font-medium text-[#14140f] hover:opacity-90 disabled:opacity-50"
          >
            {loading === "improve" ? "…" : "Envoyer"}
          </button>
        </div>
      )}

      {showHistory && history && (
        <ul className="mt-4 space-y-2 border-t border-border-subtle pt-3">
          {history.map((v) => (
            <li key={v.id} className="text-xs text-muted">
              <span className="font-medium text-foreground/80">v{v.version}</span>{" "}
              — {new Date(v.created_at).toLocaleString("fr-FR")}
              <p className="mt-1 line-clamp-2 whitespace-pre-wrap text-foreground/70">
                {v.content}
              </p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default function AIWriterPanel({
  token,
  projectId,
}: {
  token: string;
  projectId: number;
}) {
  const [documents, setDocuments] = useState<Record<string, AIDocument> | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    api
      .listDocuments(token, projectId)
      .then((docs) => {
        const byType: Record<string, AIDocument> = {};
        for (const doc of docs) byType[doc.document_type] = doc;
        setDocuments(byType);
      })
      .catch(() => setLoadError("Impossible de charger les documents IA."));
  }, [token, projectId]);

  if (loadError) {
    return <p className="text-sm text-danger">{loadError}</p>;
  }

  if (!documents) {
    return <p className="text-sm text-muted">Chargement de l&apos;assistant IA…</p>;
  }

  return (
    <div className="grid gap-4 md:grid-cols-2">
      {DOCUMENT_TYPES.map((type) => (
        <DocumentCard
          key={type}
          token={token}
          projectId={projectId}
          documentType={type}
          document={documents[type]}
          onChanged={(doc) => setDocuments((prev) => ({ ...prev, [type]: doc }))}
        />
      ))}
    </div>
  );
}
