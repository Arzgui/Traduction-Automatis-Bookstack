# Automatisation de la Traduction BookStack

Ce projet permet de traduire automatiquement les contenus de BookStack (livres, chapitres, pages) dans plusieurs langues, grâce à l'intégration de **LibreTranslate**, à une gestion de **mapping automatique** et à une interface en ligne de commande ou webhook.

## Sommaire

- [Fonctionnalités](#-fonctionnalités)
- [Pré-requis](#-pré-requis)
- [Installation](#️-installation)
- [Lancer LibreTranslate](#-lancer-libretranslate-serveur-de-traduction)
- [Modes d'utilisation](#-modes-dutilisation)
  - [1. Mode automatique (webhook)](#1-mode-automatique-webhook)
  - [2. Mode manuel (interface-CLI)](#2-mode-manuel-interface-cli)
  - [3. Maintenance du mapping](#3-maintenance-du-mapping)
  - [4. Exécuter les tests](#4-exécuter-les-tests)
- [Configuration](#️-configuration)
- [Structure du projet](#️-structure-du-projet)
- [Sécurité](#-sécurité)
- [Auteur](#-auteur)

## Fonctionnalités

- Traduction automatique des livres, chapitres et pages
- Déclenchement automatique via webhook (BookStack)
- Interface manuelle (CLI) pour traductions ponctuelles
- Mapping entre contenus source et traduits stocké localement
- Outils de nettoyage et maintenance du mapping
- Compatible avec une instance locale ou distante de **LibreTranslate**

## Pré-requis

- Python **3.9+**
- `pip` installé (`python -m ensurepip`)
- Docker (optionnel, pour exécuter LibreTranslate)
- Accès à une instance BookStack + clé API
- Git pour cloner le projet

## Installation

```bash
git clone https://github.com/<votre-utilisateur>/automatisation-traduction-bookstack.git
cd automatisation-traduction-bookstack
```

Créer un environnement virtuel (fortement recommandé) :

```bash
python -m venv venv
source venv/bin/activate  # Sous Windows : venv\Scripts\activate
```

Installer les dépendances :

```bash
pip install -r requirements.txt
```

## Lancer LibreTranslate (serveur de traduction)

**Option recommandée via Docker :**

```bash
docker run -p 5000:5000 libretranslate/libretranslate
```

**Autonome (Linux uniquement) :** Voir LibreTranslate sur GitHub

Vérifiez que dans `config.py` ou `.env`, l'URL soit correcte :

```python
LIBRETRANSLATE_URL = "http://127.0.0.1:5000/translate"
```

## Modes d'utilisation

### 1. Mode automatique (webhook)

Lance le serveur :

```bash
python webhook_server.py 5050
```

Configurez un webhook dans l'interface BookStack avec l'URL :

```
http://<votre-domaine-ou-url-ngrok>:5050/webhook
```

Chaque modification (livre, page, chapitre) déclenchera automatiquement une traduction.

### 2. Mode manuel (interface CLI)

Lance le menu interactif :

```bash
python main.py
```

Ce mode permet de :
- Traduire un livre entier
- Mettre à jour manuellement une page ou un chapitre
- Réexécuter la synchronisation ponctuellement

### 3. Maintenance du mapping

Reconstruit le mapping local pour refléter les contenus existants :

```bash
python sync_mapping.py
```

### 4. Exécuter les tests

Lance tous les tests unitaires :

```bash
python -m unittest discover tests
```

## Configuration

Modifiez le fichier `config.py` (ou `.env`) :

```python
BOOKSTACK_API_BASE = "https://votre-instance.bookstack.com/api"
BOOKSTACK_HEADERS = {"Authorization": "Token VOTRE_TOKEN"}
LIBRETRANSLATE_URL = "http://127.0.0.1:5000/translate"
TARGET_LANGS = ["en", "de"]  # Langues cibles
```

## Structure du projet

| Dossier/Fichier | Description |
|----------------|-------------|
| `api/` | Accès aux entités BookStack via l'API |
| `translation/` | Service de traduction et logique de synchronisation |
| `webhook/` | Serveur webhook (mode automatique) |
| `db/` | Mapping entre contenus source et traduits |
| `main.py` | Menu CLI interactif |
| `sync_mapping.py` | Script de nettoyage et de reconstruction du mapping |
| `tests/` | Tests automatisés |

## Sécurité

- **Ne jamais versionner** vos fichiers `.env` ou contenant un token. Ajoutez bien `.env` dans `.gitignore`.

## Auteur

Projet conçu et maintenu par **Arzgui**. Pour toute question, contribution ou bug, merci d'ouvrir une *issue*.