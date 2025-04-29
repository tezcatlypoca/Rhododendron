export interface Utilisateur {
  id: string;
  username: string;
  email: string;
  is_active: boolean;
  roles: string[];
  created_at: Date;
  last_login?: Date;
}

export interface UtilisateurCreate {
  username: string;
  email: string;
  password: string;
}

export interface UtilisateurUpdate {
  username?: string;
  email?: string;
  password?: string;
  is_active?: boolean;
  roles?: string[];
} 