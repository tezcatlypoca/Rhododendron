// src/app/core/services/mock-users.ts
import { User } from '../models/user.model';

// Interface pour stocker les données utilisateur
export interface UserData {
  orchestres: number[]; // IDs des orchestres associés à cet utilisateur
  settings?: {
    theme?: string;
    language?: string;
    notifications?: boolean;
  };
}

// Utilisateurs fictifs pour le développement
export const MOCK_USERS: User[] = [
  {
    id: 1,
    username: 'testeur',
    email: 'testeur@example.com',
    role: 'admin',
    firstName: 'Test',
    lastName: 'Utilisateur',
    profilePicture: 'assets/avatars/testeur.jpg'
  },
  {
    id: 2,
    username: 'kinder',
    email: 'vcoutry@gmail.com',
    role: 'user',
    firstName: 'Valentin',
    lastName: 'Keamder',
    profilePicture: 'assets/avatars/val.jpg'
  },
  {
    id: 3,
    username: 'Samsan',
    email: 'user2@example.com',
    role: 'user',
    firstName: 'Samuel',
    lastName: 'Vaubon',
    profilePicture: 'assets/avatars/sam.jpg'
  },
  {
    id: 4,
    username: 'Tata',
    email: 'user3@example.com',
    role: 'user',
    firstName: 'Yoann',
    lastName: 'Tata',
    profilePicture: 'assets/avatars/yo.jpg'
  }
];

// Données associées à chaque utilisateur
// src/app/core/services/mock-users.ts
// Partie mise à jour
export const MOCK_USER_DATA: { [userId: number]: UserData } = {
    1: {
      orchestres: [1, 2, 3, 4], // Testeur a accès à tous les orchestres
      settings: {
        theme: 'dark',
        language: 'fr',
        notifications: true
      }
    },
    2: {
      orchestres: [], 
      settings: {
        theme: 'light',
        language: 'fr',
        notifications: false
      }
    },
    3: {
      orchestres: [], 
      settings: {
        theme: 'light',
        language: 'en',
        notifications: true
      }
    },
    4: {
      orchestres: [], 
      settings: {
        theme: 'light',
        language: 'fr',
        notifications: true
      }
    }
  };

// Informations d'authentification (normalement stockées de manière sécurisée côté serveur)
export const MOCK_AUTH_INFO: { [email: string]: string } = {
    'testeur@example.com': 'password123',
    'vcoutry@gmail.com': 'password123',   // Mis à jour pour l'utilisateur 'kinder'
    'user2@example.com': 'password123',    // Correspond à 'Samsan'
    'user3@example.com': 'password123'     // Correspond à 'Tata'
  };