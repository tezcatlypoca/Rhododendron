export interface Projet {
  id: string;
  nom: string;
  description?: string;
  date_creation: Date;
  date_modification: Date;
  compte_id: string;
}

export interface ProjetCreate {
  nom: string;
  description?: string;
}

export interface ProjetUpdate {
  nom?: string;
  description?: string;
} 