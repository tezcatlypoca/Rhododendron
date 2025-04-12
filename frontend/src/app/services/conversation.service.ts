// src/app/services/conversation.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, switchMap } from 'rxjs/operators';
import { environment } from '../../environments/environment';
import { Conversation, Agent } from '../modeles/conversation.model';
import { Message } from '../modeles/message.model';

@Injectable({
  providedIn: 'root'
})
export class ConversationService {
  private apiUrl = `${environment.apiUrl}/conversations`;
  private agentsUrl = `${environment.apiUrl}/agents`;

  constructor(private http: HttpClient) { }

  getConversations(): Observable<Conversation[]> {
    return this.http.get<Conversation[]>(this.apiUrl).pipe(
      catchError(this.handleError)
    );
  }

  getConversation(id: string): Observable<Conversation> {
    return this.http.get<Conversation>(`${this.apiUrl}/${id}`).pipe(
      catchError(this.handleError)
    );
  }

  createConversation(conversationData: any): Observable<Conversation> {
    return this.http.post<Conversation>(this.apiUrl, conversationData).pipe(
      catchError(this.handleError)
    );
  }

  createDefaultConversation(): Observable<Conversation> {
    // D'abord, chercher un agent assistant existant
    return this.http.get<Agent[]>(`${this.agentsUrl}?role=assistant`).pipe(
      switchMap(agents => {
        if (agents && agents.length > 0) {
          // Utiliser le premier agent assistant trouvé
          return this.createConversation({
            title: "Nouvelle conversation",
            agent_id: agents[0].id
          });
        } else {
          // Créer un nouvel agent assistant
          const newAgent = {
            name: "Assistant par défaut",
            model_type: "llama",
            role: "assistant",
            config: { model: "codellama:7b-instruct-q4_0" }
          };
          return this.http.post<Agent>(this.agentsUrl, newAgent).pipe(
            switchMap(agent => {
              return this.createConversation({
                title: "Nouvelle conversation",
                agent_id: agent.id
              });
            })
          );
        }
      }),
      catchError(this.handleError)
    );
  }

  updateConversation(id: string, conversationData: any): Observable<Conversation> {
    return this.http.put<Conversation>(`${this.apiUrl}/${id}`, conversationData).pipe(
      catchError(this.handleError)
    );
  }

  deleteConversation(id: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${id}`).pipe(
      catchError(this.handleError)
    );
  }

  sendMessage(conversationId: string, messageData: { role: string; content: string; metadata: any }): Observable<Message> {
    return this.http.post<Message>(`${this.apiUrl}/${conversationId}/messages`, messageData)
      .pipe(
        catchError(error => {
          console.error('Erreur lors de l\'envoi du message:', error);
          return throwError(() => new Error('Erreur lors de l\'envoi du message'));
        })
      );
  }

  private handleError(error: any) {
    console.error('Une erreur est survenue:', error);
    return throwError(() => new Error('Une erreur est survenue lors de la communication avec le serveur.'));
  }
}
