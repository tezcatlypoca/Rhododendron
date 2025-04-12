// src/app/composants/agent-creation/agent-creation.component.ts
import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { AgentService } from '../../services/agent.service';
import { AgentCreateDTO } from '../../modeles/agent.model';
import { ChampFormulaireComponent } from '../champ-formulaire/champ-formulaire.component';
import { BoutonComponent } from '../bouton/bouton.component';

@Component({
  selector: 'app-agent-creation',
  templateUrl: './agent-creation.component.html',
  styleUrls: ['./agent-creation.component.scss'],
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    ChampFormulaireComponent,
    BoutonComponent
  ]
})
export class AgentCreationComponent {
  @Output() agentCreated = new EventEmitter<void>();
  
  formulaireAgent: FormGroup;
  enChargement: boolean = false;
  erreurMessage: string = '';
  succesMessage: string = '';
  
  modelTypes: string[] = ['codellama', 'llama3', 'autre-modele'];
  
  messagesErreur = {
    name: {
      required: 'Le nom de l\'agent est requis',
      minlength: 'Le nom doit contenir au moins 3 caractères',
      maxlength: 'Le nom ne peut pas dépasser 50 caractères'
    },
    model_type: {
      required: 'Le type de modèle est requis'
    }
  };

  constructor(
    private fb: FormBuilder,
    private agentService: AgentService
  ) {
    this.formulaireAgent = this.fb.group({
      name: ['', [Validators.required, Validators.minLength(3), Validators.maxLength(50)]],
      model_type: ['codellama', [Validators.required]],
      config: this.fb.group({
        role: ['assistant', Validators.required],
        personality: ['', Validators.maxLength(200)]
      })
    });
  }

  onSubmit(): void {
    if (this.formulaireAgent.invalid) {
      Object.keys(this.formulaireAgent.controls).forEach(key => {
        const control = this.formulaireAgent.get(key);
        control?.markAsTouched();
        control?.markAsDirty();
      });
      return;
    }

    this.enChargement = true;
    this.erreurMessage = '';
    this.succesMessage = '';

    // Ici, model_type est correctement inclus dans les données envoyées
    const agentData: AgentCreateDTO = this.formulaireAgent.value;

    this.agentService.createAgent(agentData).subscribe({
      next: (response) => {
        this.enChargement = false;
        this.succesMessage = `Agent "${response.name}" créé avec succès!`;
        this.formulaireAgent.reset({
          model_type: 'codellama',
          config: {
            role: 'assistant'
          }
        });
        this.agentCreated.emit();
      },
      error: (error) => {
        this.enChargement = false;
        this.erreurMessage = error.error?.detail || 'Erreur lors de la création de l\'agent';
      }
    });
  }
}