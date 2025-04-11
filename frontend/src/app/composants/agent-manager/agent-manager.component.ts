// src/app/composants/agent-manager/agent-manager.component.ts
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AgentCreationComponent } from '../agent-creation/agent-creation.component';
import { AgentListeComponent } from '../agent-liste/agent-liste.component';

@Component({
  selector: 'app-agent-manager',
  templateUrl: './agent-manager.component.html',
  styleUrls: ['./agent-manager.component.scss'],
  standalone: true,
  imports: [
    CommonModule,
    AgentCreationComponent,
    AgentListeComponent
  ]
})
export class AgentManagerComponent implements OnInit {
  ongletActif: 'liste' | 'creation' = 'liste';

  constructor() {}

  ngOnInit(): void {}

  changerOnglet(onglet: 'liste' | 'creation'): void {
    this.ongletActif = onglet;
  }

  onAgentCreated(): void {
    // Basculer automatiquement vers l'onglet de liste après création d'un agent
    this.ongletActif = 'liste';
  }
}