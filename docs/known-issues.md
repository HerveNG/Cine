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

- **Quota de crédits appliqué depuis la Phase 5** : `FREE` = 10
  générations/mois, `PRO` = 100/mois, `STUDIO` = illimité. Voir la section
  "Monétisation" ci-dessous.
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

## Funding Intelligence (Phase 3) — limites connues

- **Liste non exhaustive** : 7 financements réels et vérifiés au moment de
  leur ajout (voir `backend/scripts/seed_funding_opportunities.py` pour les
  sources). Ce n'est qu'un point de départ, pas un panorama complet des
  financements disponibles pour le cinéma africain.
- **Pas de dates limites précises stockées** : les deadlines réelles
  changent chaque année et ne sont pas fiables d'une session à l'autre.
  Chaque financement a un champ `application_info` en texte libre
  renvoyant vers le site officiel plutôt qu'une date fixe qu'on ne peut
  pas garantir exacte. Le compteur dashboard `upcoming_deadlines` reste
  donc honnêtement à 0.
- **Éligibilité géographique simplifiée** : `eligible_countries` vide
  signifie "pas de restriction connue", utilisé pour les grands fonds
  internationaux (Hubert Bals, IDFA Bertha, World Cinema Fund, Sørfond)
  qui couvrent des dizaines de pays qu'il ne serait pas raisonnable de
  lister à la main. Une correspondance pays n'est donc garantie que pour
  les fonds à éligibilité strictement définie (ex. AFAC, Durban FilmMart).
- **Score de matching indicatif** : basé sur 3 critères simples (type de
  projet, pays, étape) pondérés arbitrairement (40/35/25) — c'est un
  filtre d'aide à la décision explicable, pas une garantie d'éligibilité
  réelle ; toujours vérifier les critères complets sur le site officiel
  avant de candidater.
- **Pas d'administration** : les financements sont gérés uniquement via
  le script de seed (aucune interface pour en ajouter/modifier depuis
  l'application).

## Budget & calendrier de production (Phase 4) — limites connues

- **Pas de conversion de devise** : la devise est un champ libre par
  projet (ex. "XOF", "EUR"), sans taux de change ni agrégation
  multi-devises — chaque budget reste dans sa devise locale, tel quel.
- **Calendrier = liste chronologique, pas une vue graphique** : les
  jalons sont affichés triés par date, sans diagramme de Gantt ni
  calendrier visuel — suffisant pour ce MVP, mais à ne pas présenter
  comme un outil de planning avancé.
- **Pas d'export** : aucun export PDF/Excel du budget ou du calendrier.
- **Pas de rapprochement budget ↔ financements** : le budget total d'un
  projet et les financements compatibles (Phase 3) ne sont pas encore
  reliés (ex. "combien reste-t-il à financer ?").

## Monétisation (Phase 5) — limites connues

- **Pas de paiement en ligne réel** : aucune intégration Stripe (ou
  équivalent). Changer de plan est une action **administrative**
  (`PUT /api/v1/admin/users/{user_id}/plan`, réservée à `UserType.ADMIN`)
  — un choix délibéré plutôt qu'un faux bouton "Upgrade" qui ne
  débiterait rien et laisserait n'importe qui s'auto-attribuer plus de
  crédits.
- **Paliers fixes en dur** : `PLAN_LIMITS` (`backend/app/services/subscription_service.py`)
  n'est pas configurable depuis l'application — changer un quota
  nécessite une modification de code.
- **Historique d'usage non exposé aux administrateurs** : `AICreditUsage`
  est un ledger auditable en base, mais il n'existe pas encore de vue
  d'ensemble (ex. tous les utilisateurs et leur consommation) — seul
  l'utilisateur voit son propre usage via `/abonnement`.

## Fonctionnalités non implémentées (par design, cf. phasage du prompt maître)

- n8n, veille automatisée, notifications — Phase 6.
- Export PDF/DOCX/ZIP — non implémenté.
- Administration (dashboard admin) — non implémenté ; seul un endpoint
  API admin-only existe (changement de plan, Phase 5), pas d'interface.
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
