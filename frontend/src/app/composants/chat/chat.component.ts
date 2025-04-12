// src/app/composants/chat/chat.component.ts
import { Component, Input, OnInit, ViewChild, ElementRef, AfterViewChecked, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ConversationService } from '../../services/conversation.service';
import { WebsocketService } from '../../services/websocket.service';
import { StateService } from '../../services/state.service';
import { Message, MessageRole } from '../../modeles/message.model';
import { BoutonComponent } from '../bouton/bouton.component';
import { Subscription } from 'rxjs';
import { distinctUntilChanged, filter } from 'rxjs/operators';

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.scss'],
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    BoutonComponent
  ]
})
export class ChatComponent implements OnInit, AfterViewChecked, OnDestroy {
  @Input() conversationId: string = '';
  @Input() agentName: string = '';
  @Input() agentStatus: string = '';

  @ViewChild('messagesContainer') messagesContainer!: ElementRef;

  private readonly defaultModel: string = 'codellama:7b-instruct-q4_0';
  messages: Message[] = [];
  newMessageText: string = '';
  isLoading: boolean = false;
  error: string = '';
  private subscriptions = new Subscription();
  
  // Propriété pour l'intervalle de polling
  private pollingInterval: any = null;
  
  // Rendre la propriété publique pour qu'elle soit accessible dans le template
  public websocketConnected: boolean = false;

  // Rendre l'enum accessible au template
  MessageRole = MessageRole;

  constructor(
    private conversationService: ConversationService,
    private websocketService: WebsocketService,
    private stateService: StateService
  ) {}

  ngOnInit(): void {
    if (this.conversationId) {
      // Charger les messages initiaux
      this.loadMessages();
      
      // Mettre en place le polling temporaire
      this.setupPolling();
      
      // S'abonner aux messages en temps réel via le StateService
      const messagesSub = this.stateService.activeConversationMessages$
        .subscribe(messages => {
          this.messages = messages;
        });
      this.subscriptions.add(messagesSub);
      
      // S'abonner au statut de la connexion WebSocket
      const connectionSub = this.websocketService.connectionStatus$
        .pipe(
          distinctUntilChanged()
        )
        .subscribe(isConnected => {
          this.websocketConnected = isConnected;
          if (isConnected) {
            // S'abonner à la conversation spécifique quand la connexion est établie
            this.websocketService.subscribeToConversation(this.conversationId);
          } else {
            // Essayer de se reconnecter si nécessaire
            // this.websocketService.connect(); // Temporairement désactivé pour éviter les boucles
          }
        });
      this.subscriptions.add(connectionSub);
      
      // Établir la connexion WebSocket initiale
      // Temporairement désactivé : this.websocketService.connect();
    }
  }

  ngOnDestroy(): void {
    // Nettoyage du polling
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
    }
    this.subscriptions.unsubscribe();
  }

  ngAfterViewChecked(): void {
    this.scrollToBottom();
  }

  private scrollToBottom(): void {
    try {
      this.messagesContainer.nativeElement.scrollTop = this.messagesContainer.nativeElement.scrollHeight;
    } catch (err) {
      console.error('Erreur lors du défilement:', err);
    }
  }

  // Méthode de polling temporaire
  private setupPolling(): void {
    this.pollingInterval = setInterval(() => {
      if (this.conversationId && !this.isLoading) {
        this.conversationService.getConversation(this.conversationId).subscribe({
          next: (conversation) => {
            if (conversation && conversation.messages) {
              this.messages = conversation.messages;
              this.stateService.updateActiveConversationMessages(conversation.messages);
            }
          },
          error: (err) => console.error('Erreur lors du polling des messages:', err)
        });
      }
    }, 2000);  // Intervalle de 2 secondes
  }

  loadMessages(): void {
    this.isLoading = true;
    this.error = '';

    this.conversationService.getConversation(this.conversationId)
      .subscribe({
        next: (conversation) => {
          if (conversation && conversation.messages) {
            this.messages = conversation.messages;
            this.stateService.updateActiveConversationMessages(conversation.messages);
          }
          this.isLoading = false;
        },
        error: (err) => {
          console.error('Erreur lors du chargement de la conversation:', err);
          this.error = 'Erreur lors du chargement des messages';
          this.isLoading = false;
        }
      });
  }

  sendMessage(message: string): void {
    if (!this.conversationId || !message.trim()) return;

    this.isLoading = true;
    const messageData = {
      role: 'user',
      content: message,
      metadata: {}
    };

    this.conversationService.sendMessage(this.conversationId, messageData).subscribe({
      next: (response) => {
        // Ajouter manuellement le message au lieu d'attendre WebSocket
        if (response) {
          const userMessage = {
            id: response.id,
            conversation_id: response.conversation_id,
            role: response.role,
            content: message,
            timestamp: new Date().toISOString(),
            metadata: {}
          };
          this.messages = [...this.messages, userMessage];
          this.stateService.addMessageToActiveConversation(userMessage);
        }
        
        this.newMessageText = '';
        this.isLoading = false;
        
        // Déclencher immédiatement un polling pour récupérer la réponse de l'agent
        setTimeout(() => {
          this.loadMessages();
        }, 1000);
      },
      error: (error) => {
        console.error('Erreur lors de l\'envoi du message:', error);
        this.error = 'Erreur lors de l\'envoi du message';
        this.isLoading = false;
      }
    });
  }

  getMessageClasses(message: Message): any {
    return {
      'message': true,
      'user-message': message.role === MessageRole.USER,
      'assistant-message': message.role === MessageRole.ASSISTANT,
      'system-message': message.role === MessageRole.SYSTEM
    };
  }

  formatTimestamp(timestamp: string | Date): string {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
  }

  /**
   * État de la connexion WebSocket (pour affichage dans l'interface)
   */
  get connectionStatus(): string {
    return this.websocketConnected ? 'connecté' : 'déconnecté';
  }
}