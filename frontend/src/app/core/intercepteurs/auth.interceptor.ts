// src/app/core/intercepteurs/auth.interceptor.ts
import { HttpHandlerFn, HttpInterceptorFn, HttpRequest, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError } from 'rxjs/operators';
import { throwError } from 'rxjs';
import { AuthService } from '../../services/auth.service';

/**
 * Intercepteur HTTP pour ajouter le token JWT aux requêtes
 * et gérer les erreurs d'authentification
 */
export const authInterceptor: HttpInterceptorFn = (req: HttpRequest<unknown>, next: HttpHandlerFn) => {
  const authService = inject(AuthService);
  const router = inject(Router);
  
  // Ajouter le token JWT à l'en-tête d'autorisation
  const token = authService.obtenirToken();
  
  if (token) {
    req = req.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`
      }
    });
  }

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      // Gérer les erreurs d'authentification (401)
      if (error.status === 401) {
        authService.deconnexion();
        router.navigate(['/connexion']);
      }
      return throwError(() => error);
    })
  );
};