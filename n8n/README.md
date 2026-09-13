# n8n — Automatisation FilmFund Africa

Prévu pour la Phase 6 (veille automatisée) :

```text
Sites des fonds → Collecte → Analyse IA → Nettoyage → Base de données → Matching → Notification
```

**Statut Phase 1 : non connecté.** Le service `n8n` est présent dans
`docker-compose.yml` derrière le profil `automation` (`docker compose --profile automation up`)
mais aucun workflow n'est encore exporté ici.

Quand des workflows seront créés, exportez-les dans ce dossier au format
JSON (`n8n export:workflow`) pour qu'ils soient versionnés avec le reste du
projet.

Règle produit : toute opportunité de financement collectée automatiquement
doit conserver `source_url`, `source_name` et `last_verified_at`, et ne
jamais être présentée comme active sans cette traçabilité.
