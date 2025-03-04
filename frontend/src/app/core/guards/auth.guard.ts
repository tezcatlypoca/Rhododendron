// src/app/core/guards/auth.guard.ts
import { Injectable } from '@angular/core';
import { Router, CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { NotificationService } from '../services/notification.service';

@Injectable({ providedIn: 'root' })
export class AuthGuard implements CanActivate {
  constructor(
    private router: Router,
    private authService: AuthService,
    private notificationService: NotificationService
  ) {}

  canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot) {
    if (this.authService.isAuthenticated()) {
      // Vérifier si l'accès à l'orchestre est autorisé (si applicable)
      const orchestreId = route.params['id'];
      if (orchestreId && !this.authService.hasAccessToOrchestre(Number(orchestreId))) {
        this.notificationService.error(
          'Accès refusé', 
          'Vous n\'avez pas accès à cet orchestre'
        );
        this.router.navigate(['/']);
        return false;
      }
      
      // Authentifié et autorisé
      return true;
    }

    // Non authentifié, rediriger vers la page de connexion
    this.notificationService.warning(
      'Authentification requise',
      'Veuillez vous connecter pour accéder à cette page'
    );
    this.router.navigate(['/login'], { queryParams: { returnUrl: state.url }});
    return false;
  }
}