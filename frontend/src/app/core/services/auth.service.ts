// src/app/core/services/auth.service.ts
import { Injectable, PLATFORM_ID, Inject } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { BehaviorSubject, Observable, of, throwError } from 'rxjs';
import { delay, tap } from 'rxjs/operators';
import { User } from '../models/user.model';
import { MOCK_USERS, MOCK_USER_DATA, MOCK_AUTH_INFO, UserData } from './mock-users';
import { NotificationService } from './notification.service';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  currentUser$ = this.currentUserSubject.asObservable();
  
  private userDataSubject = new BehaviorSubject<UserData | null>(null);
  userData$ = this.userDataSubject.asObservable();
  
  private tokenKey = 'auth_token';
  private userKey = 'auth_user';
  private userDataKey = 'user_data';
  private isBrowser: boolean;

  constructor(
    private notificationService: NotificationService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {
    this.isBrowser = isPlatformBrowser(this.platformId);
    if (this.isBrowser) {
      this.loadStoredUser();
    }
  }

  login(email: string, password: string): Observable<User> {
    // Vérification des identifiants
    const storedPassword = MOCK_AUTH_INFO[email];
    
    if (!storedPassword || storedPassword !== password) {
      return throwError(() => new Error('Email ou mot de passe incorrect'));
    }
    
    // Recherche de l'utilisateur
    const user = MOCK_USERS.find(u => u.email === email);
    
    if (!user) {
      return throwError(() => new Error('Utilisateur non trouvé'));
    }
    
    // Utilisateur trouvé, générer un token fictif
    const token = `fakeToken_${user.id}_${Date.now()}`;
    
    // Récupérer les données utilisateur
    const userData = MOCK_USER_DATA[user.id];
    
    // Stocker les informations (seulement dans le navigateur)
    if (this.isBrowser) {
      localStorage.setItem(this.tokenKey, token);
      localStorage.setItem(this.userKey, JSON.stringify(user));
      localStorage.setItem(this.userDataKey, JSON.stringify(userData));
    }
    
    // Mettre à jour les observables
    this.currentUserSubject.next(user);
    this.userDataSubject.next(userData);
    
    // Simuler un délai réseau
    return of(user).pipe(delay(800));
  }

  logout(): Observable<boolean> {
    // Supprimer les données stockées (seulement dans le navigateur)
    if (this.isBrowser) {
      localStorage.removeItem(this.tokenKey);
      localStorage.removeItem(this.userKey);
      localStorage.removeItem(this.userDataKey);
    }
    
    // Mettre à jour les observables
    this.currentUserSubject.next(null);
    this.userDataSubject.next(null);
    
    // Simuler un délai réseau
    return of(true).pipe(delay(500));
  }

  isAuthenticated(): boolean {
    return !!this.getToken() && !!this.currentUserSubject.value;
  }

  getToken(): string | null {
    if (!this.isBrowser) {
      return null;
    }
    return localStorage.getItem(this.tokenKey);
  }

  getCurrentUser(): User | null {
    return this.currentUserSubject.value;
  }

  getUserData(): UserData | null {
    return this.userDataSubject.value;
  }
  updateUserData(userData: UserData): void {
    this.userDataSubject.next(userData);
  }

  getOrchestreIds(): number[] {
    const userData = this.userDataSubject.value;
    return userData?.orchestres || [];
  }

  hasAccessToOrchestre(orchestreId: number): boolean {
    // L'admin (role="admin") a accès à tous les orchestres
    if (this.currentUserSubject.value?.role === 'admin') {
      return true;
    }
    
    // Pour les autres utilisateurs, vérifier la liste des orchestres
    const orchestreIds = this.getOrchestreIds();
    return orchestreIds.includes(orchestreId);
  }

  // Charger l'utilisateur depuis le stockage local
  private loadStoredUser(): void {
    if (!this.isBrowser) {
      return;
    }
    
    const token = this.getToken();
    const storedUser = localStorage.getItem(this.userKey);
    const storedUserData = localStorage.getItem(this.userDataKey);
    
    if (token && storedUser && storedUserData) {
      try {
        const user: User = JSON.parse(storedUser);
        const userData: UserData = JSON.parse(storedUserData);
        
        this.currentUserSubject.next(user);
        this.userDataSubject.next(userData);
      } catch (error) {
        this.notificationService?.error('Erreur de session', 'Impossible de restaurer votre session');
        this.logout().subscribe();
      }
    }
  }
}