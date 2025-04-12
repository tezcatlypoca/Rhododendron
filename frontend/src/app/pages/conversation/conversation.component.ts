import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, ActivatedRoute } from '@angular/router';
import { ChatComponent } from '../../composants/chat/chat.component';
import { ConversationService } from '../../services/conversation.service';
import { Conversation } from '../../modeles/conversation.model';

@Component({
  selector: 'app-conversation',
  standalone: true,
  imports: [CommonModule, RouterLink, ChatComponent],
  templateUrl: './conversation.component.html',
  styleUrls: ['./conversation.component.scss']
})
export class ConversationComponent implements OnInit {
  conversationId: string = '';
  agentName: string = 'Assistant';

  constructor(
    private route: ActivatedRoute,
    private conversationService: ConversationService
  ) {}

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.conversationId = params['conv_id'];
      if (!this.conversationId) {
        // Créer une nouvelle conversation avec un agent assistant
        this.conversationService.createDefaultConversation().subscribe({
          next: (conversation: Conversation) => {
            this.conversationId = conversation.id;
            this.agentName = conversation.agent?.name || 'Assistant';
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
          },
          error: (error: any) => {
            console.error('Erreur lors du chargement de la conversation:', error);
          }
        });
      }
    });
  }
}
