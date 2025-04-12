// src/app/composants/chat/chat.component.ts
import { Component, Input, OnInit, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ConversationService } from '../../services/conversation.service';
import { Message, MessageRole } from '../../modeles/conversation.model';
import { BoutonComponent } from '../bouton/bouton.component';

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
export class ChatComponent implements OnInit, AfterViewChecked {
  @Input() conversationId: string = '';
  @Input() agentName: string = 'Assistant';
  
  @ViewChild('messagesContainer') messagesContainer!: ElementRef;
  
  messages: Message[] = [];
  newMessageText: string = '';
  isLoading: boolean = false;
  error: string = '';
  
  // Rendre l'enum accessible au template
  MessageRole = MessageRole;
  
  constructor(private conversationService: ConversationService) {}
  
  ngOnInit(): void {
    this.loadMessages();
  }
  
  ngAfterViewChecked(): void {
    this.scrollToBottom();
  }
  
  loadMessages(): void {
    // Chargement des messages depuis le service
    if (!this.conversationId) return;
    
    this.isLoading = true;
    
    this.conversationService.getConversation(this.conversationId)
      .subscribe({
        next: (conversation) => {
          this.messages = conversation.messages || [];
          this.isLoading = false;
          setTimeout(() => this.scrollToBottom(), 100);
        },
        error: (error) => {
          this.error = "Impossible de charger les messages";
          this.isLoading = false;
          console.error("Erreur lors du chargement des messages:", error);
        }
      });
  }
  
  sendMessage(): void {
    if (!this.newMessageText.trim() || !this.conversationId) return;
    
    this.isLoading = true;
    this.error = '';
    
    this.conversationService.sendMessage(this.conversationId, this.newMessageText)
      .subscribe({
        next: () => {
          // Le message est déjà ajouté à la conversation côté serveur
          // On recharge les messages pour avoir la réponse de l'agent
          this.loadMessages();
          this.newMessageText = '';
        },
        error: (error) => {
          this.error = "Erreur lors de l'envoi du message";
          this.isLoading = false;
          console.error("Erreur lors de l'envoi du message:", error);
        }
      });
  }
  
  scrollToBottom(): void {
    try {
      this.messagesContainer.nativeElement.scrollTop = this.messagesContainer.nativeElement.scrollHeight;
    } catch (err) { }
  }
  
  getMessageClasses(message: Message): any {
    return {
      'user': message.role === MessageRole.USER,
      'agent': message.role === MessageRole.ASSISTANT
    };
  }
  
  formatTimestamp(timestamp: string | Date): string {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }
}