# Base de données — FilmFund Africa

PostgreSQL, compatible Supabase / Neon / Postgres local (piloté entièrement
par la variable d'environnement `DATABASE_URL`).

Les migrations vivent dans `backend/alembic/` (Alembic + SQLAlchemy 2.0),
co-localisées avec les modèles ORM (`backend/app/models/`) dont elles sont
générées, plutôt que dupliquées ici.

## Schéma Phase 1 (Foundation)

- `users` — comptes et profils (voir `backend/app/models/user.py`)
- `projects` — projets audiovisuels, isolés par `user_id` (voir
  `backend/app/models/project.py`)

## Tables prévues (prompt maître, section 28) — non créées en Phase 1

```text
characters
documents
document_versions
funding_opportunities
funding_requirements
project_funding_matches
budgets
budget_items
funding_plans
notifications
subscriptions
subscription_plans
ai_usage
audit_logs
```

Elles seront ajoutées via de nouvelles migrations Alembic au fur et à
mesure des phases (voir `docs/known-issues.md` pour le détail de ce qui
n'est pas encore construit).

## Commandes utiles

```bash
cd backend
source .venv/bin/activate
alembic upgrade head        # applique les migrations
alembic downgrade base      # revient à un schéma vide
alembic revision --autogenerate -m "message"   # génère une nouvelle migration
python scripts/seed.py      # crée 2 utilisateurs démo + 3 projets démo
```
