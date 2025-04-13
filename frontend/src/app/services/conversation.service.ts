// src/app/services/conversation.service.ts
import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http'; // Ajout de HttpParams ici
import { Observable, throwError, of } from 'rxjs';
import { catchError, switchMap, tap, take } from 'rxjs/operators';
import { environment } from '../../environments/environment';
import { Conversation, Agent } from '../modeles/conversation.model';
import { Message } from '../modeles/message.model';
import { StateService } from './state.service';
import { WebsocketService } from './websocket.service';

@Injectable({
  providedIn: 'root'
})
export class ConversationService {
  private apiUrl = `${environment.apiUrl}/conversations`;
  private agentsUrl = `${environment.apiUrl}/agents`;

  constructor(
    private http: HttpClient,
    private stateService: StateService,
    private websocketService: WebsocketService
  ) {
    // S'abonner aux messages WebSocket pour mettre à jour l'état
    this.websocketService.messages$.subscribe(message => {
      this.stateService.addMessageToActiveConversation(message);
    });
  }

  getConversations(): Observable<Conversation[]> {
    return this.http.get<Conversation[]>(this.apiUrl).pipe(
      tap(conversations => {
        this.stateService.updateConversations(conversations);
      }),
      catchError(this.handleError)
    );
  }

  getConversation(id: string): Observable<Conversation> {
    return this.http.get<Conversation>(`${this.apiUrl}/${id}`).pipe(
      tap(conversation => {
        console.log('Conversation récupérée:', conversation);
        if (conversation && conversation.messages) {
          this.stateService.setActiveConversation(conversation);
          this.stateService.updateActiveConversationMessages(conversation.messages);
        }
        // S'abonner à cette conversation via WebSocket
        this.websocketService.subscribeToConversation(id);
      }),
      catchError(this.handleError)
    );
  }

  createConversation(conversationData: any): Observable<Conversation> {
    return this.http.post<Conversation>(this.apiUrl, conversationData).pipe(
      tap(conversation => {
        this.stateService.addConversation(conversation);
      }),
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
      tap(updatedConversation => {
        this.stateService.updateConversation(updatedConversation);
      }),
      catchError(this.handleError)
    );
  }

  deleteConversation(id: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${id}`).pipe(
      tap(() => {
        this.stateService.deleteConversation(id);
      }),
      catchError(this.handleError)
    );
  }

  sendMessage(conversationId: string, messageData: { role: string; content: string; metadata: any }): Observable<Message> {
    // S'assurer que la connexion WebSocket est établie
    const isConnected = this.websocketService.connectionStatus$.pipe(take(1));

    return isConnected.pipe(
      switchMap(connected => {
        if (!connected) {
          this.websocketService.connect();
          this.websocketService.subscribeToConversation(conversationId);
        }

        return this.http.post<Message>(`${this.apiUrl}/${conversationId}/messages`, messageData).pipe(
          tap(message => {
            // On n'ajoute pas le message ici car il sera reçu via WebSocket
            // Cela évite les doublons et garantit l'ordre correct
          }),
          catchError(error => {
            console.error('Erreur lors de l\'envoi du message:', error);
            return throwError(() => new Error('Erreur lors de l\'envoi du message'));
          })
        );
      })
    );
  }

  loadMessages(conversationId: string, limit?: number): Observable<Message[]> {
    return this.http.get<Message[]>(`${this.apiUrl}/${conversationId}/messages${limit ? `?limit=${limit}` : ''}`).pipe(
      tap(messages => {
        console.log('Messages chargés depuis l\'API:', messages);
        // Mettre à jour les messages dans le state
        this.stateService.updateActiveConversationMessages(messages);
        // Mettre à jour la conversation active avec les messages
        this.stateService.activeConversation$.pipe(take(1)).subscribe(activeConversation => {
          if (activeConversation) {
            const updatedConversation = {
              ...activeConversation,
              messages: messages
            };
            this.stateService.setActiveConversation(updatedConversation);
          }
        });
      }),
      catchError(this.handleError)
    );
  }

  private handleError(error: any) {
    console.error('Une erreur est survenue:', error);
    return throwError(() => new Error('Une erreur est survenue lors de la communication avec le serveur.'));
  }
}
