# FilmFund Africa

**De l'idée au financement de votre projet audiovisuel.**

SaaS destiné aux auteurs, réalisateurs et producteurs africains — développement
de projets audiovisuels, génération de documents assistée par IA, recherche
et matching de financements, budgets et export de dossier.

> **Statut : MVP — Phases 1 à 5 livrées.** Authentification, gestion des
> utilisateurs, CRUD projets, tableau de bord, AI Writer (génération de
> documents par IA, versionnés), Funding Intelligence (recherche et matching
> à score explicable sur des financements réels), Budget & plan de
> financement (catégories, sous-totaux calculés, calendrier de production)
> et Monétisation (plans Gratuit/Pro/Studio, crédits IA réellement
> appliqués) sont réellement fonctionnels et testés. Seul le module n8n
> (Phase 6) n'est **pas encore implémenté** — voir
> [docs/known-issues.md](docs/known-issues.md) pour le détail honnête de
> ce qui manque, notamment l'absence de paiement en ligne réel.

## Stack

- **Frontend** : Next.js 15 (App Router) + React 19 + TypeScript + Tailwind CSS 4
- **Backend** : FastAPI (Python 3.11) + SQLAlchemy 2.0 + Alembic
- **Base de données** : PostgreSQL 16 (compatible Supabase / Neon / local)
- **Auth** : JWT (bcrypt pour le hash des mots de passe)
- **IA (AI Writer)** : couche d'abstraction provider — Anthropic (Claude)
  ou OpenAI (ChatGPT) en production, ou un provider `local` déterministe
  sans appel réseau (défaut hors-ligne et utilisé par les tests automatisés)
- **Conteneurisation** : Docker / Docker Compose
- **Automatisation (prévu)** : n8n

## Arborescence

```text
filmfund-africa/ (ce dépôt)
├── frontend/          # Next.js + TypeScript + Tailwind
├── backend/           # FastAPI (api/core/models/schemas/services/repositories/workers)
├── database/          # Doc du schéma (migrations réelles dans backend/alembic/)
├── n8n/               # Automatisation (Phase 6, non connectée)
├── prompts/           # Prompts IA versionnés (Phase 2, vide pour l'instant)
├── docs/              # Documentation, known-issues
├── scripts/           # Scripts transverses (voir backend/scripts/ pour le seed)
├── docker-compose.yml
├── .env.example
├── README.md
└── LICENSE
```

## 1. Installation

Prérequis : Node.js 20+, Python 3.11+, PostgreSQL 16 (ou Docker).

```bash
git clone <ce-depot>
cd Cine
cp .env.example .env
```

Éditez `.env` et remplacez au minimum `JWT_SECRET` par une valeur aléatoire
longue avant tout déploiement réel.

## 2. Configuration — variables d'environnement

Voir `.env.example` à la racine pour la liste complète (Postgres, JWT, IA,
n8n, SMTP, stockage). Le frontend lit `NEXT_PUBLIC_API_URL` depuis
`frontend/.env.local` (copiez `frontend/.env.local.example`).

**Ne jamais committer de vraies clés API ou secrets dans le dépôt.**

## 3. Lancement avec Docker (recommandé)

```bash
docker compose up --build
```

- Frontend : http://localhost:3000
- Backend (API + docs Swagger) : http://localhost:8000/docs
- PostgreSQL : localhost:5432

Le conteneur backend applique automatiquement les migrations Alembic au
démarrage (`alembic upgrade head`).

Pour activer n8n (optionnel, non câblé à un workflow en Phase 1) :

```bash
docker compose --profile automation up
```

## 4. Lancement en local sans Docker

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt   # ou requirements.txt en production
cp .env.example .env   # puis ajustez DATABASE_URL etc. (ou copiez depuis la racine)
```

Créez la base Postgres localement, par exemple :

```bash
sudo -u postgres psql -c "CREATE USER filmfund WITH PASSWORD 'filmfund';"
sudo -u postgres psql -c "CREATE DATABASE filmfund OWNER filmfund;"
```

Puis :

```bash
alembic upgrade head                        # migration database
python scripts/seed.py                      # seed (2 utilisateurs démo + 3 projets démo)
python scripts/seed_funding_opportunities.py  # seed (7 financements réels, Phase 3)
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Ouvrez http://localhost:3000.

## 5. Tests

```bash
cd backend
source .venv/bin/activate
# Nécessite une base filmfund_test en plus de filmfund (voir database/README.md)
sudo -u postgres psql -c "CREATE DATABASE filmfund_test OWNER filmfund;"
python -m pytest -v
```

