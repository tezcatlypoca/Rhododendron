# 📁 Structure des dossiers de Crew AI Locale

```plaintext
CrewAI-Locale/
│── backend/                # Backend en Python (FastAPI, CrewAI, LangChain)
│   ├── app/
│   │   ├── api/            # Routes FastAPI
│   │   ├── models/         # Définitions des modèles de données
│   │   ├── services/       # Logique métier (agents AI, orchestration)
│   │   ├── core/           # Configuration et utils
│   │   ├── main.py         # Point d'entrée FastAPI
│   ├── agents/             # Code spécifique aux agents AI
│   ├── requirements.txt    # Dépendances Python
│   ├── Dockerfile          # Conteneurisation du backend
│   ├── tests/              # Tests unitaires pour le backend
│
│── frontend/               # Frontend en Angular
│   ├── src/
│   │   ├── app/            # Composants Angular
│   │   ├── assets/         # Images, styles, etc.
│   │   ├── environments/   # Configurations env
│   │   ├── main.ts         # Entrée Angular
│   ├── angular.json        # Configuration Angular
│   ├── package.json        # Dépendances JS
│   ├── tsconfig.json       # Configuration TypeScript
│   ├── tests/              # Tests unitaires pour le frontend
│
│── deployment/             # Fichiers pour le déploiement (Docker, scripts)
│── docs/                   # Documentation
│── .gitignore              # Fichiers à ignorer par Git
│── README.md               # Présentation du projet
