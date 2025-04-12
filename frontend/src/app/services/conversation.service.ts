// src/app/services/conversation.service.ts
import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { BehaviorSubject, Observable, throwError } from 'rxjs';
import { tap, catchError, map } from 'rxjs/operators';

import { environment } from '../../environments/environment';
import { Conversation, Message, MessageRequest, MessageResponse, MessageRole } from '../modeles/conversation.model';

@Injectable({
  providedIn: 'root'
})
export class ConversationService {
  private apiUrl = `${environment.apiUrl}`;
  
  // Conversation active
  private activeConversationSubject = new BehaviorSubject<Conversation | null>(null);
  activeConversation$ = this.activeConversationSubject.asObservable();

  constructor(private http: HttpClient) {}

  /**
   * Crée une nouvelle conversation
   */
  createConversation(title: string, agent_id?: string): Observable<Conversation> {
    // CORRECTION IMPORTANTE: Utiliser HttpParams pour les paramètres de requête
    let params = new HttpParams()
      .set('title', title);
    
    if (agent_id) {
      params = params.set('agent_id', agent_id);
    }
    
    // Notez que le corps est null et les paramètres sont passés via params
    return this.http.post<Conversation>(`${this.apiUrl}/conversations`, null, { params })
      .pipe(
        tap(conversation => {
          this.activeConversationSubject.next(conversation);
        }),
        catchError(error => {
          console.error('Erreur lors de la création de la conversation:', error);
          return throwError(() => new Error(error.error?.detail || 'Erreur lors de la création de la conversation'));
        })
      );
  }

  /**
   * Récupère toutes les conversations
   */
  getAllConversations(): Observable<Conversation[]> {
    return this.http.get<Conversation[]>(`${this.apiUrl}/conversations`);
  }

  /**
   * Récupère une conversation spécifique
   */
  getConversation(conversationId: string): Observable<Conversation> {
    return this.http.get<Conversation>(`${this.apiUrl}/conversations/${conversationId}`)
      .pipe(
        tap(conversation => {
          this.activeConversationSubject.next(conversation);
        })
      );
  }

  /**
   * Envoie un message dans une conversation
   */
  sendMessage(conversationId: string, message: string): Observable<Message> {
    const request: MessageRequest = {
      prompt: message
    };
    
    return this.http.post<Message>(`${this.apiUrl}/conversations/${conversationId}/send`, request)
      .pipe(
        catchError(error => {
          console.error('Erreur lors de l\'envoi du message:', error);
          return throwError(() => new Error(error.error?.detail || 'Erreur lors de l\'envoi du message'));
        })
      );
  }

  /**
   * Met à jour le titre d'une conversation
   */
  updateConversationTitle(conversationId: string, newTitle: string): Observable<Conversation> {
    // Utiliser HttpParams pour ce paramètre également
    const params = new HttpParams().set('new_title', newTitle);
    return this.http.put<Conversation>(`${this.apiUrl}/conversations/${conversationId}/title`, null, { params });
  }

  /**
   * Supprime une conversation
   */
  deleteConversation(conversationId: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/conversations/${conversationId}`);
  }

  /**
   * Définit la conversation active
   */
  setActiveConversation(conversation: Conversation): void {
    this.activeConversationSubject.next(conversation);
  }

  /**
   * Récupère la conversation active
   */
  getActiveConversation(): Conversation | null {
    return this.activeConversationSubject.value;
  }

  /**
   * Démarre une conversation avec un agent prédéfini
   */
  startConversationWithDefaultAgent(): Observable<Conversation> {
    // Créer une conversation avec l'agent par défaut
    return this.createConversation("Nouvelle conversation", "agent-id-par-defaut");
  }
}