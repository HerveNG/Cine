# Prompts IA — FilmFund Africa

Ce dossier accueillera les prompts versionnés pour l'AI Writer (Phase 2), un
par type de document, comme prévu dans le prompt maître :

```text
prompts/
├── synopsis.py
├── intention.py
├── realization.py
├── treatment.py
├── pitch.py
├── scoring.py
└── funding_match.py
```

**Statut Phase 1 : vide.** Le module AI Writer n'est pas encore implémenté.
Aucun prompt n'est codé en dur ailleurs dans le backend — voir
`backend/app/services/` où une couche d'abstraction `AIService` /
`Provider` (OpenAI / Anthropic / modèle local) sera introduite en Phase 2,
configurable via la variable d'environnement `AI_PROVIDER`.

Règle produit : chaque prompt doit recevoir le contexte structuré réel du
projet et ne jamais inventer silencieusement des informations manquantes
(personnages, budgets, financements, dates).
