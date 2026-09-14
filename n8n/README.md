# n8n — Automatisation FilmFund Africa

Pipeline visé :

```text
Sites des fonds → Collecte → Analyse IA → Nettoyage → Base de données → Matching → Notification
```

## Statut Phase 6 : le côté FilmFund est câblé, le côté n8n est un modèle

Ce qui est **réellement construit et testé** côté backend/frontend :

- `FundingFollow` : un utilisateur peut suivre un financement (bouton
  "Suivre" sur `/financements` et sur la page projet)
- `Notification` : créée pour chaque suiveur quand un financement suivi
  est mis à jour — visible sur `/notifications`, badge de non-lus dans
  l'en-tête
- `last_verified_at` sur `FundingOpportunity` : horodatage de la dernière
  vérification, mis à jour à chaque upsert (seed manuel ou webhook)
- `POST /api/v1/integrations/n8n/funding-update` : point d'entrée que le
  workflow n8n doit appeler après avoir détecté un changement réel sur le
  site officiel d'un fonds. Protégé par un secret partagé (header
  `X-N8N-Secret`, comparé à `N8N_WEBHOOK_SECRET`) — endpoint désactivé
  (503) si ce secret n'est pas configuré, jamais d'écriture non
  authentifiée acceptée.

Ce qui **reste à faire dans une vraie instance n8n** (ce dépôt ne fait pas
tourner n8n lui-même — pas de Docker dans cet environnement de
développement) :

- Le service `n8n` est présent dans `docker-compose.yml` derrière le
  profil `automation` (`docker compose --profile automation up`)
- [`workflows/funding-watch.example.json`](workflows/funding-watch.example.json)
  est un **modèle à importer et adapter**, pas un workflow prêt à
  tourner : il illustre la structure (déclencheur planifié → récupération
  de la page → détection de changement → appel du webhook), mais la
  vraie logique de détection de changement (`Vérifier le contenu`) est un
  placeholder à écrire spécifiquement pour chaque site de fonds surveillé
  — chaque page a sa propre structure et ses propres évolutions.
- Variables d'environnement attendues côté n8n pour le modèle :
  `FILMFUND_API_URL` (ex. `https://api.filmfundafrica.dev`) et
  `FILMFUND_N8N_SECRET` (même valeur que `N8N_WEBHOOK_SECRET` côté backend).

Quand un vrai workflow fonctionnel existe, exportez-le dans ce dossier au
format JSON (`n8n export:workflow`) pour qu'il soit versionné avec le
reste du projet.

Règle produit (déjà respectée par le modèle de données) : toute
opportunité de financement mise à jour automatiquement conserve `url`,
`organization` et `last_verified_at`, et n'est jamais présentée comme
vérifiée sans cette traçabilité.
