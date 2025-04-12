// src/app/services/websocket.service.ts
import { Injectable } from '@angular/core';
import { Observable, Subject, BehaviorSubject } from 'rxjs';
import { environment } from '../../environments/environment';
import { AuthService } from './auth.service';
import { webSocket, WebSocketSubject } from 'rxjs/webSocket';
import { catchError, tap, switchMap, filter } from 'rxjs/operators';
import { Message } from '../modeles/message.model';

export interface WebSocketMessage {
  type: string;
  payload: any;
}

/**
 * Service de communication WebSocket
 * Gère la connexion temps réel avec le backend
 */
@Injectable({
  providedIn: 'root'
})
export class WebsocketService {
  private socket$: WebSocketSubject<WebSocketMessage> | null = null;
  private messagesSubject = new Subject<Message>();
  private connectionStatusSubject = new BehaviorSubject<boolean>(false);

  // Observables publics
  public messages$ = this.messagesSubject.asObservable();
  public connectionStatus$ = this.connectionStatusSubject.asObservable();

  constructor(private authService: AuthService) {}

  /**
   * Établit une connexion WebSocket
   */
  public connect(): void {
    console.log('WebSocket connection temporairement désactivée');
    // Pour l'instant, simuler une connexion réussie pour éviter les erreurs
    this.connectionStatusSubject.next(true);
    
    /* Temporairement désactivé pour éviter les erreurs 403 en boucle
    if (this.socket$ !== null) {
      this.socket$.complete();
    }

    const token = this.authService.obtenirToken();
    const wsUrl = `${environment.wsUrl}?token=${token}`;

    this.socket$ = webSocket<WebSocketMessage>({
      url: wsUrl,
      openObserver: {
        next: () => {
          console.log('WebSocket connecté');
          this.connectionStatusSubject.next(true);
        }
      },
      closeObserver: {
        next: () => {
          console.log('WebSocket déconnecté');
          this.connectionStatusSubject.next(false);
          
          // Tentative de reconnexion après un délai
          setTimeout(() => this.connect(), 5000);
        }
      }
    });

    this.socket$.pipe(
      filter(message => message.type === 'new_message'),
      tap(message => console.log('Message WebSocket reçu:', message)),
      catchError(error => {
        console.error('Erreur WebSocket:', error);
        // Tentative de reconnexion après un délai
        setTimeout(() => this.connect(), 5000);
        throw error;
      })
    ).subscribe(message => {
      if (message.type === 'new_message') {
        this.messagesSubject.next(message.payload as Message);
      }
    });
    */
  }

  /**
   * Souscrit à un canal spécifique (conversation)
   * @param conversationId ID de la conversation à suivre
   */
  public subscribeToConversation(conversationId: string): void {
    console.log(`Abonnement simulé à la conversation: ${conversationId}`);
    // Temporairement désactivé
    /*
    if (this.socket$ && this.socket$.closed === false) {
      this.socket$.next({
        type: 'subscribe',
        payload: { conversation_id: conversationId }
      });
    } else {
      console.error('Tentative d\'abonnement sur un socket fermé');
      // Se connecter avant de souscrire
      this.connect();
      setTimeout(() => this.subscribeToConversation(conversationId), 1000);
    }
    */
  }

  /**
   * Envoie un message via WebSocket
   * @param message Message à envoyer
   */
  public sendMessage(message: WebSocketMessage): void {
    console.log('Envoi de message WebSocket simulé:', message);
    // Temporairement désactivé
    /*
    if (this.socket$ && this.socket$.closed === false) {
      this.socket$.next(message);
    } else {
      console.error('Tentative d\'envoi sur un socket fermé');
    }
    */
  }

  /**
   * Ferme la connexion WebSocket
   */
  public disconnect(): void {
    console.log('Déconnexion WebSocket simulée');
    this.connectionStatusSubject.next(false);
    
    /*
    if (this.socket$) {
      this.socket$.complete();
      this.socket$ = null;
      this.connectionStatusSubject.next(false);
    }
    */
  }
}