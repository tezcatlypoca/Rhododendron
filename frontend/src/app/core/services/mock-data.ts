import { Orchestre, Instrument, Projet, Capacite } from '../../orchestre_cards/models';

// Données fictives pour les projets
export const MOCK_PROJETS: Projet[] = [
  {
    id: 1,
    nom: "Site E-commerce",
    type: "Web",
    description: "Plateforme de vente en ligne multi-vendeurs"
  },
  {
    id: 2,
    nom: "Application CRM",
    type: "Web",
    description: "Gestion de la relation client pour PME"
  },
  {
    id: 3,
    nom: "Application Fitness",
    type: "Mobile",
    description: "App de suivi d'entrainement pour Android et iOS"
  },
  {
    id: 4,
    nom: "Campagne Réseaux Sociaux",
    type: "Marketing",
    description: "Stratégie cross-platform pour lancement produit"
  },
  {
    id: 5,
    nom: "Blog Content",
    type: "Contenu",
    description: "Production de contenu SEO pour site corporate"
  },
  {
    id: 6,
    nom: "Analyse Prédictive Ventes",
    type: "Data Science",
    description: "Modèle prédictif pour optimisation des stocks"
  }
];

// Données fictives pour les instruments
export const MOCK_INSTRUMENTS: Instrument[] = [
  {
    id: 1,
    nom: "Frontend Maestro",
    role: "Développeur",
    specificites: ["Angular", "React", "CSS avancé"],
    capacites: [
      { nom: "Angular", niveau: 5 },
      { nom: "React", niveau: 4 },
      { nom: "CSS", niveau: 5 }
    ],
    projetsIds: [1, 2]
  },
  {
    id: 2,
    nom: "Backend Virtuose",
    role: "Développeur",
    specificites: ["Node.js", "Python", "Bases de données"],
    capacites: [
      { nom: "Node.js", niveau: 5 },
      { nom: "MongoDB", niveau: 4 },
      { nom: "API REST", niveau: 5 }
    ],
    projetsIds: [1]
  },
  {
    id: 3,
    nom: "Quality Assurance",
    role: "Testeur",
    specificites: ["Tests unitaires", "Tests d'intégration", "Automatisation"],
    capacites: [
      { nom: "Jest", niveau: 4 },
      { nom: "Cypress", niveau: 5 },
      { nom: "Jenkins", niveau: 3 }
    ],
    projetsIds: [1, 2]
  },
  {
    id: 4,
    nom: "Tech Lead Symphony",
    role: "Manager",
    specificites: ["Gestion de projet", "Architecture", "Code review"],
    capacites: [
      { nom: "Architecture", niveau: 5 },
      { nom: "CI/CD", niveau: 4 },
      { nom: "Code Quality", niveau: 5 }
    ],
    projetsIds: [1, 2]
  },
  {
    id: 5,
    nom: "Android Developer",
    role: "Développeur",
    specificites: ["Java", "Kotlin", "Flutter"],
    capacites: [
      { nom: "Flutter", niveau: 5 },
      { nom: "Firebase", niveau: 4 },
      { nom: "UI/UX Mobile", niveau: 4 }
    ],
    projetsIds: [3]
  },
  {
    id: 6,
    nom: "iOS Specialist",
    role: "Développeur",
    specificites: ["Swift", "SwiftUI", "XCode"],
    capacites: [
      { nom: "Swift", niveau: 5 },
      { nom: "Core Data", niveau: 4 },
      { nom: "Apple Health", niveau: 5 }
    ],
    projetsIds: [3]
  },
  {
    id: 7,
    nom: "Mobile UX Designer",
    role: "Designer",
    specificites: ["Wireframes", "Prototypage", "Material Design"],
    capacites: [
      { nom: "Figma", niveau: 5 },
      { nom: "Material Design", niveau: 5 },
      { nom: "Animation", niveau: 4 }
    ],
    projetsIds: [3]
  },
  {
    id: 8,
    nom: "Content Composer",
    role: "Rédacteur",
    specificites: ["Copywriting", "SEO", "Storytelling"],
    capacites: [
      { nom: "SEO", niveau: 5 },
      { nom: "Blog", niveau: 4 },
      { nom: "Copywriting", niveau: 5 }
    ],
    projetsIds: [5]
  },
  {
    id: 9,
    nom: "Social Media Soloist",
    role: "Community Manager",
    specificites: ["Stratégie", "Analytics", "Engagement"],
    capacites: [
      { nom: "Facebook Ads", niveau: 5 },
      { nom: "Instagram", niveau: 5 },
      { nom: "TikTok", niveau: 4 }
    ],
    projetsIds: [4]
  },
  {
    id: 10,
    nom: "Visual Director",
    role: "Designer",
    specificites: ["Identité visuelle", "UX/UI", "Infographies"],
    capacites: [
      { nom: "Adobe Suite", niveau: 5 },
      { nom: "Motion Design", niveau: 4 },
      { nom: "Brand Identity", niveau: 5 }
    ],
    projetsIds: [4, 5]
  },
  {
    id: 11,
    nom: "Data Miner",
    role: "Analyste",
    specificites: ["Extraction", "Nettoyage", "Préparation"],
    capacites: [
      { nom: "SQL", niveau: 5 },
      { nom: "ETL", niveau: 4 },
      { nom: "Data Cleaning", niveau: 5 }
    ],
    projetsIds: [6]
  },
  {
    id: 12,
    nom: "ML Engineer",
    role: "Ingénieur IA",
    specificites: ["Algorithmes ML", "Deep Learning", "Validation"],
    capacites: [
      { nom: "Python", niveau: 5 },
      { nom: "TensorFlow", niveau: 4 },
      { nom: "Scikit-learn", niveau: 5 }
    ],
    projetsIds: [6]
  },
  {
    id: 13,
    nom: "Visualization Expert",
    role: "Data Visualizer",
    specificites: ["Dashboards", "Storytelling", "Insights"],
    capacites: [
      { nom: "Tableau", niveau: 5 },
      { nom: "D3.js", niveau: 4 },
      { nom: "Power BI", niveau: 4 }
    ],
    projetsIds: [6]
  }
];

