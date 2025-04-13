import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, ActivatedRoute } from '@angular/router';
import { ChatComponent } from '../../composants/chat/chat.component';
import { ConversationService } from '../../services/conversation.service';
import { StateService } from '../../services/state.service';
import { WebsocketService } from '../../services/websocket.service';
import { Conversation } from '../../modeles/conversation.model';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-conversation',
  standalone: true,
  imports: [CommonModule, RouterLink, ChatComponent],
  templateUrl: './conversation.component.html',
  styleUrls: ['./conversation.component.scss']
})
export class ConversationComponent implements OnInit, OnDestroy {
  conversationId: string = '';
  agentName: string = 'Assistant';
  private subscriptions = new Subscription();

  constructor(
    private route: ActivatedRoute,
    private conversationService: ConversationService,
    private stateService: StateService,
    private websocketService: WebsocketService
  ) {}

  ngOnInit() {
    const routeSub = this.route.params.subscribe(params => {
      this.conversationId = params['conv_id'];
      if (!this.conversationId) {
        // Créer une nouvelle conversation
        this.conversationService.createDefaultConversation().subscribe({
          next: (conversation: Conversation) => {
            this.conversationId = conversation.id;
            this.agentName = conversation.agent?.name || 'Assistant';

            // Se connecter au WebSocket
            this.websocketService.connect();
            this.websocketService.subscribeToConversation(this.conversationId);

            // Mettre à jour l'état global
            this.stateService.setActiveConversation(conversation);

            // Explicitement charger les messages
            this.conversationService.loadMessages(this.conversationId).subscribe({
              next: (messages) => {
                console.log('Messages initiaux chargés pour nouvelle conversation:', messages);
                this.stateService.updateActiveConversationMessages(messages);
              }
            });
          },
          error: (error) => {
            console.error('Erreur lors de la création de la conversation:', error);
          }
        });
      } else {
        // Charger une conversation existante
        this.conversationService.getConversation(this.conversationId).subscribe({
          next: (conversation: Conversation) => {
            this.agentName = conversation.agent?.name || 'Assistant';

            // Mettre à jour l'état global
            this.stateService.setActiveConversation(conversation);

            // Se connecter au WebSocket
            this.websocketService.connect();
            this.websocketService.subscribeToConversation(this.conversationId);

            // Explicitement charger les messages
            this.conversationService.loadMessages(this.conversationId).subscribe({
              next: (messages) => {
                console.log('Messages initiaux chargés pour conversation existante:', messages);
                this.stateService.updateActiveConversationMessages(messages);
              }
            });
          },
          error: (error) => {
            console.error('Erreur lors du chargement de la conversation:', error);
          }
        });
      }
    });

    this.subscriptions.add(routeSub);
  }

  ngOnDestroy() {
    this.subscriptions.unsubscribe();
  }
}
