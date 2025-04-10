// src/app/services/auth.service.ts
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, of, throwError } from 'rxjs';
import { catchError, map, tap, switchMap } from 'rxjs/operators';
import { JwtHelperService } from '@auth0/angular-jwt';
import { PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';

import { Utilisateur, InscriptionDonnees, ConnexionDonnees, TokenReponse } from '../modeles/auth.model';
import { environment } from '../../environments/environment';

/**
 * Service de gestion de l'authentification
 * Gère les appels API d'authentification et maintient l'état de connexion de l'utilisateur
 */
@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = environment.apiUrl;
  private jwtHelper = new JwtHelperService();
  private utilisateurSubject = new BehaviorSubject<Utilisateur | null>(null);
  private platformId = inject(PLATFORM_ID);
  
  utilisateur$ = this.utilisateurSubject.asObservable();

  constructor(private http: HttpClient) {
    this.chargerUtilisateur();
  }

  /**
   * Inscription d'un nouvel utilisateur
   * @param donnees Données d'inscription
   * @returns Observable avec les informations utilisateur
   */
  inscription(donnees: InscriptionDonnees): Observable<Utilisateur> {
    return this.http.post<Utilisateur>(`${this.apiUrl}/auth/register`, donnees).pipe(
      catchError(error => {
        console.error('Erreur d\'inscription:', error);
        return throwError(() => new Error(error.error?.detail || 'Erreur lors de l\'inscription'));
      })
    );
  }

  /**
   * Connexion d'un utilisateur
   * @param donnees Données de connexion
   * @returns Observable avec la réponse de token
   */
  connexion(donnees: ConnexionDonnees): Observable<TokenReponse> {
    // Conversion des données pour respecter le format OAuth2 attendu par le backend
    const formData = new FormData();
    formData.append('username', donnees.username);
    formData.append('password', donnees.password);

    return this.http.post<TokenReponse>(`${this.apiUrl}/auth/login`, formData).pipe(
      tap(reponse => {
        if (isPlatformBrowser(this.platformId)) {
          localStorage.setItem('access_token', reponse.access_token);
          
          // Créer un utilisateur temporaire pour mise à jour immédiate
          try {
            const decodedToken = this.jwtHelper.decodeToken(reponse.access_token);
            const tempUtilisateur: Utilisateur = {
              id: decodedToken.sub || '',
              username: decodedToken.username || donnees.username,
              email: decodedToken.email || '',
              roles: decodedToken.roles || [],
              is_active: true,
              created_at: new Date().toISOString()
            };
            // Mettre à jour immédiatement l'état
            this.utilisateurSubject.next(tempUtilisateur);
          } catch (e) {
            console.warn('Impossible de décoder le token pour mise à jour rapide');
          }
        }
        // Charger le profil complet
        this.chargerProfilUtilisateur().subscribe();
      }),
      catchError(error => {
        console.error('Erreur de connexion:', error);
        return throwError(() => new Error(error.error?.detail || 'Email ou mot de passe incorrect'));
      })
    );
  }

  /**
   * Déconnexion de l'utilisateur
   */
  deconnexion(): void {
    if (isPlatformBrowser(this.platformId)) {
      localStorage.removeItem('access_token');
    }
    this.utilisateurSubject.next(null);
  }

  /**
   * Récupère les informations de l'utilisateur connecté
   * @returns Observable avec les informations utilisateur
   */
  chargerProfilUtilisateur(): Observable<Utilisateur> {
    return this.http.get<Utilisateur>(`${this.apiUrl}/auth/me`).pipe(
      tap(utilisateur => {
        this.utilisateurSubject.next(utilisateur);
      }),
      catchError(error => {
        console.error('Erreur lors du chargement du profil:', error);
        this.deconnexion();
        return throwError(() => new Error('Session expirée ou invalide'));
      })
    );
  }

  /**
   * Vérifie si l'utilisateur est connecté
   * @returns true si l'utilisateur est connecté
   */
  estConnecte(): boolean {
    if (!isPlatformBrowser(this.platformId)) {
      return false; // Toujours retourner false côté serveur
    }
    
    const token = localStorage.getItem('access_token');
    return !!token && !this.jwtHelper.isTokenExpired(token);
  }

  /**
   * Récupère le token JWT
   * @returns Le token JWT ou null
   */
  obtenirToken(): string | null {
    if (!isPlatformBrowser(this.platformId)) {
      return null; // Toujours retourner null côté serveur
    }
    
    return localStorage.getItem('access_token');
  }

  /**
   * Charge l'utilisateur depuis le token au démarrage
   */
  private chargerUtilisateur(): void {
    if (this.estConnecte()) {
      this.chargerProfilUtilisateur().subscribe();
    }
  }
}