// Création des orchestres avec les instruments et projets référencés
export const MOCK_ORCHESTRES: Orchestre[] = [
  {
    id: 1,
    nom: "Orchestre Développement Web",
    specialite: "Développement",
    dateCreation: new Date(2023, 9, 15),
    projets: [MOCK_PROJETS[0], MOCK_PROJETS[1]],
    instruments: [MOCK_INSTRUMENTS[0], MOCK_INSTRUMENTS[1], MOCK_INSTRUMENTS[2], MOCK_INSTRUMENTS[3]]
  },
  {
    id: 2,
    nom: "Orchestre Mobile Apps",
    specialite: "Développement",
    dateCreation: new Date(2024, 0, 5),
    projets: [MOCK_PROJETS[2]],
    instruments: [MOCK_INSTRUMENTS[4], MOCK_INSTRUMENTS[5], MOCK_INSTRUMENTS[6]]
  },
  {
    id: 3,
    nom: "Orchestre Marketing Digital",
    specialite: "Communication",
    dateCreation: new Date(2023, 11, 3),
    projets: [MOCK_PROJETS[3], MOCK_PROJETS[4]],
    instruments: [MOCK_INSTRUMENTS[7], MOCK_INSTRUMENTS[8], MOCK_INSTRUMENTS[9]]
  },
  {
    id: 4,
    nom: "Orchestre Data Science",
    specialite: "Analyse",
    dateCreation: new Date(2024, 0, 20),
    projets: [MOCK_PROJETS[5]],
    instruments: [MOCK_INSTRUMENTS[10], MOCK_INSTRUMENTS[11], MOCK_INSTRUMENTS[12]]
  }
];