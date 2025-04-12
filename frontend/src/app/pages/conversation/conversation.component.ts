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
    // S'abonner aux changements de paramètres d'URL
    const routeSub = this.route.params.subscribe(params => {
      this.conversationId = params['conv_id'];
      if (!this.conversationId) {
        // Créer une nouvelle conversation avec un agent assistant
        this.conversationService.createDefaultConversation().subscribe({
          next: (conversation: Conversation) => {
            this.conversationId = conversation.id;
            this.agentName = conversation.agent?.name || 'Assistant';
            
            // Se connecter au WebSocket et s'abonner à cette conversation
            this.websocketService.connect();
            this.websocketService.subscribeToConversation(this.conversationId);
            
            // Mettre à jour l'état global
            this.stateService.setActiveConversation(conversation);
          },
          error: (error: any) => {
            console.error('Erreur lors de la création de la conversation:', error);
          }
        });
      } else {
        // Charger les détails de la conversation existante
        this.conversationService.getConversation(this.conversationId).subscribe({
          next: (conversation: Conversation) => {
            this.agentName = conversation.agent?.name || 'Assistant';
            
            // Se connecter au WebSocket et s'abonner à cette conversation
            this.websocketService.connect();
            this.websocketService.subscribeToConversation(this.conversationId);
          },
          error: (error: any) => {
            console.error('Erreur lors du chargement de la conversation:', error);
          }
        });
      }
    });
    
    this.subscriptions.add(routeSub);
    
    // S'abonner aux changements de la conversation active
    const conversationSub = this.stateService.activeConversation$.subscribe(conversation => {
      if (conversation) {
        this.agentName = conversation.agent?.name || 'Assistant';
      }
    });
    
    this.subscriptions.add(conversationSub);
  }
  
  ngOnDestroy() {
    // Nettoyer toutes les souscriptions
    this.subscriptions.unsubscribe();
  }
}