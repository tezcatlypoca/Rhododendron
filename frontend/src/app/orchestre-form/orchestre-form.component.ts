// src/app/orchestre-form/orchestre-form.component.ts
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, FormArray, Validators, ReactiveFormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { OrchestreService } from '../core/services/orchestre.service';
import { NotificationService } from '../core/services/notification.service';
import { Orchestre, Instrument, Projet } from '../orchestre_cards/models';

@Component({
  selector: 'app-orchestre-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './orchestre-form.component.html',
  styleUrls: ['./orchestre-form.component.scss']
})
export class OrchestreFormComponent implements OnInit {
  orchestreForm!: FormGroup;
  isEditMode = false;
  orchestreId: number | null = null;
  isLoading = true;
  error: string | null = null;
  submitInProgress = false;

  specialites = ['Développement', 'Communication', 'Analyse', 'Autre'];

  constructor(
    private fb: FormBuilder,
    private orchestreService: OrchestreService,
    private route: ActivatedRoute,
    private router: Router,
    private notificationService: NotificationService // Ajouté ici
  ) {}

  ngOnInit(): void {
    this.initForm();

    // Déterminer si nous sommes en mode édition en vérifiant la route
    this.route.paramMap.subscribe(params => {
      const id = params.get('id');
      if (id) {
        this.isEditMode = true;
        this.orchestreId = Number(id);
        this.loadOrchestre(this.orchestreId);
      } else {
        this.isLoading = false;
      }
    });
  }

  private initForm(): void {
    this.orchestreForm = this.fb.group({
      nom: ['', [Validators.required, Validators.minLength(3)]],
      specialite: ['Développement', Validators.required],
      instruments: this.fb.array([]),
      projets: this.fb.array([])
    });
  }

  private loadOrchestre(id: number): void {
    this.orchestreService.getOrchestreById(id).subscribe({
      next: (orchestre) => {
        this.patchFormWithOrchestre(orchestre);
        this.isLoading = false;
      },
      error: (err) => {
        this.error = 'Erreur lors du chargement de l\'orchestre';
        this.isLoading = false;
        this.notificationService.error('Erreur de chargement', 'Impossible de charger les données de l\'orchestre');
        console.error('Erreur:', err);
      }
    });
  }

  private patchFormWithOrchestre(orchestre: Orchestre): void {
    // Mise à jour des champs de base
    this.orchestreForm.patchValue({
      nom: orchestre.nom,
      specialite: orchestre.specialite
    });

    // Chargement des instruments
    if (orchestre.instruments && orchestre.instruments.length > 0) {
      const instrumentsArray = this.orchestreForm.get('instruments') as FormArray;
      instrumentsArray.clear(); // Nettoyer le tableau avant d'ajouter

      orchestre.instruments.forEach(instrument => {
        instrumentsArray.push(this.createInstrumentFormGroup(instrument));
      });
    }

    // Chargement des projets
    if (orchestre.projets && orchestre.projets.length > 0) {
      const projetsArray = this.orchestreForm.get('projets') as FormArray;
      projetsArray.clear(); // Nettoyer le tableau avant d'ajouter

      orchestre.projets.forEach(projet => {
        projetsArray.push(this.createProjetFormGroup(projet));
      });
    }
  }

  // Création d'un FormGroup pour un instrument
  private createInstrumentFormGroup(instrument?: Instrument): FormGroup {
    return this.fb.group({
      id: [instrument?.id],
      nom: [instrument?.nom || '', [Validators.required, Validators.minLength(2)]],
      role: [instrument?.role || '', Validators.required],
      specificites: [instrument?.specificites?.join(', ') || ''],
      capacites: this.fb.array(
        instrument?.capacites?.map(cap => this.createCapaciteFormGroup(cap)) || []
      )
    });
  }

  // Création d'un FormGroup pour une capacité
  private createCapaciteFormGroup(capacite?: { nom: string, niveau: number }): FormGroup {
    return this.fb.group({
      nom: [capacite?.nom || '', Validators.required],
      niveau: [capacite?.niveau || 3, [Validators.required, Validators.min(1), Validators.max(5)]]
    });
  }

  // Création d'un FormGroup pour un projet
  private createProjetFormGroup(projet?: Projet): FormGroup {
    return this.fb.group({
      id: [projet?.id],
      nom: [projet?.nom || '', [Validators.required, Validators.minLength(2)]],
      type: [projet?.type || '', Validators.required],
      description: [projet?.description || '']
    });
  }

  // Getters pour accéder aux FormArrays
  get instrumentsArray(): FormArray {
    return this.orchestreForm.get('instruments') as FormArray;
  }

  get projetsArray(): FormArray {
    return this.orchestreForm.get('projets') as FormArray;
  }

  // Méthodes pour ajouter des éléments aux FormArrays
  addInstrument(): void {
    this.instrumentsArray.push(this.createInstrumentFormGroup());
    this.notificationService.info('Instrument ajouté', 'Complétez les informations pour ce nouvel instrument');
  }

  removeInstrument(index: number): void {
    this.instrumentsArray.removeAt(index);
    this.notificationService.warning('Instrument supprimé');
  }

  addCapacite(instrumentIndex: number): void {
    const capacites = this.instrumentsArray.at(instrumentIndex).get('capacites') as FormArray;
    capacites.push(this.createCapaciteFormGroup());
  }

  removeCapacite(instrumentIndex: number, capaciteIndex: number): void {
    const capacites = this.instrumentsArray.at(instrumentIndex).get('capacites') as FormArray;
    capacites.removeAt(capaciteIndex);
  }

