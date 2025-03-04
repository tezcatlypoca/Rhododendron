// src/app/app.routes.ts
import { Routes } from '@angular/router';
import { AccueilComponent } from './accueil/accueil.component';
import { OrchestreDetailComponent } from './orchestre-detail/orchestre-detail.component';
import { OrchestreFormComponent } from './orchestre-form/orchestre-form.component';
import { LoginComponent } from './auth/login/login.component';
import { AuthGuard } from './core/guards/auth.guard';

export const routes: Routes = [
  { path: '', component: AccueilComponent },
  { path: 'login', component: LoginComponent },
  { 
    path: 'orchestre/:id', 
    component: OrchestreDetailComponent,
    canActivate: [AuthGuard] 
  },
  { 
    path: 'nouvelle-orchestre', 
    component: OrchestreFormComponent,
    canActivate: [AuthGuard] 
  },
  { 
    path: 'orchestre/:id/configurer', 
    component: OrchestreFormComponent,
    canActivate: [AuthGuard] 
  },
  { path: '**', redirectTo: '' }
];