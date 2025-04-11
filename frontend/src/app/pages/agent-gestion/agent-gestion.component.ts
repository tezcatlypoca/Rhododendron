// src/app/pages/agent-gestion/agent-gestion.component.ts
import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AgentManagerComponent } from '../../composants/agent-manager/agent-manager.component';

@Component({
  selector: 'app-agent-gestion',
  templateUrl: './agent-gestion.component.html',
  styleUrls: ['./agent-gestion.component.scss'],
  standalone: true,
  imports: [
    CommonModule,
    AgentManagerComponent
  ]
})
export class AgentGestionComponent {
  constructor() {}
}