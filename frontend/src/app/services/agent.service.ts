// src/app/services/agent.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';
import { environment } from '../../environments/environment';
import { Agent, AgentCreate, AgentUpdate } from '../models/agent.model';
import { StateService } from './state.service';

@Injectable({
  providedIn: 'root'
})
export class AgentService {
  private apiUrl = `${environment.apiUrl}/agents`;

  constructor(
    private http: HttpClient,
    private stateService: StateService
  ) {}

  /**
   * Récupère la liste de tous les agents
   */
  getAllAgents(): Observable<Agent[]> {
    return this.http.get<Agent[]>(this.apiUrl).pipe(
      tap(agents => {
        this.stateService.updateAgents(agents);
      }),
      catchError(error => {
        console.error('Erreur lors de la récupération des agents:', error);
        return throwError(() => new Error('Erreur lors de la récupération des agents'));
      })
    );
  }

  /**
   * Récupère un agent spécifique par son ID
   */
  getAgentById(id: string): Observable<Agent> {
    return this.http.get<Agent>(`${this.apiUrl}/${id}`).pipe(
      catchError(error => {
        console.error(`Erreur lors de la récupération de l'agent ${id}:`, error);
        return throwError(() => new Error(`Erreur lors de la récupération de l'agent`));
      })
    );
  }

  /**
   * Crée un nouvel agent
   */
  createAgent(agent: AgentCreate): Observable<Agent> {
    return this.http.post<Agent>(this.apiUrl, agent).pipe(
      tap(newAgent => {
        this.stateService.addAgent(newAgent);
      }),
      catchError(error => {
        console.error('Erreur lors de la création de l\'agent:', error);
        return throwError(() => new Error('Erreur lors de la création de l\'agent'));
      })
    );
  }

  /**
   * Met à jour un agent existant
   */
  updateAgent(id: string, agent: AgentUpdate): Observable<Agent> {
    return this.http.put<Agent>(`${this.apiUrl}/${id}`, agent).pipe(
      tap(updatedAgent => {
        this.stateService.updateAgent(updatedAgent);
      }),
      catchError(error => {
        console.error('Erreur lors de la mise à jour de l\'agent:', error);
        return throwError(() => new Error('Erreur lors de la mise à jour de l\'agent'));
      })
    );
  }

  /**
   * Supprime un agent existant
   */
  deleteAgent(id: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${id}`).pipe(
      tap(() => {
        // Mettre à jour la liste des agents après suppression
        this.getAllAgents().subscribe();
      }),
      catchError(error => {
        console.error('Erreur lors de la suppression de l\'agent:', error);
        return throwError(() => new Error('Erreur lors de la suppression de l\'agent'));
      })
    );
  }
}