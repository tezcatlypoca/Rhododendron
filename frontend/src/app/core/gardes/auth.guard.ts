// src/app/core/gardes/auth.guard.ts
import { inject } from '@angular/core';
import { Router, CanActivateFn } from '@angular/router';
import { AuthService } from '../../services/auth.service';

/**
 * Garde d'authentification
 * Protège les routes qui nécessitent une authentification
 */
export const authGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);
  
  if (authService.estConnecte()) {
    return true;
  }
  
  // Redirection vers la page de connexion
  return router.createUrlTree(['/connexion']);
};