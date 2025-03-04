import { Injectable } from '@angular/core';
import { Observable, of, throwError } from 'rxjs';
import { delay, map } from 'rxjs/operators';
import { Orchestre, Instrument, Projet } from '../../orchestre_cards/models';
import { MOCK_ORCHESTRES, MOCK_INSTRUMENTS, MOCK_PROJETS } from './mock-data';
import { AuthService } from './auth.service';
import { NotificationService } from './notification.service';

@Injectable({
  providedIn: 'root'
})
export class OrchestreService {
  private orchestres = MOCK_ORCHESTRES;
  private instruments = MOCK_INSTRUMENTS;
  private projets = MOCK_PROJETS;

  // Simuler un délai réseau pour être plus réaliste
  private delay = 300;

  constructor(
    private authService: AuthService,
    private notificationService: NotificationService
  ) {}

  // ORCHESTRES
  
  getAllOrchestres(): Observable<Orchestre[]> {
    // Vérifier les droits d'accès de l'utilisateur actuel
    const userData = this.authService.getUserData();
    
    if (!userData) {
      return of([]).pipe(delay(this.delay));
    }
    
    // Pour l'admin (Testeur), retourner tous les orchestres
    if (this.authService.getCurrentUser()?.role === 'admin') {
      return of([...this.orchestres]).pipe(delay(this.delay));
    }
    
    // Pour les autres utilisateurs, filtrer selon leurs droits
    const accessibleOrchestreIds = userData.orchestres || [];
    const filteredOrchestres = this.orchestres.filter(orchestre => 
      accessibleOrchestreIds.includes(orchestre.id)
    );
    
    return of(filteredOrchestres).pipe(delay(this.delay));
  }

  getOrchestreById(id: number): Observable<Orchestre> {
    const orchestre = this.orchestres.find(o => o.id === id);
    
    if (!orchestre) {
      return throwError(() => new Error(`Orchestre avec ID ${id} non trouvé`));
    }
    
    // Vérifier les droits d'accès
    if (!this.authService.hasAccessToOrchestre(id)) {
      return throwError(() => new Error('Vous n\'avez pas accès à cet orchestre'));
    }
    
    return of({...orchestre}).pipe(delay(this.delay));
  }

  addOrchestre(orchestre: Omit<Orchestre, 'id'>): Observable<Orchestre> {
    // Génération d'un nouvel ID (simulé)
    const newId = Math.max(...this.orchestres.map(o => o.id), 0) + 1;
    const newOrchestre: Orchestre = { 
      ...orchestre, 
      id: newId,
      dateCreation: new Date()
    };
    
    // Ajouter l'orchestre à la liste globale
    this.orchestres.push(newOrchestre);
    
    // Ajouter l'ID de l'orchestre à la liste des orchestres accessibles par l'utilisateur
    const currentUser = this.authService.getCurrentUser();
    if (currentUser && currentUser.role !== 'admin') {
      const userData = this.authService.getUserData();
      if (userData) {
        userData.orchestres.push(newId);
        
        // Mise à jour du localStorage (pour simuler une mise à jour serveur)
        localStorage.setItem('user_data', JSON.stringify(userData));
        
        // Mettre à jour le BehaviorSubject dans le service d'authentification
        this.authService.updateUserData(userData);
      }
    }
    
    this.notificationService.success(
      'Orchestre créé avec succès', 
      `L'orchestre "${newOrchestre.nom}" a été créé`
    );
    
    return of(newOrchestre).pipe(delay(this.delay));
  }

  updateOrchestre(orchestre: Orchestre): Observable<Orchestre> {
    const index = this.orchestres.findIndex(o => o.id === orchestre.id);
    if (index === -1) {
      return throwError(() => new Error(`Orchestre avec ID ${orchestre.id} non trouvé`));
    }
    
    // Vérifier les droits d'accès
    if (!this.authService.hasAccessToOrchestre(orchestre.id)) {
      return throwError(() => new Error('Vous n\'avez pas accès à cet orchestre'));
    }
    
    this.orchestres[index] = {...orchestre};
    return of(this.orchestres[index]).pipe(delay(this.delay));
  }

