// Définition des interfaces réutilisables
export interface Projet {
  id: number;
  nom: string;
  type: string;
  description: string;
}

export interface Capacite {
  nom: string;
  niveau: number; // 1-5
}

export interface Instrument {
  id: number;
  nom: string;
  role: string;
  specificites: string[];
  capacites?: Capacite[];
  projetsIds?: number[]; // Références aux IDs des projets
}

export interface Orchestre {
  id: number;
  nom: string;
  specialite: string;
  instruments: Instrument[];
  dateCreation: Date;
  projets?: Projet[];
}
