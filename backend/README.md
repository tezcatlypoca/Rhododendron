# 🚀 API Rhododendron - Backend

API d'authentification pour le projet Rhododendron, un système d'agents AI collaboratifs.

## 📋 Prérequis

- Python 3.8+
- pip (gestionnaire de paquets Python)

## 🛠 Installation

1. Créer un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows : venv\Scripts\activate
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

3. Configurer les variables d'environnement :
```bash
cp .env.example .env
# Éditer le fichier .env avec vos configurations
```

## 🚀 Lancement de l'API

```bash
uvicorn src.main:app --reload
```

L'API sera disponible sur :
- API : `http://localhost:8000`
- Documentation : `http://localhost:8000/doc`

## 📚 Documentation de l'API

### Routes d'Authentification

#### 1. Inscription (`POST /auth/register`)
```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

#### 2. Connexion (`POST /auth/login`)
```json
{
  "username": "string",
  "password": "string"
}
```

#### 3. Informations utilisateur (`GET /auth/me`)
- Requiert un token JWT dans le header :
```
Authorization: Bearer <token>
```

## 🔐 Sécurité

- Authentification via JWT
- Tokens valides pendant 30 minutes
- Mots de passe hachés avec bcrypt
- Validation des données d'entrée

## 🗄 Base de données

- SQLite pour le développement
- Fichier : `users.db`
- Création automatique au premier appel

## 🛠 Structure du projet

```
backend/
├── src/
│   ├── api/
│   │   ├── routes/
│   │   │   └── auth.py
│   │   └── dependencies.py
│   ├── core/
│   │   └── config.py
│   ├── models/
│   │   ├── domain/
│   │   │   └── user.py
│   │   └── schemas/
│   │       └── auth.py
│   ├── repositories/
│   │   └── user_repository.py
│   ├── services/
│   │   └── auth_service.py
│   └── main.py
├── requirements.txt
└── .env
```

## 🔍 Points importants

- Les emails doivent être valides
- Les mots de passe doivent faire au moins 8 caractères
- Les noms d'utilisateur doivent faire entre 3 et 50 caractères
- CORS est configuré pour accepter toutes les origines (à modifier en production)

## 🐛 Débogage

En cas d'erreur :
1. Vérifier que la base de données est accessible
2. Vérifier les variables d'environnement
3. Consulter les logs de l'API

## 📝 TODO

- [ ] Ajouter des tests unitaires
- [ ] Implémenter une base de données plus robuste
- [ ] Ajouter des validations supplémentaires
- [ ] Améliorer la gestion des erreurs 