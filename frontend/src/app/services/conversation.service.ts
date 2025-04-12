// src/app/services/conversation.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, throwError } from 'rxjs';
import { tap, catchError } from 'rxjs/operators';
import { v4 as uuidv4 } from 'uuid';

import { environment } from '../../environments/environment';
import { Agent } from '../modeles/agent.model';
import { Conversation, Message, MessageRequest, MessageResponse } from '../modeles/conversation.model';

@Injectable({
  providedIn: 'root'
})
export class ConversationService {
  private apiUrl = `${environment.apiUrl}/agents`;
  
  // Conversation active
  private activeConversationSubject = new BehaviorSubject<Conversation | null>(null);
  activeConversation$ = this.activeConversationSubject.asObservable();
  
  // Map des conversations par agent
  private conversations: Map<string, Conversation> = new Map();

  constructor(private http: HttpClient) {}

  /**
   * Démarre ou continue une conversation avec un agent
   */
  startConversation(agent: Agent): void {
    let conversation = this.conversations.get(agent.id);
    
    if (!conversation) {
      // Créer une nouvelle conversation si elle n'existe pas
      conversation = {
        id: uuidv4(),
        agentId: agent.id,
        messages: [],
        lastActivity: new Date()
      };
      this.conversations.set(agent.id, conversation);
    }
    
    this.activeConversationSubject.next(conversation);
  }

  /**
   * Envoie un message à l'agent et ajoute la réponse à la conversation
   */
  sendMessage(message: string): Observable<MessageResponse> {
    const conversation = this.activeConversationSubject.value;
    
    if (!conversation) {
      return throwError(() => new Error('Aucune conversation active'));
    }
    
    // Ajouter le message de l'utilisateur à la conversation
    const userMessage: Message = {
      id: uuidv4(),
      sender: 'user',
      content: message,
      timestamp: new Date()
    };
    
    conversation.messages.push(userMessage);
    conversation.lastActivity = new Date();
    this.activeConversationSubject.next({...conversation});
    
    // Envoyer la requête au backend
    const request: MessageRequest = {
      prompt: message
    };
    
    return this.http.post<MessageResponse>(`${this.apiUrl}/${conversation.agentId}/request`, request)
      .pipe(
        tap(response => {
          // Ajouter la réponse de l'agent à la conversation
          const agentMessage: Message = {
            id: uuidv4(),
            sender: 'agent',
            content: response.response,
            timestamp: new Date(response.timestamp)
          };
          
          conversation.messages.push(agentMessage);
          conversation.lastActivity = new Date();
          this.activeConversationSubject.next({...conversation});
        }),
        catchError(error => {
          console.error('Erreur lors de l\'envoi du message:', error);
          return throwError(() => new Error(error.error?.detail || 'Erreur lors de la communication avec l\'agent'));
        })
      );
  }

  /**
   * Récupère la conversation active
   */
  getActiveConversation(): Conversation | null {
    return this.activeConversationSubject.value;
  }

  /**
   * Récupère toutes les conversations
   */
  getAllConversations(): Conversation[] {
    return Array.from(this.conversations.values());
  }

  /**
   * Efface la conversation active
   */
  clearActiveConversation(): void {
    const conversation = this.activeConversationSubject.value;
    
    if (conversation) {
      conversation.messages = [];
      conversation.lastActivity = new Date();
      this.activeConversationSubject.next({...conversation});
    }
  }
}