Les tests s'exécutent contre une vraie base PostgreSQL (pas de mock), et
couvrent notamment l'isolation stricte des données entre utilisateurs
(`tests/test_projects.py::test_user_cannot_access_another_users_project`).

Frontend :

```bash
cd frontend
npm run lint
npm run build
```

## 6. Comptes de démonstration (après `python scripts/seed.py`)

| Email | Mot de passe | Rôle | Plan |
|---|---|---|---|
| demo.realisatrice@filmfundafrica.dev | Demo1234! | Réalisatrice | Gratuit |
| demo.producteur@filmfundafrica.dev | Demo1234! | Producteur | Pro |
| demo.admin@filmfundafrica.dev | Demo1234! | Administratrice | Studio |

Le compte admin peut changer le plan d'un autre utilisateur via
`PUT /api/v1/admin/users/{user_id}/plan` (aucune interface graphique
d'administration pour l'instant — voir known-issues.md).

## 7. Déploiement

Ce MVP n'a pas encore de pipeline de déploiement dédié. Le `docker-compose.yml`
sert de base : en production, séparez la base de données (ex. instance
Supabase/Neon managée), servez le frontend derrière un CDN/reverse proxy,
utilisez des secrets gérés (pas de `.env` en clair), et activez HTTPS.

---

## Rapport de livraison — Phases 1 à 5

### FEATURES IMPLEMENTED

