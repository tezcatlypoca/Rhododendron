# 🖥️ Rhododendron - Frontend

Interface utilisateur pour le projet Rhododendron, un système d'agents AI collaboratifs.

## 📋 Prérequis

- Node.js 18+ et npm
- Angular CLI 19.2.7+

## 🛠 Installation

1. Installer les dépendances :
```bash
npm install
```

2. Configurer les variables d'environnement :
```bash
# Vérifier et éditer src/environments/environment.ts pour le développement
# Vérifier et éditer src/environments/environment.prod.ts pour la production
```

## 🚀 Lancement du serveur de développement

```bash
ng serve
```

L'application sera disponible sur :
- `http://localhost:4200/`

L'application se rechargera automatiquement si vous modifiez l'un des fichiers source.

## 🔧 Génération de code

Angular CLI inclut des outils puissants pour générer du code :

```bash
# Générer un composant
ng generate component nom-du-composant

# Générer un service
ng generate service nom-du-service

# Générer une directive
ng generate directive nom-de-la-directive

# Autres schématiques disponibles
ng generate --help
```

## 📦 Compilation pour la production

```bash
ng build
```

Les artefacts de build seront stockés dans le répertoire `dist/`. Le build utilise par défaut la configuration de production.

## 🧪 Exécution des tests unitaires

```bash
ng test
```

Exécute les tests unitaires via [Karma](https://karma-runner.github.io).

## 📊 Structure du projet

```
frontend/
├── src/
│   ├── app/
│   │   ├── composants/         # Composants réutilisables
│   │   │   ├── bouton/
│   │   │   └── champ-formulaire/
│   │   ├── core/               # Fonctionnalités fondamentales
│   │   │   ├── gardes/         # Protections de routes
│   │   │   └── intercepteurs/  # Intercepteurs HTTP
│   │   ├── modeles/            # Interfaces et types
│   │   ├── pages/              # Pages de l'application
│   │   │   ├── connexion/
│   │   │   ├── inscription/
│   │   │   └── profil/
│   │   ├── partage/            # Ressources partagées
│   │   └── services/           # Services
│   ├── environments/           # Configurations d'environnement
│   ├── assets/                 # Ressources statiques
│   └── styles.scss             # Styles globaux
├── angular.json                # Configuration Angular
└── package.json                # Dépendances npm
```

## 🔑 Fonctionnalités principales

- **Authentification complète** : Inscription, connexion et gestion des sessions
- **Gestion de profil utilisateur** : Visualisation et modification des informations
- **Interface responsive** : Adaptée à tous les appareils
- **Composants réutilisables** : Boutons, champs de formulaire, etc.

## 🔒 Sécurité

- Authentification via JWT
- Interception des requêtes HTTP pour ajouter le token
- Protection des routes avec des guards
- Validation des formulaires

## 💡 Bonnes pratiques

- Architecture modulaire et componentisée
- Composants Angular standalone
- Utilisation des formulaires réactifs
- Gestion des erreurs centralisée

## 📱 Compatibilité

- Navigateurs modernes (Chrome, Firefox, Safari, Edge)
- Design responsive pour mobile et desktop

## 🔗 Ressources additionnelles

- [Documentation officielle d'Angular](https://angular.io/docs)
- [Documentation CLI Angular](https://angular.dev/tools/cli)
- [Guide des formulaires réactifs](https://angular.io/guide/reactive-forms)