# Automatisation Traduction BookStack

Ce projet permet la synchronisation multilingue automatisée de contenus BookStack (livres, chapitres, pages) avec gestion des webhooks, mapping, traduction automatique et outils de maintenance.

## Structure du projet

- `api/` : Accès API BookStack (livres, chapitres, pages, mapping)
- `translation/` : Traduction et synchronisation (orchestration, services de traduction)
- `webhook/` : Serveur webhook pour réception des notifications BookStack
- `utils/` : Utilitaires (fichiers, logs, etc.)
- `db/` : Mapping entre entités source et traduites
- `tests/` : Tests unitaires
- `main.py` : Point d'entrée CLI (mode manuel)
- `webhook_server.py` : Serveur webhook (mode automatique)
- `sync_mapping.py` : Script de maintenance du mapping

## Fonctionnalités principales

- Traduction automatique de livres, chapitres, pages BookStack (via LibreTranslate ou autre API)
- Mapping centralisé entre entités source et traduites
- Synchronisation automatique via webhook ou manuelle via CLI
- Nettoyage et enrichissement du mapping (livres, chapitres, pages)
- Tests unitaires pour chaque module

## Utilisation

### 1. Mode automatique (webhook)
- Lancer le serveur webhook :
  ```sh
  python webhook_server.py 5050
  ```
- Configurer le webhook dans BookStack pour pointer vers l'URL publique de `/webhook`
- Toute modification dans BookStack sera traduite et synchronisée automatiquement

### 2. Mode manuel (CLI)
- Lancer le menu interactif :
  ```sh
  python main.py
  ```
- Suivre les instructions pour traduire ou mettre à jour livres, chapitres, pages

### 3. Maintenance du mapping
- Enrichir et nettoyer le mapping :
  ```sh
  python sync_mapping.py
  ```

### 4. Lancer les tests unitaires
- Depuis la racine du projet :
  ```sh
  python -m unittest discover tests
  ```

## Configuration
- Modifier `config.py` pour adapter l'URL BookStack, les tokens API, les langues cibles, etc.
- Le mapping est stocké dans `db/mapping.json`

## Extensibilité
- Le projet est modulaire : chaque brique (API, mapping, traduction, synchronisation, webhook) peut être adaptée ou remplacée facilement.
- Ajoutez vos propres modules ou adaptez la logique métier selon vos besoins.

## Auteurs
- Projet initial et refactoring : Karez & GitHub Copilot

---

Pour toute question ou contribution, ouvrez une issue ou contactez l'auteur.