  deleteOrchestre(id: number): Observable<void> {
    const index = this.orchestres.findIndex(o => o.id === id);
    if (index === -1) {
      return throwError(() => new Error(`Orchestre avec ID ${id} non trouvé`));
    }
    
    // Vérifier les droits d'accès
    if (!this.authService.hasAccessToOrchestre(id)) {
      return throwError(() => new Error('Vous n\'avez pas accès à cet orchestre'));
    }
    
    // Si ce n'est pas un admin, retirer l'orchestre de la liste des orchestres accessibles
    const currentUser = this.authService.getCurrentUser();
    if (currentUser && currentUser.role !== 'admin') {
      const userData = this.authService.getUserData();
      if (userData) {
        userData.orchestres = userData.orchestres.filter(orchestreId => orchestreId !== id);
        
        // Mise à jour du localStorage
        localStorage.setItem('user_data', JSON.stringify(userData));
        
        // Mettre à jour le BehaviorSubject
        this.authService.updateUserData(userData);
      }
    }
    
    this.orchestres.splice(index, 1);
    return of(undefined).pipe(delay(this.delay));
  }

  // INSTRUMENTS
  
  getAllInstruments(): Observable<Instrument[]> {
    return of([...this.instruments]).pipe(delay(this.delay));
  }
  
  getInstrumentById(id: number): Observable<Instrument> {
    const instrument = this.instruments.find(i => i.id === id);
    if (!instrument) {
      return throwError(() => new Error(`Instrument avec ID ${id} non trouvé`));
    }
    return of({...instrument}).pipe(delay(this.delay));
  }
  
  getInstrumentsForOrchestre(orchestreId: number): Observable<Instrument[]> {
    return this.getOrchestreById(orchestreId).pipe(
      map(orchestre => orchestre.instruments || [])
    );
  }

  addInstrument(instrument: Omit<Instrument, 'id'>): Observable<Instrument> {
    const newId = Math.max(...this.instruments.map(i => i.id), 0) + 1;
    const newInstrument: Instrument = { ...instrument, id: newId };
    
    this.instruments.push(newInstrument);
    return of(newInstrument).pipe(delay(this.delay));
  }
  
  addInstrumentToOrchestre(orchestreId: number, instrumentId: number): Observable<Orchestre> {
    return this.getOrchestreById(orchestreId).pipe(
      map(orchestre => {
        const instrument = this.instruments.find(i => i.id === instrumentId);
        if (!instrument) {
          throw new Error(`Instrument avec ID ${instrumentId} non trouvé`);
        }
        
        // Vérifier si l'instrument est déjà dans l'orchestre
        if (orchestre.instruments.some(i => i.id === instrumentId)) {
          throw new Error(`L'instrument avec ID ${instrumentId} est déjà dans l'orchestre`);
        }
        
        // Ajouter l'instrument à l'orchestre
        orchestre.instruments.push(instrument);
        
        // Mettre à jour l'orchestre
        const index = this.orchestres.findIndex(o => o.id === orchestreId);
        this.orchestres[index] = orchestre;
        
        return orchestre;
      })
    ).pipe(delay(this.delay));
  }

  // PROJETS
  
  getAllProjets(): Observable<Projet[]> {
    return of([...this.projets]).pipe(delay(this.delay));
  }
  
  getProjetById(id: number): Observable<Projet> {
    const projet = this.projets.find(p => p.id === id);
    if (!projet) {
      return throwError(() => new Error(`Projet avec ID ${id} non trouvé`));
    }
    return of({...projet}).pipe(delay(this.delay));
  }
  
  getProjetsForOrchestre(orchestreId: number): Observable<Projet[]> {
    return this.getOrchestreById(orchestreId).pipe(
      map(orchestre => orchestre.projets || [])
    );
  }

  addProjet(projet: Omit<Projet, 'id'>): Observable<Projet> {
    const newId = Math.max(...this.projets.map(p => p.id), 0) + 1;
    const newProjet: Projet = { ...projet, id: newId };
    
    this.projets.push(newProjet);
    return of(newProjet).pipe(delay(this.delay));
  }
  
  addProjetToOrchestre(orchestreId: number, projetId: number): Observable<Orchestre> {
    return this.getOrchestreById(orchestreId).pipe(
      map(orchestre => {
        const projet = this.projets.find(p => p.id === projetId);
        if (!projet) {
          throw new Error(`Projet avec ID ${projetId} non trouvé`);
        }
        
        // S'assurer que projets est initialisé
        if (!orchestre.projets) {
          orchestre.projets = [];
        }
        
        // Vérifier si le projet est déjà dans l'orchestre
        if (orchestre.projets.some(p => p.id === projetId)) {
          throw new Error(`Le projet avec ID ${projetId} est déjà dans l'orchestre`);
        }
        
        // Ajouter le projet à l'orchestre
        orchestre.projets.push(projet);
        
        // Mettre à jour l'orchestre
        const index = this.orchestres.findIndex(o => o.id === orchestreId);
        this.orchestres[index] = orchestre;
        
        return orchestre;
      })
    ).pipe(delay(this.delay));
  }
}