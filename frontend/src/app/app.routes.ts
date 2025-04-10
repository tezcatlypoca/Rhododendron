import { Routes } from '@angular/router';
import { authGuard } from './core/gardes/auth.guard';

export const routes: Routes = [
  { 
    path: 'connexion', 
    loadComponent: () => import('./pages/connexion/connexion.component').then(m => m.ConnexionComponent) 
  },
  { 
    path: 'inscription', 
    loadComponent: () => import('./pages/inscription/inscription.component').then(m => m.InscriptionComponent) 
  },
  { 
    path: 'profil', 
    loadComponent: () => import('./pages/profil/profil.component').then(m => m.ProfilComponent),
    canActivate: [authGuard] 
  },
  { path: '', redirectTo: '/connexion', pathMatch: 'full' },
  { path: '**', redirectTo: '/connexion' }
];