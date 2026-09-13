Les scripts opérationnels du backend (seed de démo, migrations) vivent dans
`backend/scripts/` pour rester dans le même environnement Python
(`backend/.venv`). Voir `backend/scripts/seed.py` et `database/README.md`.

Ce dossier racine `scripts/` est réservé aux scripts transverses futurs
(déploiement, CI, tâches multi-services) qui ne sont pas spécifiques au
backend ou au frontend.