- Architecture backend modulaire (`api/core/models/schemas/services/repositories/workers`)
- PostgreSQL réel + migrations Alembic (cycle upgrade/downgrade vérifié)
- Authentification : inscription, connexion, JWT, `/auth/me`, hash bcrypt
- Modèle utilisateur complet (profil, type : AUTHOR/DIRECTOR/PRODUCER/INSTITUTION/ADMIN)
- CRUD Projets complet (create/list/get/update/delete) avec **isolation stricte
  par utilisateur** (testée : un utilisateur ne peut jamais lire/modifier/supprimer
  le projet d'un autre — 404, pas 403, pour ne pas révéler l'existence de l'ID)
- **AI Writer (Phase 2)** : génération par IA de 6 types de documents par
  projet (logline, synopsis court/long, note d'intention, traitement, pitch),
  avec versioning complet (chaque génération/régénération/amélioration/
  raccourcissement crée une nouvelle version, jamais d'écrasement) et
  historique consultable. Couche d'abstraction `AIProvider` avec trois
  implémentations : `anthropic` (Claude, vérifié en conditions réelles),
  `openai` (ChatGPT, sélection et gestion d'erreur testées — clé API à
  insérer plus tard) et `local` (déterministe, sans réseau — utilisé par
  les tests et comme option hors-ligne), toutes pilotées par
  `AI_PROVIDER`/`AI_API_KEY`/`AI_MODEL`. Isolation utilisateur héritée
  du CRUD projets (404 sur un document d'un projet qui n'est pas le sien).
  Endpoints sous `/api/v1/projects/{project_id}/documents/*`.
- **Funding Intelligence (Phase 3)** : 7 financements réels et curatés
  (Fonds Image de la Francophonie, Hubert Bals Fund, IDFA Bertha Fund,
  World Cinema Fund, Sørfond, AFAC, Durban FilmMart Development Fund —
  sources dans `backend/scripts/seed_funding_opportunities.py`), page
  `/financements` avec recherche/filtres (type de projet, pays, texte
  libre), et matching projet↔financement avec **score explicable sur 100**
  (40 pts type de projet, 35 pts pays, 25 pts étape de développement —
  chaque critère est affiché ✓/✗, aucune boîte noire). Aucune donnée
  fictive : les critères d'éligibilité larges (dizaines de pays) sont
  traités comme "non restreints" plutôt que listés arbitrairement, et les
  dates limites précises ne sont pas stockées (elles changent chaque
  année) — un champ texte renvoie vers le site officiel.
- **Budget & plan de financement (Phase 4)** : catégories de budget par
  projet, lignes en quantité × coût unitaire, sous-totaux et total
  **calculés côté backend à chaque lecture** (jamais stockés — une seule
  source de vérité, aucun risque de désynchronisation), devise libre par
  projet (XOF, EUR, USD…, sans conversion automatique). Calendrier de
  production : jalons (titre, dates, notes) triés chronologiquement — une
  liste, pas une vue calendrier graphique (hors scope pour ce MVP).
  Isolation utilisateur héritée du CRUD projets, cascade de suppression
  (supprimer une catégorie supprime ses lignes, supprimer un projet
  supprime tout). Endpoints sous `/api/v1/projects/{project_id}/budget/*`
  et `/api/v1/projects/{project_id}/milestones`.
- Dashboard : statistiques réelles (projets, documents générés,
  opportunités compatibles avec score ≥ 60) ; seules les échéances
  précises restent à 0, honnêtement (non trackées)
- Frontend Next.js complet : landing page, inscription, connexion, dashboard
  avec recommandations de financement réelles, liste/création/édition/
  suppression de projets, panneaux "Assistant IA", "Financements
  compatibles", "Budget" et "Calendrier de production" par projet,
  navigation avec modules futurs clairement marqués "Bientôt"
- Design premium sobre et cinématographique (fond sombre, accents or)
- Docker Compose (frontend + backend + postgres, n8n en option)
- **Monétisation (Phase 5)** : plans `FREE` (10 crédits IA/mois), `PRO`
  (100/mois) et `STUDIO` (illimité). 1 crédit = 1 appel réussi à l'AI
  Writer (generate/regenerate/improve/shorten) — un appel qui échoue ne
  consomme jamais de crédit (testé explicitement). Quota réellement
  appliqué : `HTTPException 402` avec message clair au-delà du quota.
  Page `/abonnement` (usage en cours, comparatif des plans). Pas de
  paiement en self-service : changer de plan est une action **admin**
  (`PUT /api/v1/admin/users/{user_id}/plan`, protégée par le rôle
  `UserType.ADMIN`) plutôt qu'un faux bouton de paiement qui ne
  débiterait rien.
- Seed de démonstration (3 utilisateurs — dont un compte admin —, 3
  projets, 7 financements réels)
- 38 tests backend automatisés, exécutés contre une vraie base PostgreSQL
  (AI Writer forcé sur le provider `local` en tests — jamais d'appel réseau
  ni de dépendance à une clé API dans la suite automatisée ; le matching
  de financements, les calculs de budget et les quotas de crédits sont
  déterministes, sans IA)
- Build frontend (TypeScript strict + ESLint) sans erreur

### FEATURES PARTIALLY IMPLEMENTED

- Réinitialisation de mot de passe : schémas définis, endpoint et envoi
  d'email **non branchés**
- Système de rôles : `UserType.ADMIN` a maintenant un premier usage réel
  d'autorisation différenciée (changer le plan d'un utilisateur), mais
  c'est le seul — pas encore de véritable interface d'administration, et
  les autres types de rôle (`AUTHOR`/`DIRECTOR`/`PRODUCER`/`INSTITUTION`)
  restent purement déclaratifs (mêmes droits sur leurs propres données).

### KNOWN ISSUES

Voir [docs/known-issues.md](docs/known-issues.md) pour le détail complet :
JWT stocké en `localStorage` (à migrer vers cookie httpOnly avant prod), pas
de rate limiting, pas d'OAuth Google, polices système par défaut (pas de
dépendance Google Fonts).

### ENVIRONMENT VARIABLES

Voir `.env.example` (racine) et `frontend/.env.local.example`.

### HOW TO RUN

Voir sections 3 et 4 ci-dessus (`docker compose up --build`, ou backend +
frontend séparément).

### NEXT STEPS (Phase 6 et suivantes, cf. prompt maître)

1. **Phase 6 — Automatisation** : workflows n8n de veille des financements,
   notifications (ex. nouvelle session de dépôt sur un fonds suivi).
2. Durcissement sécurité avant prod : cookies httpOnly, rate limiting,
   audit logs, OAuth Google.
3. AI Writer : vérifier le provider OpenAI avec une vraie clé API (la
   sélection et la gestion d'erreur sont testées, pas encore un appel
   réseau réel — voir known-issues.md), streaming de la réponse IA,
   édition manuelle du contenu généré avant sauvegarde.
4. Funding Intelligence : élargir la liste de financements au-delà des 7
   premiers, ajouter le suivi de dates limites réelles (actuellement non
   stocké, voir known-issues.md).
5. Budget : export PDF/Excel, conversion de devise indicative, plan de
   financement (rapprochement budget ↔ financements obtenus).
6. Monétisation : paiement en ligne réel (Stripe ou équivalent), pour que
   le changement de plan ne soit plus une action admin-only.
