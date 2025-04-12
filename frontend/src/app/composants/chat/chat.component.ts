// src/app/composants/chat/chat.component.ts
import { Component, Input, OnInit, OnDestroy, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Subscription } from 'rxjs';

import { ConversationService } from '../../services/conversation.service';
import { Agent } from '../../modeles/agent.model';
import { Conversation, Message } from '../../modeles/conversation.model';
import { BoutonComponent } from '../bouton/bouton.component';

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.scss'],
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, BoutonComponent]
})
export class ChatComponent implements OnInit, OnDestroy, AfterViewChecked {
  @Input() agent!: Agent;
  @ViewChild('messagesContainer') private messagesContainer!: ElementRef;

  messageForm: FormGroup;
  conversation: Conversation | null = null;
  messages: Message[] = [];
  enChargement: boolean = false;
  erreurMessage: string = '';
  
  private subscriptions = new Subscription();

  constructor(
    private fb: FormBuilder,
    private conversationService: ConversationService
  ) {
    this.messageForm = this.fb.group({
      message: ['', [Validators.required]]
    });
  }

  ngOnInit(): void {
    // Démarrer ou continuer une conversation avec l'agent
    this.conversationService.startConversation(this.agent);
    
    // S'abonner aux changements de la conversation active
    const conversationSub = this.conversationService.activeConversation$.subscribe(conversation => {
      this.conversation = conversation;
      this.messages = conversation?.messages || [];
    });
    
    this.subscriptions.add(conversationSub);
  }

  ngOnDestroy(): void {
    this.subscriptions.unsubscribe();
  }

  ngAfterViewChecked(): void {
    this.scrollToBottom();
  }

  /**
   * Envoie un message à l'agent
   */
  onSubmit(): void {
    if (this.messageForm.invalid || this.enChargement) {
      return;
    }

    const message = this.messageForm.value.message;
    this.enChargement = true;
    this.erreurMessage = '';
    
    this.conversationService.sendMessage(message).subscribe({
      next: () => {
        this.enChargement = false;
        this.messageForm.reset();
      },
      error: (error) => {
        this.enChargement = false;
        this.erreurMessage = error.message || 'Erreur lors de l\'envoi du message';
      }
    });
  }

  /**
   * Efface la conversation
   */
  clearConversation(): void {
    this.conversationService.clearActiveConversation();
  }

  /**
   * Fait défiler la vue jusqu'au dernier message
   */
  private scrollToBottom(): void {
    try {
      this.messagesContainer.nativeElement.scrollTop = this.messagesContainer.nativeElement.scrollHeight;
    } catch (err) {}
  }

  /**
   * Formate la date pour l'affichage
   */
  formatDate(date: Date): string {
    return new Date(date).toLocaleTimeString('fr-FR', {
      hour: '2-digit',
      minute: '2-digit'
    });
  }
}