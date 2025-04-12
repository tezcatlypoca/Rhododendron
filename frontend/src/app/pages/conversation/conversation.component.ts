// src/app/pages/conversation/conversation.component.ts
import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';
import { Subscription, switchMap } from 'rxjs';

import { AgentService } from '../../services/agent.service';
import { ConversationService } from '../../services/conversation.service';
import { Agent } from '../../modeles/agent.model';
import { ChatComponent } from '../../composants/chat/chat.component';
import { BoutonComponent } from '../../composants/bouton/bouton.component';

@Component({
  selector: 'app-conversation',
  templateUrl: './conversation.component.html',
  styleUrls: ['./conversation.component.scss'],
  standalone: true,
  imports: [CommonModule, RouterModule, ChatComponent, BoutonComponent]
})
export class ConversationComponent implements OnInit, OnDestroy {
  agentId: string = '';
  agent: Agent | null = null;
  enChargement: boolean = true;
  erreurMessage: string = '';
  
  private subscriptions = new Subscription();

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private agentService: AgentService,
    private conversationService: ConversationService
  ) {}

  ngOnInit(): void {
    // Récupérer l'ID de l'agent depuis les paramètres de l'URL
    const routeSub = this.route.paramMap.pipe(
      switchMap(params => {
        this.agentId = params.get('id') || '';
        
        if (!this.agentId) {
          this.erreurMessage = 'ID d\'agent non spécifié';
          this.enChargement = false;
          return [];
        }
        
        return this.agentService.getAgentById(this.agentId);
      })
    ).subscribe({
      next: (agent) => {
        this.agent = agent;
        this.enChargement = false;
      },
      error: (error) => {
        this.erreurMessage = 'Impossible de charger les informations de l\'agent';
        this.enChargement = false;
        console.error('Erreur lors du chargement de l\'agent:', error);
      }
    });
    
    this.subscriptions.add(routeSub);
  }

  ngOnDestroy(): void {
    this.subscriptions.unsubscribe();
  }

  /**
   * Retourne à la liste des agents
   */
  retourListe(): void {
    this.router.navigate(['/agents']);
  }
}