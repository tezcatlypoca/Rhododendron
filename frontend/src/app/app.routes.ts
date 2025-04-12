// src/app/app.routes.ts
import { Routes } from '@angular/router';
import { ConnexionComponent } from './pages/connexion/connexion.component';
import { InscriptionComponent } from './pages/inscription/inscription.component';
import { DashboardComponent } from './pages/dashboard/dashboard.component';
import { authGuard } from './core/gardes/auth.guard';

export const routes: Routes = [
  { path: '', redirectTo: 'connexion', pathMatch: 'full' },
  { path: 'connexion', component: ConnexionComponent },
  { path: 'inscription', component: InscriptionComponent },
  {
    path: 'dashboard',
    component: DashboardComponent,
    canActivate: [authGuard]
  },
  {
    path: 'profil',
    loadComponent: () => import('./pages/profil/profil.component').then(m => m.ProfilComponent),
    canActivate: [authGuard]
  },
  {
    path: 'agents',
    loadComponent: () => import('./pages/agent-gestion/agent-gestion.component').then(m => m.AgentGestionComponent),
    canActivate: [authGuard]
  },
  {
    path: 'conversations/:id',
    loadComponent: () => import('./pages/conversation/conversation.component').then(m => m.ConversationComponent),
    canActivate: [authGuard]
  },
  { path: '**', redirectTo: 'connexion' }
];