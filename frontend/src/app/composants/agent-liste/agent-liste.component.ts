// src/app/composants/agent-liste/agent-liste.component.ts
import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AgentService } from '../../services/agent.service';
import { Agent } from '../../modeles/agent.model';
import { Subscription } from 'rxjs';
import { BoutonComponent } from '../bouton/bouton.component';

@Component({
  selector: 'app-agent-liste',
  templateUrl: './agent-liste.component.html',
  styleUrls: ['./agent-liste.component.scss'],
  standalone: true,
  imports: [
    CommonModule,
    BoutonComponent
  ]
})
export class AgentListeComponent implements OnInit, OnDestroy {
  agents: Agent[] = [];
  enChargement: boolean = true;
  erreurMessage: string = '';
  agentSelectionneId: string | null = null;
  
  private subscriptions = new Subscription();

  constructor(private agentService: AgentService) {}

  ngOnInit(): void {
    this.chargerAgents();
  }

  ngOnDestroy(): void {
    this.subscriptions.unsubscribe();
  }

  chargerAgents(): void {
    this.enChargement = true;
    this.erreurMessage = '';
    
    const sub = this.agentService.getAllAgents().subscribe({
      next: (agents) => {
        this.agents = agents;
        this.enChargement = false;
      },
      error: (error) => {
        this.erreurMessage = 'Erreur lors du chargement des agents';
        this.enChargement = false;
        console.error('Erreur de chargement des agents:', error);
      }
    });
    
    this.subscriptions.add(sub);
  }

  toggleAgentActivation(agent: Agent, event: Event): void {
    event.stopPropagation();
    
    const updatedAgent = {
      is_active: !agent.is_active
    };
    
    this.agentService.updateAgent(agent.id, updatedAgent).subscribe({
      next: (response) => {
        // Mettre à jour l'agent dans la liste
        const index = this.agents.findIndex(a => a.id === agent.id);
        if (index !== -1) {
          this.agents[index] = response;
        }
      },
      error: (error) => {
        console.error('Erreur lors de la mise à jour de l\'agent:', error);
      }
    });
  }

  selectionnerAgent(agent: Agent): void {
    this.agentSelectionneId = this.agentSelectionneId === agent.id ? null : agent.id;
  }

  formatDate(dateString: string): string {
    if (!dateString) return 'Jamais';
    
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', { 
      day: '2-digit', 
      month: '2-digit', 
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }
}