# Système de Vectorisation pour Applications Flutter et Android

## Description
Ce module permet d'indexer et de rechercher sémantiquement dans votre code source Flutter et Android. Il transforme les fichiers de code en vecteurs d'embedding et permet des recherches basées sur la similarité sémantique plutôt que sur la simple correspondance de mots-clés.

## Fonctionnalités principales
- Indexation automatique de fichiers de code source (.dart, .java, .kt, etc.)
- Conversion de documents texte en représentations vectorielles
- Recherche sémantique dans le code source
- Support pour différents types de fichiers (code, configuration, documentation)
- Exclusion automatique des dossiers système (.git, node_modules, etc.)

## Installation
1. Assurez-vous que Python 3.8+ est installé
2. Créez un environnement virtuel: `python -m venv rhodoenv`
3. Activez l'environnement: 
   - Windows: `rhodoenv\Scripts\activate`
   - Linux/Mac: `source rhodoenv/bin/activate`
4. Installez les dépendances: 
   ```
   pip install langchain langchain_community langchain_huggingface langchain_chroma
   pip install sentence-transformers chromadb numpy pyyaml chardet
   ```

## Configuration
Créez un fichier `config.yaml` à la racine du projet:
```yaml
app:
  name: "Crew AI Locale"
  debug: true
database:
  type: "sqlite"
paths:
  vector_db: "D:/Coding/AppWindows/Rhododendron/src/data/vectordb"
  projets: "D:/Coding/AppWindows/Rhododendron/src/data/projets"
  documentation: "D:/Coding/AppWindows/Rhododendron/src/data/documentation"
```

## Utilisation
Depuis la racine du projet:

### Création/mise à jour de la base vectorielle
```
python src/vectorisation.py update
```

### Chargement de la base existante
```
python src/vectorisation.py load
```

### Recherche sémantique
```
python src/vectorisation.py search
```

## Structure des fichiers
- `vectorisation.py`: Module principal de vectorisation
- `settings.py`: Configuration et chemins
- `config.yaml`: Paramètres configurables du système

## Exemples de recherche
Le système permet de rechercher des concepts comme:
- "Comment implémenter l'authentification Firebase dans Flutter"
- "Architecture de l'application Flutter"
- "Gestion des erreurs réseau dans l'application"

## Performances
- Vectorisation d'environ 518 chunks en ~28 secondes
- Recherche quasi-instantanée une fois la base créée
- Taille moyenne des chunks: ~928 caractères

## Dépendances principales
- sentence-transformers/all-MiniLM-L6-v2 (modèle d'embedding)
- langchain (framework pour applications IA)
- chromadb (base de données vectorielle)

## Notes techniques
- La base est stockée au format SQLite (chroma.sqlite3)
- Le découpage des documents utilise un chevauchement de 200 caractères
- Les fichiers sont automatiquement détectés avec l'encodage approprié

## Dépannage
- Si la base n'est pas trouvée, vérifiez les chemins dans config.yaml
- Exécutez les commandes depuis la racine du projet
- Pour recréer entièrement la base: `python src/vectorisation.py update --recreate`