  addProjet(): void {
    this.projetsArray.push(this.createProjetFormGroup());
    this.notificationService.info('Projet ajouté', 'Complétez les informations pour ce nouveau projet');
  }

  removeProjet(index: number): void {
    this.projetsArray.removeAt(index);
    this.notificationService.warning('Projet supprimé');
  }

  // Préparation du modèle Orchestre à partir du formulaire
  private prepareOrchestreModel(): Partial<Orchestre> {
    const formValue = this.orchestreForm.value;
    
    // Transformation des instruments
    const instruments = formValue.instruments?.map((instrument: any) => {
      // Transformation des specificites de chaîne à tableau
      const specificites = instrument.specificites
        ? instrument.specificites.split(',').map((s: string) => s.trim()).filter(Boolean)
        : [];
        
      return {
        ...instrument,
        specificites
      };
    }) || [];
    
    // Construction du modèle d'orchestre
    const orchestre: Partial<Orchestre> = {
      nom: formValue.nom || '',
      specialite: formValue.specialite || 'Développement',
      instruments: instruments,
      projets: formValue.projets || []
    };
    
    // Si en mode édition, ajouter l'ID
    if (this.isEditMode && this.orchestreId) {
      orchestre.id = this.orchestreId;
    }
    
    return orchestre;
  }

  // Soumission du formulaire
  onSubmit(): void {
    if (this.orchestreForm.invalid) {
      // Vérifier les erreurs et les afficher via le service de notification
      const errors: { [key: string]: string } = {};
      
      // Vérification du nom
      const nomControl = this.orchestreForm.get('nom');
      if (nomControl?.errors?.['required']) {
        errors['nom'] = 'Le nom de l\'orchestre est requis';
      } else if (nomControl?.errors?.['minlength']) {
        errors['nom'] = 'Le nom doit contenir au moins 3 caractères';
      }
      
      // Vérifier les instruments
      this.instrumentsArray.controls.forEach((control, index) => {
        if (control.get('nom')?.errors?.['required']) {
          errors[`instrument${index}`] = `Le nom de l'instrument #${index + 1} est requis`;
        }
        if (control.get('role')?.errors?.['required']) {
          errors[`instrument_role${index}`] = `Le rôle de l'instrument #${index + 1} est requis`;
        }
      });
      
      // Vérifier les projets
      this.projetsArray.controls.forEach((control, index) => {
        if (control.get('nom')?.errors?.['required']) {
          errors[`projet${index}`] = `Le nom du projet #${index + 1} est requis`;
        }
        if (control.get('type')?.errors?.['required']) {
          errors[`projet_type${index}`] = `Le type du projet #${index + 1} est requis`;
        }
      });
      
      // Afficher les erreurs
      this.notificationService.formValidationError(errors);
      
      // Marquer tous les contrôles comme touchés pour afficher les erreurs visuellement
      this.orchestreForm.markAllAsTouched();
      return;
    }

    this.submitInProgress = true;
    const orchestreModel = this.prepareOrchestreModel();

    if (this.isEditMode) {
      // En mode édition, nous avons besoin de l'ID, donc on peut caster vers Orchestre
      this.orchestreService.updateOrchestre(orchestreModel as Orchestre).subscribe({
        next: (result) => {
          this.submitInProgress = false;
          this.notificationService.success(
            'Orchestre mis à jour avec succès',
            `L'orchestre "${result.nom}" a été mis à jour`
          );
          this.router.navigate(['/orchestre', result.id]);
        },
        error: (err) => {
          this.submitInProgress = false;
          this.notificationService.error(
            'Erreur lors de la mise à jour',
            err.message || 'Une erreur inattendue est survenue'
          );
          console.error('Erreur:', err);
        }
      });
    } else {
      // En mode création, nous devons nous assurer que toutes les propriétés requises sont présentes
      const newOrchestre: Omit<Orchestre, 'id'> = {
        nom: orchestreModel.nom || '',
        specialite: orchestreModel.specialite || 'Développement',
        instruments: orchestreModel.instruments || [],
        dateCreation: new Date(),
        projets: orchestreModel.projets || []
      };
      
      this.orchestreService.addOrchestre(newOrchestre).subscribe({
        next: (result) => {
          this.submitInProgress = false;
          this.notificationService.success(
            'Orchestre créé avec succès',
            `L'orchestre "${result.nom}" a été créé`
          );
          this.router.navigate(['/orchestre', result.id]);
        },
        error: (err) => {
          this.submitInProgress = false;
          this.notificationService.error(
            'Erreur lors de la création',
            err.message || 'Une erreur inattendue est survenue'
          );
          console.error('Erreur:', err);
        }
      });
    }
  }

  // Navigation
  cancel(): void {
    if (this.isEditMode && this.orchestreId) {
      this.notificationService.info('Modifications annulées');
      this.router.navigate(['/orchestre', this.orchestreId]);
    } else {
      this.notificationService.info('Création annulée');
      this.router.navigate(['/']);
    }
  }

  // Utilitaires pour les templates
  getCapacitesArray(instrumentIndex: number): FormArray {
    return this.instrumentsArray.at(instrumentIndex).get('capacites') as FormArray;
  }

  // Vérification d'erreur de validation
  hasError(controlName: string, errorType: string): boolean {
    const control = this.orchestreForm.get(controlName);
    return control?.touched === true && control?.hasError(errorType) === true;
  }
}