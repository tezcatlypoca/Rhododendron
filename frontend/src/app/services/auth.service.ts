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
    console.log('Initialisation du service AuthService');
    // Ne pas charger l'utilisateur au démarrage
    // this.chargerUtilisateur();
  }

  /**
   * Inscription d'un nouvel utilisateur
   * @param donnees Données d'inscription
   * @returns Observable avec les informations utilisateur
   */
  inscription(donnees: InscriptionDonnees): Observable<Utilisateur> {
    console.log('Tentative d\'inscription avec les données:', donnees);
    return this.http.post<Utilisateur>(`${this.apiUrl}/auth/register`, donnees).pipe(
      tap(response => console.log('Réponse d\'inscription:', response)),
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
      return false;
    }

    const token = localStorage.getItem('access_token');
    if (!token) {
      return false;
    }

    try {
      // Vérifier si le token est valide avant de tenter de le décoder
      if (this.jwtHelper.isTokenExpired(token)) {
        console.log('Token expiré');
        this.deconnexion();
        return false;
      }

      // Vérifier si le token est un JWT valide
      const parts = token.split('.');
      if (parts.length !== 3) {
        console.log('Token invalide: format incorrect');
        this.deconnexion();
        return false;
      }

      return true;
    } catch (error) {
      console.warn('Erreur lors de la vérification du token:', error);
      this.deconnexion();
      return false;
    }
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
   * Charge l'utilisateur depuis le token
   */
  private chargerUtilisateur(): void {
    if (!isPlatformBrowser(this.platformId)) {
      return;
    }

    const token = localStorage.getItem('access_token');
    if (!token) {
      console.log('Aucun token trouvé dans le localStorage');
      return;
    }

    try {
      // Vérifier si le token est valide avant de tenter de le décoder
      if (this.jwtHelper.isTokenExpired(token)) {
        console.log('Token expiré');
        this.deconnexion();
        return;
      }

      // Décoder le token pour obtenir les informations de base
      const decodedToken = this.jwtHelper.decodeToken(token);
      if (!decodedToken) {
        console.log('Token invalide');
        this.deconnexion();
        return;
      }

      // Créer un utilisateur temporaire avec les informations du token
      const tempUtilisateur: Utilisateur = {
        id: decodedToken.sub || '',
        username: decodedToken.username || '',
        email: decodedToken.email || '',
        roles: decodedToken.roles || [],
        is_active: true,
        created_at: new Date().toISOString()
      };
      this.utilisateurSubject.next(tempUtilisateur);

      // Charger le profil complet
      this.chargerProfilUtilisateur().subscribe();
    } catch (error) {
      console.warn('Erreur lors du chargement de l\'utilisateur:', error);
      this.deconnexion();
    }
  }
}
