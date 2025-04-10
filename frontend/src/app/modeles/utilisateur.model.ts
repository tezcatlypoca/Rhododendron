// src/app/modeles/utilisateur.model.ts
export interface Utilisateur {
    id: string;
    username: string;
    email: string;
    roles: string[];
    is_active: boolean;
    created_at: string;
    last_login?: string;
  }
  
  // src/app/modeles/auth.model.ts
  export interface InscriptionDonnees {
    username: string;
    email: string;
    password: string;
  }
  
  export interface ConnexionDonnees {
    username: string;
    password: string;
  }
  
  export interface TokenReponse {
    access_token: string;
  }