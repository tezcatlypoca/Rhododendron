// src/app/services/auth.service.ts
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, of, throwError } from 'rxjs';
import { catchError, map, tap, switchMap } from 'rxjs/operators';
import { JwtHelperService } from '@auth0/angular-jwt';
import { PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { environment } from '../../environments/environment';
import { LoginRequest, Token, AuthResponse, Utilisateur } from '../models/auth.model';

/**
 * Service de gestion de l'authentification
 * Gère les appels API d'authentification et maintient l'état de connexion de l'utilisateur
 */
@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = `${environment.apiUrl}/auth`;
  private jwtHelper = new JwtHelperService();
  private currentUserSubject = new BehaviorSubject<Utilisateur | null>(null);
  private platformId = inject(PLATFORM_ID);

  public utilisateur$ = this.currentUserSubject.asObservable();

  constructor(private http: HttpClient) {
    console.log('Initialisation du service AuthService');
    this.loadStoredUser();
  }

  private loadStoredUser(): void {
    const storedUser = localStorage.getItem('currentUser');
    if (storedUser) {
      this.currentUserSubject.next(JSON.parse(storedUser));
    }
  }

  /**
   * Inscription d'un nouvel utilisateur
   * @param donnees Données d'inscription
   * @returns Observable avec les informations utilisateur
   */
  register(userData: LoginRequest): Observable<AuthResponse> {
    console.log('Tentative d\'inscription avec les données:', userData);
    return this.http.post<AuthResponse>(`${this.apiUrl}/register`, userData).pipe(
      tap(response => {
        console.log('Réponse d\'inscription:', response);
        localStorage.setItem('token', response.token.access_token);
        localStorage.setItem('currentUser', JSON.stringify(response.user));
        this.currentUserSubject.next(response.user);
      }),
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
  login(credentials: LoginRequest): Observable<AuthResponse> {
    console.log('Tentative de connexion avec les données:', credentials);
    return this.http.post<AuthResponse>(`${this.apiUrl}/login`, credentials).pipe(
      tap(response => {
        console.log('Réponse de connexion:', response);
        localStorage.setItem('token', response.token.access_token);
        localStorage.setItem('currentUser', JSON.stringify(response.user));
        this.currentUserSubject.next(response.user);
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
    localStorage.removeItem('token');
    localStorage.removeItem('currentUser');
    this.currentUserSubject.next(null);
  }

  /**
   * Récupère les informations de l'utilisateur connecté
   * @returns Observable avec les informations utilisateur
   */
  getCurrentUser(): Observable<Utilisateur> {
    return this.http.get<Utilisateur>(`${this.apiUrl}/me`).pipe(
      tap(utilisateur => {
        this.currentUserSubject.next(utilisateur);
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
    return !!localStorage.getItem('token');
  }

  /**
   * Récupère le token JWT
   * @returns Le token JWT ou null
   */
  obtenirToken(): string | null {
    return localStorage.getItem('token');
  }

  /**
   * Charge l'utilisateur depuis le token
   */
  chargerProfilUtilisateur(): Observable<Utilisateur> {
    return this.getCurrentUser();
  }
}
