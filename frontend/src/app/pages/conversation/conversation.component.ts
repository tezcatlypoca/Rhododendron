// src/app/pages/conversation/conversation.component.ts
import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { Subscription } from 'rxjs';
import { CommonModule } from '@angular/common';

import { ConversationService } from '../../services/conversation.service';
import { AgentService } from '../../services/agent.service';
import { Conversation } from '../../modeles/conversation.model';
import { Agent } from '../../modeles/agent.model';
import { ChatComponent } from '../../composants/chat/chat.component';

@Component({
  selector: 'app-conversation',
  templateUrl: './conversation.component.html',
  styleUrls: ['./conversation.component.scss'],
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    ChatComponent
  ]
})
export class ConversationComponent implements OnInit, OnDestroy {
  conversation: Conversation | null = null;
  agent: Agent | null = null;
  loading: boolean = true;
  error: string = '';
  
  private subscriptions = new Subscription();

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private conversationService: ConversationService,
    private agentService: AgentService
  ) {}

  ngOnInit(): void {
    // Vérifier si on a un ID de conversation dans l'URL
    const conversationId = this.route.snapshot.paramMap.get('id');
    
    if (conversationId === 'new') {
      // Directement créer une conversation avec l'assistant par défaut
      this.startDefaultConversation();
    } else if (conversationId) {
      // Charger une conversation existante
      this.loadConversation(conversationId);
    } else {
      // Rediriger vers la création d'une nouvelle conversation
      this.router.navigate(['/conversation/new']);
    }
  }

  ngOnDestroy(): void {
    this.subscriptions.unsubscribe();
  }

  startDefaultConversation(): void {
    this.loading = true;
    this.error = '';
    
    // Créer directement une conversation avec un titre par défaut
    // Sans spécifier d'agent_id (utilisation de l'agent par défaut côté backend)
    this.conversationService.createConversation("Nouvelle conversation")
      .subscribe({
        next: (conversation) => {
          this.conversation = conversation;
          this.loading = false;
          
          // Si un agent_id est retourné, charger l'agent
          if (conversation.agent_id) {
            this.loadAgent(conversation.agent_id);
          }
          
          // Remplacer l'URL 'new' par l'ID réel
          this.router.navigate(['/conversation', conversation.id], { replaceUrl: true });
        },
        error: (error) => {
          this.error = "Impossible de créer une nouvelle conversation";
          this.loading = false;
          console.error("Erreur lors de la création de la conversation:", error);
        }
      });
  }

  loadConversation(conversationId: string): void {
    this.loading = true;
    
    const sub = this.conversationService.getConversation(conversationId)
      .subscribe({
        next: (conversation) => {
          this.conversation = conversation;
          this.loading = false;
          
          // Si la conversation a un agent, charger les informations de l'agent
          if (conversation.agent_id) {
            this.loadAgent(conversation.agent_id);
          }
        },
        error: (error) => {
          this.error = "Impossible de charger la conversation";
          this.loading = false;
          console.error("Erreur lors du chargement de la conversation:", error);
        }
      });
    
    this.subscriptions.add(sub);
  }

  loadAgent(agentId: string): void {
    const sub = this.agentService.getAgentById(agentId)
      .subscribe({
        next: (agent) => {
          this.agent = agent;
        },
        error: (error) => {
          console.error("Erreur lors du chargement de l'agent:", error);
        }
      });
    
    this.subscriptions.add(sub);
  }

  retry(): void {
    this.startDefaultConversation();
  }
}