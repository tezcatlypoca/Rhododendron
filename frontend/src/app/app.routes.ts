// src/app/app.routes.ts
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
  { 
    path: 'dashboard', 
    loadComponent: () => import('./pages/dashboard/dashboard.component').then(m => m.DashboardComponent),
    canActivate: [authGuard] 
  },
  // Routes pour les futures fonctionnalités
  { 
    path: 'agents', 
    loadComponent: () => import('./pages/dashboard/dashboard.component').then(m => m.DashboardComponent),
    canActivate: [authGuard] 
  },
  { 
    path: 'agents/:id', 
    loadComponent: () => import('./pages/dashboard/dashboard.component').then(m => m.DashboardComponent),
    canActivate: [authGuard] 
  },
  { 
    path: 'statistiques', 
    loadComponent: () => import('./pages/dashboard/dashboard.component').then(m => m.DashboardComponent),
    canActivate: [authGuard] 
  },
  // Redirections par défaut
  { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
  { path: '**', redirectTo: '/dashboard' }
];