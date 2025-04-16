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

# Interface LLM avec DirectML pour GPU AMD

Ce projet permet d'exécuter des modèles LLM au format GGUF sur des GPU AMD (comme les Radeon Vega 64 et RX 6600) en utilisant DirectML via llama.cpp.

## Prérequis

- Windows 10/11
- GPU AMD avec pilotes récents
- Python 3.8+
- CMake 3.15+
- Visual Studio 2019 ou 2022 avec les outils de développement C++
- DirectML SDK

## Installation

1. **Installer les dépendances système** :
   ```bash
   # Installer Visual Studio avec les outils C++
   # Installer CMake
   # Installer les derniers pilotes AMD
   ```

2. **Installer DirectML SDK** :
   - Télécharger depuis : https://github.com/microsoft/DirectML
   - Suivre les instructions d'installation

3. **Compiler llama.cpp avec DirectML** :
   ```bash
   git clone https://github.com/ggerganov/llama.cpp
   cd llama.cpp
   mkdir build
   cd build
   cmake .. -DLLAMA_DML=ON -DCMAKE_BUILD_TYPE=Release
   cmake --build . --config Release
   ```

4. **Installer les dépendances Python** :
   ```bash
   pip install llama-cpp-python[dml]
   ```

## Configuration

1. **Variables d'environnement** :
   ```bash
   set LLAMA_DML=1
   set DML_DEBUG_LAYER=0
   ```

2. **Paramètres GPU** :
   - Ajuster `n_gpu_layers` selon votre mémoire GPU
   - Pour Vega 64 (8GB) : ~40 couches
   - Pour RX 6600 (8GB) : ~40 couches

## Utilisation

```python
from services.llm_interface import LLMInterface

# Initialiser l'interface
llm = LLMInterface()

# Charger le modèle (optionnel si le chemin par défaut est utilisé)
llm.load_model("chemin/vers/votre/modele.gguf")

# Générer une réponse
response = llm.generate_response(
    prompt="Votre question ici",
    context={"role": "assistant"},
    temperature=0.7,
    max_tokens=1000
)
```

## Paramètres d'inférence

- `temperature` (0.0-1.0) : Contrôle la créativité
- `top_p` (0.0-1.0) : Filtrage par probabilité cumulative
- `max_tokens` : Nombre maximum de tokens à générer
- `stop` : Séquence d'arrêt
- `repeat_penalty` : Pénalité pour la répétition

## Optimisation des performances

1. **Mémoire GPU** :
   - Ajuster `n_gpu_layers` selon votre mémoire disponible
   - Utiliser `use_mlock=True` pour verrouiller la mémoire
   - Activer `use_mmap=True` pour le mapping mémoire

2. **CPU** :
   - Ajuster `n_threads` selon votre CPU
   - Valeur recommandée : nombre de cœurs physiques

3. **Contexte** :
   - Ajuster `n_ctx` selon vos besoins
   - Valeur par défaut : 4096 tokens

## Dépannage

1. **Erreur de chargement DirectML** :
   - Vérifier l'installation de DirectML SDK
   - Mettre à jour les pilotes AMD
   - Redémarrer l'ordinateur

2. **Problèmes de mémoire** :
   - Réduire `n_gpu_layers`
   - Utiliser un modèle plus petit
   - Fermer les applications gourmandes en GPU

3. **Performances lentes** :
   - Vérifier l'utilisation GPU
   - Ajuster les paramètres d'inférence
   - Mettre à jour les pilotes

## Exemple complet

```python
from services.llm_interface import LLMInterface
import logging

# Configurer le logging
logging.basicConfig(level=logging.INFO)

# Initialiser et configurer
llm = LLMInterface()
llm.load_model()  # Utilise le chemin par défaut

# Exemple de conversation
context = {
    "role": "assistant",
    "name": "Code Assistant"
}

history = [
    {"role": "user", "content": "Bonjour, peux-tu m'aider avec du code Python ?"},
    {"role": "assistant", "content": "Bien sûr ! Je suis là pour vous aider avec le code Python. Quelle est votre question ?"}
]

# Générer une réponse
response = llm.generate_response(
    prompt="Comment créer une classe en Python ?",
    context=context,
    conversation_history=history,
    temperature=0.7,
    max_tokens=500
)

print(response)
```

## Notes

- Le modèle doit être au format GGUF
- DirectML est optimisé pour Windows
- Les performances peuvent varier selon le GPU
- Consulter la documentation de llama.cpp pour plus d'options 