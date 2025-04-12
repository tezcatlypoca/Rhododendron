// src/app/composants/chat/chat.component.ts
import { Component, Input, OnInit, ViewChild, ElementRef, AfterViewChecked, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ConversationService } from '../../services/conversation.service';
import { Message, MessageRole } from '../../modeles/message.model';
import { BoutonComponent } from '../bouton/bouton.component';
import { interval, Subscription } from 'rxjs';

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
  private refreshSubscription?: Subscription;
  private lastMessageId: string = '';

  // Rendre l'enum accessible au template
  MessageRole = MessageRole;

  constructor(private conversationService: ConversationService) {}

  ngOnInit(): void {
    if (this.conversationId) {
      this.loadMessages();
      // Mettre en place le rafraîchissement périodique
      this.setupMessageRefresh();
    }
  }

  ngOnDestroy(): void {
    if (this.refreshSubscription) {
      this.refreshSubscription.unsubscribe();
    }
  }

  private setupMessageRefresh(): void {
    // Rafraîchir les messages toutes les 2 secondes
    this.refreshSubscription = interval(2000).subscribe(() => {
      this.checkNewMessages();
    });
  }

  private checkNewMessages(): void {
    if (!this.conversationId) return;

    this.conversationService.getConversation(this.conversationId)
      .subscribe({
        next: (conversation) => {
          if (conversation.messages && conversation.messages.length > 0) {
            const lastMessage = conversation.messages[conversation.messages.length - 1];
            if (lastMessage.id !== this.lastMessageId) {
              this.messages = conversation.messages;
              this.lastMessageId = lastMessage.id;
            }
          }
        },
        error: (err) => {
          console.error('Erreur lors de la vérification des nouveaux messages:', err);
        }
      });
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

  loadMessages(): void {
    this.isLoading = true;
    this.error = '';

    this.conversationService.getConversation(this.conversationId)
      .subscribe({
        next: (conversation) => {
          this.messages = conversation.messages || [];
          if (this.messages.length > 0) {
            this.lastMessageId = this.messages[this.messages.length - 1].id;
          }
          this.isLoading = false;
        },
        error: (err) => {
          console.error('Erreur lors du chargement des messages:', err);
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
        this.messages.push(response);
        this.lastMessageId = response.id;
        this.newMessageText = '';
        this.isLoading = false;
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
}
