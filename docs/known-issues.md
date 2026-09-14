# Known issues — Phases 1 à 6

Ce document liste honnêtement les limites connues du MVP à ce stade, pour
ne jamais laisser croire qu'une fonctionnalité est terminée alors qu'elle
ne l'est pas.

**Déployé en ligne** (démo) : frontend https://filmfund-africa.vercel.app,
backend https://filmfund-africa-backend.vercel.app, base Supabase avec
données de démo. IA désactivée (`AI_PROVIDER=none`) — voir § 7 du README.
Les limites ci-dessous restent valables pour ce déploiement de démo.

## Sécurité / production-readiness

### Corrigé — revue de sécurité post-Phase 6

- **Faille de privilège critique corrigée** : jusqu'à cette revue,
  `POST /auth/register` acceptait `"user_type": "ADMIN"` dans le corps de
  la requête — n'importe qui pouvait s'auto-attribuer les droits admin
  (utilisés depuis la Phase 5 pour changer le plan de n'importe quel
  utilisateur). `UserCreate` rejette maintenant explicitement ADMIN à
  l'inscription (`app/schemas/user.py`) ; les comptes admin ne sont créés
  que hors ligne (`scripts/seed.py` ou accès DB direct). Testé
  (`tests/test_auth.py::test_register_rejects_self_assigned_admin_role`).
- **JWT en cookie httpOnly** : le token ne voyage plus jamais dans le
  corps JSON ni dans `localStorage` — uniquement via un cookie
  `httpOnly` + `SameSite=Lax` posé par le backend
  (`app/core/security.py::set_access_token_cookie`), immunisé contre le
  vol de token par XSS. `SameSite=Lax` suffit comme protection CSRF pour
  une API JSON appelée via `fetch` (pas de cookie envoyé sur une requête
  cross-site hors navigation de premier niveau), sans jeton CSRF
  supplémentaire. L'en-tête `Authorization: Bearer` reste accepté en
  repli côté backend — délibérément, pour que la suite de tests et
  Swagger `/docs` continuent de fonctionner sans réécriture, pas un
  oubli de compatibilité.
- **Rate limiting** : `slowapi`, 5 tentatives/minute par IP sur
  `/auth/login` et `/auth/register` (`app/core/rate_limit.py`).
- **En-têtes de sécurité** : `X-Content-Type-Options`, `X-Frame-Options`,
  `Referrer-Policy`, `Permissions-Policy` sur toutes les réponses
  (`app/core/security_headers.py`) ; `Strict-Transport-Security`
  uniquement quand `ENVIRONMENT=production` (HSTS n'a pas de sens en
  HTTP local).
- **`JWT_SECRET` par défaut bloqué en production** : l'application refuse
  de démarrer si `ENVIRONMENT=production` et que `JWT_SECRET` vaut
  encore le placeholder commité dans ce dépôt public
  (`app/core/config.py`).
- **Secret webhook n8n comparé en temps constant** : `secrets.compare_digest`
  au lieu d'un `!=` naïf, qui aurait pu laisser deviner le secret
  octet par octet via la mesure du temps de réponse.
- **Validation renforcée** : mot de passe minimum 8 caractères à
  l'inscription ; montants de budget (`quantity`, `unit_cost`) et durées
  de projet non négatifs ; libellés non vides ; date de fin de jalon
  jamais antérieure à la date de début.

### Restant à faire

- **Réinitialisation de mot de passe** : les schémas Pydantic existent
  (`PasswordResetRequest`, `PasswordResetConfirm`) mais aucun endpoint ni
  envoi d'email réel n'est branché — SMTP n'est pas configuré. Ne pas
  annoncer cette fonctionnalité comme disponible.
- **OAuth Google** : prévu par le prompt maître, non implémenté.
- **Pas de CSP (Content-Security-Policy)** : les en-têtes ajoutés
  couvrent le clickjacking/MIME-sniffing/referrer, mais pas encore une
  politique CSP complète (plus complexe à régler sans casser le frontend
  Next.js) ni d'audit de dépendances automatisé (`pip-audit`/`npm audit`
  en CI).
- **Rate limiting en mémoire, pas partagé** : `slowapi` stocke les
  compteurs en mémoire du process — suffisant pour un déploiement
  mono-process, mais à basculer sur Redis si l'app tourne un jour sur
  plusieurs workers/instances (sinon chaque instance a sa propre limite).

## AI Writer (Phase 2) — limites connues

- **Quota de crédits appliqué depuis la Phase 5** : `FREE` = 10
  générations/mois, `PRO` = 100/mois, `STUDIO` = illimité. Voir la section
  "Monétisation" ci-dessous.
- **Deux providers réels branchés** : `anthropic` (Claude) et `openai`
  (ChatGPT), sélectionnables via `AI_PROVIDER`/`AI_API_KEY`/`AI_MODEL` —
  aucun changement d'endpoint requis grâce à l'abstraction
  (`app/services/ai/base.py`). Le provider `openai` n'a pas encore été
  vérifié avec une vraie clé API (clé à insérer ultérieurement) : la
  sélection et la gestion d'erreur sont testées (`tests/test_ai_factory.py`),
  mais pas un appel réseau réel comme pour `anthropic`.
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

## Automatisation (Phase 6) — limites connues

- **Le workflow n8n est un modèle, pas une automatisation qui tourne** :
  cet environnement de développement ne fait pas tourner n8n (pas de
  Docker). `n8n/workflows/funding-watch.example.json` illustre la
  structure (déclencheur planifié → récupération de page → détection de
  changement → appel du webhook), mais la logique de détection de
  changement par site officiel (`Vérifier le contenu`) est un
  placeholder à écrire spécifiquement pour chaque fonds surveillé —
  chaque page a sa propre structure. Ce qui est réellement construit et
  testé, c'est le **côté FilmFund** de la chaîne : suivre un financement,
  webhook authentifié (`POST /api/v1/integrations/n8n/funding-update`,
  secret partagé requis), notification des suiveurs, `last_verified_at`.
- **Un seul canal de notification** : en base, consultées dans
  l'application (page `/notifications` + badge). Pas d'email ni de push.
- **Pas de déduplication avancée** : chaque appel webhook crée une
  nouvelle notification pour chaque suiveur, même si le changement est
  mineur — c'est au workflow n8n (le "Vérifier le contenu" côté n8n) de
  ne déclencher l'appel que sur un changement réel, pas au backend de
  filtrer a posteriori.

## Fonctionnalités non implémentées (par design, cf. phasage du prompt maître)

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
