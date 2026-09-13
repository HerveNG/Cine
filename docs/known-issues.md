# Known issues — Phase 1 (Foundation)

Ce document liste honnêtement les limites connues du MVP à ce stade, pour
ne jamais laisser croire qu'une fonctionnalité est terminée alors qu'elle
ne l'est pas.

## Sécurité / production-readiness

- **Stockage du JWT côté frontend** : le token est actuellement stocké dans
  `localStorage` (voir `frontend/src/lib/auth-context.tsx`) pour simplifier
  le MVP. C'est vulnérable au XSS. Avant mise en production réelle,
  migrer vers un cookie `httpOnly` + `secure` posé par le backend.
- **Rate limiting** : non implémenté. À ajouter (ex. `slowapi`) avant
  exposition publique, en particulier sur `/auth/login` et `/auth/register`.
- **Réinitialisation de mot de passe** : les schémas Pydantic existent
  (`PasswordResetRequest`, `PasswordResetConfirm`) mais aucun endpoint ni
  envoi d'email réel n'est branché — SMTP n'est pas configuré. Ne pas
  annoncer cette fonctionnalité comme disponible.
- **OAuth Google** : prévu par le prompt maître, non implémenté en Phase 1.

## Fonctionnalités non implémentées (par design, cf. phasage du prompt maître)

- AI Writer (génération de logline, synopsis, notes, traitement, pitch…) —
  Phase 2.
- Funding Intelligence, recherche, matching, scoring — Phase 3.
- Budget, plan de financement, calendrier — Phase 4.
- Abonnements, crédits IA — Phase 5.
- n8n, veille automatisée, notifications — Phase 6.
- Export PDF/DOCX/ZIP — non implémenté.
- Administration (dashboard admin) — non implémenté.
- Internationalisation (FR/EN) — l'interface est en français uniquement.

Le tableau de bord et la page projet reflètent honnêtement cet état : les
compteurs liés aux modules non construits affichent 0 plutôt qu'une valeur
inventée, et des encarts indiquent explicitement "module à venir".

## Choix techniques à trancher plus tard

- `LICENSE` est actuellement une notice propriétaire par défaut — à
  remplacer si une autre licence est souhaitée.
- Les polices sont actuellement des polices système (pas de Google Fonts)
  car l'environnement de build utilisé n'avait pas accès à
  `fonts.googleapis.com`. Aucun impact fonctionnel ; à revoir si une
  identité typographique plus distinctive est souhaitée.
