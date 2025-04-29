// src/app/app.routes.ts
import { Routes } from '@angular/router';
import { ConnexionComponent } from './pages/connexion/connexion.component';
import { InscriptionComponent } from './pages/inscription/inscription.component';
import { DashboardComponent } from './pages/dashboard/dashboard.component';
import { authGuard } from './core/gardes/auth.guard';
import { ConversationComponent } from './pages/conversation/conversation.component';

export const routes: Routes = [
  { path: '', redirectTo: 'connexion', pathMatch: 'full' },
  { path: '*', redirectTo: 'connexion', pathMatch: 'full' },
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
    path: 'conversation',
    component: ConversationComponent,
    canActivate: [authGuard]
  },
  {
    path: 'projet',
    loadComponent: () => import('./pages/projet/projet.component').then(m => m.ProjetComponent),
    canActivate: [authGuard]
  },
  {
    path: 'edition-agent/:id',
    loadComponent: () => import('./pages/agent-edition/agent-edition.component').then(m => m.AgentEditionComponent),
    canActivate: [authGuard]
  },
  { path: '**', redirectTo: 'connexion' }
];
