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

## AI Writer (Phase 2) — limites connues

- **Pas de quota/crédits** : n'importe quel utilisateur authentifié peut
  générer un nombre illimité de documents (chaque appel consomme de vraies
  requêtes Anthropic, donc du budget réel). Le système de crédits IA est
  prévu en Phase 5.
- **Un seul provider réel branché** : `AnthropicProvider` (Claude). L'
  abstraction (`app/services/ai/base.py`) permet d'ajouter un provider
  OpenAI sans changer les endpoints, mais ce n'est pas fait.
- **Pas de streaming** : la génération bloque la requête HTTP jusqu'à la
  réponse complète du modèle (pas de affichage progressif côté frontend).
- **Contenu généré non éditable manuellement** : l'utilisateur peut
  régénérer/améliorer/raccourcir via l'IA, mais ne peut pas encore corriger
  le texte à la main et sauvegarder cette correction comme nouvelle version.
- **`AI_PROVIDER=none`** (valeur par défaut de `.env.example`) désactive
  volontairement le module : les endpoints `/documents/*` renvoient alors
  une erreur 503 explicite plutôt que de simuler une génération.

## Fonctionnalités non implémentées (par design, cf. phasage du prompt maître)

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
