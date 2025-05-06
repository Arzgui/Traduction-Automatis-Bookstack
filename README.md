# Automatisation de la Traduction BookStack

Ce projet permet de traduire automatiquement les contenus de BookStack (livres, chapitres, pages) en plusieurs langues, avec gestion des webhooks, mapping automatique, et une interface en ligne de commande.

---

## Sommaire

- [Fonctionnalités](#fonctionnalités)
- [Pré-requis](#pré-requis)
- [Installation](#installation)
- [Lancer LibreTranslate (serveur de traduction)](#lancer-libretranslate-serveur-de-traduction)
- [Modes d'utilisation](#modes-dutilisation)
  - [Mode automatique (webhook)](#1-mode-automatique-webhook)
  - [Mode manuel (interface CLI)](#2-mode-manuel-interface-cli)
  - [Maintenance du mapping](#3-maintenance-du-mapping)
  - [Exécuter les tests](#4-exécuter-les-tests)
- [Configuration](#configuration)
- [Sécurité](#sécurité)
- [Structure du projet](#structure-du-projet)
- [Auteur](#auteur)

---

## Fonctionnalités

- Traduction automatique des livres, chapitres et pages BookStack
- Synchronisation automatique à chaque mise à jour via webhook
- Interface manuelle pour contrôle ou mise à jour ponctuelle
- Mapping entre contenus source et traduits (stocké localement)
- Outils de nettoyage et de maintenance du mapping
- Compatible avec LibreTranslate (traduction locale)

---

## Pré-requis

Avant de commencer, assurez-vous d’avoir :

- Python 3.9 ou supérieur
- pip installé (`python -m ensurepip`)
- Docker (si vous utilisez LibreTranslate via container)
- Une instance BookStack avec une API key

---

## Installation

1. Clonez le dépôt :
   ```bash
   git clone https://github.com/<votre-utilisateur>/automatisation-traduction-bookstack.git
   cd automatisation-traduction-bookstack
   ```

2. Créez un environnement virtuel (optionnel mais recommandé) :
```bash
python -m venv venv
source venv/bin/activate  # Sous Windows : venv\Scripts\activate 
```

3. Installez les dépendances :
```bash
pip install -r requirements.txt
```

Lancer LibreTranslate (serveur de traduction)
LibreTranslate est utilisé comme moteur de traduction automatique.
```bash
docker run -p 5000:5000 libretranslate/libretranslate
```

Option 2 - Autonome (Linux uniquement)
Voir : https://github.com/LibreTranslate/LibreTranslate

Assurez-vous ensuite que l'URL dans config.py ou .env est bien définie :
```python
LIBRETRANSLATE_URL = "http://127.0.0.1:5000/translate"
```

Modes d'utilisation
1. Mode automatique (webhook)
Ce mode permet de déclencher la traduction dès qu'un contenu est modifié dans BookStack.

Lancez le serveur webhook :
```bash
python webhook_server.py 5050
```


Configurez un webhook dans l’interface BookStack avec cette URL :
```arduino
https://votre-domaine/webhook
En cas de test manuel avec un tunnel pour exposer votre local avec ngrok:
https://url-ngrok/webhook
```
Chaque mise à jour (page, chapitre, livre) sera automatiquement traduite et synchronisée.


2. Mode manuel (interface CLI)
Utilisez ce mode si vous souhaitez contrôler manuellement la traduction d’un contenu :
```bash
python main.py
```

Vous pourrez :

Traduire un livre entier

Mettre à jour une page ou un chapitre spécifique

Synchroniser ponctuellement

3. Maintenance du mapping
Ce script analyse les contenus existants sur BookStack et reconstruit le mapping local pour suivre les correspondances.
```bash
python sync_mapping.py
```

4. Exécuter les tests
Pour lancer tous les tests unitaires :
```bash
python -m unittest discover tests
```

Configuration
Modifiez le fichier config.py pour définir vos paramètres :

URL de BookStack (BOOKSTACK_API_BASE)

Token d'authentification (BOOKSTACK_HEADERS)

URL du traducteur (LIBRETRANSLATE_URL)

Langues cibles (TARGET_LANGS)
```python
BOOKSTACK_API_BASE = "https://votre-instance.bookstack.com/api"
BOOKSTACK_HEADERS = {"Authorization": "Token votre_token"}
TARGET_LANGS = ["en", "de"]
```

| Élément           | Description                                         |
| ----------------- | --------------------------------------------------- |
| `api/`            | Accès aux entités BookStack via API                 |
| `translation/`    | Service de traduction et logique de synchronisation |
| `webhook/`        | Serveur webhook (mode automatique)                  |
| `db/`             | Mapping entre contenus source et traduits           |
| `main.py`         | Menu CLI interactif                                 |
| `sync_mapping.py` | Outil de reconstruction du mapping                  |
| `tests/`          | Tests automatisés                                   |

Auteur
Projet développé et maintenu par Arzgui.