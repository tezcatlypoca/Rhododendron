// src/app/pages/agent-edition/agent-edition.component.ts
import { Component, OnInit, OnDestroy } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule, AbstractControl } from '@angular/forms';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';
import { Subscription, switchMap } from 'rxjs';

import { AgentService } from '../../services/agent.service';
import { Agent, AgentUpdateDTO } from '../../modeles/agent.model';
import { ChampFormulaireComponent } from '../../composants/champ-formulaire/champ-formulaire.component';
import { BoutonComponent } from '../../composants/bouton/bouton.component';

@Component({
  selector: 'app-agent-edition',
  templateUrl: './agent-edition.component.html',
  styleUrls: ['./agent-edition.component.scss'],
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterModule,
    ChampFormulaireComponent,
    BoutonComponent
  ]
})
export class AgentEditionComponent implements OnInit, OnDestroy {
  formulaireAgent: FormGroup;
  agent: Agent | null = null;
  agentId: string = '';
  enChargement: boolean = true;
  enSauvegarde: boolean = false;
  erreurMessage: string = '';
  succesMessage: string = '';
  
  // Liste des modèles disponibles
  modelTypes: string[] = ['codellama', 'llama3', 'autre-modele'];
  
  // Messages d'erreur pour les validations
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
  
  private subscriptions = new Subscription();

  constructor(
    private fb: FormBuilder,
    private agentService: AgentService,
    private route: ActivatedRoute,
    private router: Router
  ) {
    // Initialisation du formulaire (sera rempli avec les données de l'agent plus tard)
    this.formulaireAgent = this.fb.group({
      name: ['', [Validators.required, Validators.minLength(3), Validators.maxLength(50)]],
      model_type: ['', [Validators.required]],
      is_active: [true],
      config: this.fb.group({
        role: ['assistant', Validators.required],
        personality: ['', Validators.maxLength(200)],
        temperature: [0.7, [Validators.required, Validators.min(0), Validators.max(1)]],
        max_tokens: [1024, [Validators.required, Validators.min(1), Validators.max(4096)]],
        context_window: [4096, [Validators.required, Validators.min(512), Validators.max(8192)]],
        context_strategy: ['recency', Validators.required]
      })
    });
  }

  ngOnInit(): void {
    // Récupérer l'ID de l'agent depuis l'URL et charger ses données
    const routeSub = this.route.paramMap.pipe(
      switchMap(params => {
        this.agentId = params.get('id') || '';
        if (!this.agentId) {
          throw new Error('ID d\'agent non spécifié');
        }
        return this.agentService.getAgentById(this.agentId);
      })
    ).subscribe({
      next: (agent) => {
        this.agent = agent;
        this.initialiserFormulaire(agent);
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
   * Initialise le formulaire avec les données de l'agent
   */
  initialiserFormulaire(agent: Agent): void {
    // Pour éviter les erreurs si certaines configurations n'existent pas
    const config = agent.config || {};
    
    this.formulaireAgent.patchValue({
      name: agent.name,
      model_type: agent.model_type,
      is_active: agent.is_active,
      config: {
        role: config['role'] || 'assistant',
        personality: config['personality'] || '',
        temperature: config['temperature'] !== undefined ? config['temperature'] : 0.7,
        max_tokens: config['max_tokens'] || 1024,
        context_window: config['context_window'] || 4096,
        context_strategy: config['context_strategy'] || 'recency'
      }
    });
  }

  /**
   * Soumission du formulaire pour mettre à jour l'agent
   */
  onSubmit(): void {
    if (this.formulaireAgent.invalid) {
      // Marquer tous les champs comme touchés pour afficher les erreurs
      Object.keys(this.formulaireAgent.controls).forEach(key => {
        const control = this.formulaireAgent.get(key);
        if (control) {
          control.markAsTouched();
          control.markAsDirty();
        }
      });
      
      // Marquer également les contrôles dans le groupe config
      const configGroup = this.formulaireAgent.get('config');
      if (configGroup) {
        Object.keys((configGroup as any).controls).forEach(key => {
          const control = configGroup.get(key);
          if (control) {
            control.markAsTouched();
            control.markAsDirty();
          }
        });
      }
      
      return;
    }

    this.enSauvegarde = true;
    this.erreurMessage = '';
    this.succesMessage = '';

    const agentData: AgentUpdateDTO = this.formulaireAgent.value;

    this.agentService.updateAgent(this.agentId, agentData).subscribe({
      next: (response) => {
        this.enSauvegarde = false;
        this.succesMessage = `Agent "${response.name}" mis à jour avec succès!`;
        this.agent = response;
        // Mettre à jour le formulaire avec les données actualisées
        this.initialiserFormulaire(response);
      },
      error: (error) => {
        this.enSauvegarde = false;
        this.erreurMessage = error.error?.detail || 'Erreur lors de la mise à jour de l\'agent';
        console.error('Erreur lors de la mise à jour:', error);
      }
    });
  }

  /**
   * Retourne à la liste des agents
   */
  retourListe(): void {
    this.router.navigate(['/agents']);
  }
}