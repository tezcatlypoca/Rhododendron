import { Component, Input, OnInit, ViewChild, ElementRef, AfterViewChecked, OnDestroy, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ConversationService } from '../../services/conversation.service';
import { WebsocketService } from '../../services/websocket.service';
import { StateService } from '../../services/state.service';
import { Message, MessageRole } from '../../modeles/message.model';
import { BoutonComponent } from '../bouton/bouton.component';
import { Subscription } from 'rxjs';
import { distinctUntilChanged } from 'rxjs/operators';

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
export class ChatComponent implements OnInit, AfterViewChecked, OnDestroy, OnChanges {
  @Input() conversationId: string = '';
  @Input() agentName: string = '';
  @Input() agentStatus: string = '';

  @ViewChild('messagesContainer') messagesContainer!: ElementRef;

  messages: Message[] = [];
  newMessageText: string = '';
  isLoading: boolean = false;
  error: string = '';
  private subscriptions = new Subscription();
  private pollingInterval: any = null;
  public websocketConnected: boolean = false;
  MessageRole = MessageRole;

  constructor(
    private conversationService: ConversationService,
    private websocketService: WebsocketService,
    private stateService: StateService
  ) {}

  ngOnChanges(changes: SimpleChanges) {
    console.log('Changements détectés dans le composant chat:', changes);
    if (changes['conversationId'] && changes['conversationId'].currentValue) {
      console.log('Nouveau conversationId:', changes['conversationId'].currentValue);
      this.loadMessages();
    }
  }

  ngOnInit(): void {
    console.log('Chat initialisé avec conversationId:', this.conversationId);
    if (this.conversationId) {
      // Chargement initial des messages
      this.loadMessages();

      // S'abonner aux messages en temps réel
      const messagesSub = this.stateService.activeConversationMessages$
        .subscribe((messages: Message[]) => {
          console.log('Mise à jour des messages dans le chat:', messages);
          this.messages = messages;
        });
      this.subscriptions.add(messagesSub);

      // Mettre en place le polling
      this.setupPolling();

      // S'abonner au statut WebSocket
      const connectionSub = this.websocketService.connectionStatus$
        .pipe(distinctUntilChanged())
        .subscribe(isConnected => {
          this.websocketConnected = isConnected;
          if (isConnected) {
            this.websocketService.subscribeToConversation(this.conversationId);
          }
        });
      this.subscriptions.add(connectionSub);
    }
  }

  ngOnDestroy(): void {
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

  private setupPolling(): void {
    this.pollingInterval = setInterval(() => {
      if (this.conversationId && !this.isLoading) {
        this.conversationService.getConversation(this.conversationId).subscribe({
          next: (conversation) => {
            if (conversation && conversation.messages) {
              this.stateService.updateActiveConversationMessages(conversation.messages);
            }
          },
          error: (err) => console.error('Erreur lors du polling des messages:', err)
        });
      }
    }, 3000);
  }

  loadMessages(): void {
    if (!this.conversationId) return;

    this.isLoading = true;
    this.error = '';

    // Charger la conversation complète
    this.conversationService.getConversation(this.conversationId)
      .subscribe({
        next: (conversation) => {
          console.log('Conversation chargée:', conversation);
          if (conversation && conversation.messages) {
            this.messages = conversation.messages;
            this.stateService.updateActiveConversationMessages(conversation.messages);
          }
          this.isLoading = false;
        },
        error: (err) => {
          console.error('Erreur lors du chargement de la conversation:', err);
          this.error = 'Erreur lors du chargement de la conversation';
          this.isLoading = false;
        }
      });
  }

  sendMessage(message: string): void {
    if (!this.conversationId || !message.trim()) return;

    // Créer et afficher immédiatement le message utilisateur
    const userMessage = {
      id: 'temp-' + new Date().getTime(),
      conversation_id: this.conversationId,
      role: 'user',
      content: message,
      timestamp: new Date().toISOString(),
      metadata: {}
    } as Message;

    // Ajouter à l'interface
    this.messages = [...this.messages, userMessage];

    // Vider le champ et activer l'indicateur de chargement
    this.newMessageText = '';
    this.isLoading = true;

    // Données pour l'API
    const messageData = {
      role: 'user',
      content: message,
      metadata: {}
    };

    // Envoyer au serveur
    this.conversationService.sendMessage(this.conversationId, messageData).subscribe({
      next: (response) => {
        // Mettre à jour l'ID si nécessaire
        if (response) {
          const index = this.messages.findIndex(m => m.id === userMessage.id);
          if (index !== -1) {
            this.messages[index].id = response.id;
          }
        }

        this.isLoading = false;

        // Déclencher le chargement de la réponse
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

  get connectionStatus(): string {
    return this.websocketConnected ? 'connecté' : 'déconnecté';
  }
}
