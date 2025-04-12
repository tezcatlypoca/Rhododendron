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

  // console.log('Vérification de l\'authentification...');
  const estConnecte = authService.estConnecte();
  // console.log('Utilisateur connecté:', estConnecte);

  if (estConnecte) {
    return true;
  }

  console.log('Redirection vers la page de connexion...');
  // Redirection vers la page de connexion
  return router.createUrlTree(['/connexion']);
};
