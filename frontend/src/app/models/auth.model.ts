export interface Utilisateur {
  id: string;
  username: string;
  email: string;
  roles: string[];
  is_active: boolean;
  created_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface TokenData {
  email?: string;
}

export interface AuthResponse {
  user: Utilisateur;
  token: Token;
} 