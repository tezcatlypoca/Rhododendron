// src/app/services/agent.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { Agent, AgentCreateDTO, AgentUpdateDTO, AgentResponse } from '../modeles/agent.model';

@Injectable({
  providedIn: 'root'
})
export class AgentService {
  private apiUrl = `${environment.apiUrl}/agents`;

  constructor(private http: HttpClient) {}

  /**
   * Récupère la liste de tous les agents
   */
  getAllAgents(): Observable<Agent[]> {
    return this.http.get<Agent[]>(this.apiUrl);
  }

  /**
   * Récupère un agent spécifique par son ID
   */
  getAgentById(id: string): Observable<Agent> {
    return this.http.get<Agent>(`${this.apiUrl}/${id}`);
  }

  /**
   * Crée un nouvel agent
   */
  createAgent(agent: AgentCreateDTO): Observable<Agent> {
    return this.http.post<Agent>(this.apiUrl, agent);
  }

  /**
   * Met à jour un agent existant
   */
  updateAgent(id: string, agent: AgentUpdateDTO): Observable<Agent> {
    return this.http.put<Agent>(`${this.apiUrl}/${id}`, agent);
  }

  /**
   * Envoie une requête à un agent
   */
  sendRequest(agentId: string, prompt: string): Observable<AgentResponse> {
    return this.http.post<AgentResponse>(`${this.apiUrl}/${agentId}/request`, {
      prompt,
      parameters: {}
    });
  }
}