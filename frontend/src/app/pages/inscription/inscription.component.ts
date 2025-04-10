// src/app/pages/inscription/inscription.component.ts
import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth.service';
import { ChampFormulaireComponent } from '../../composants/champ-formulaire/champ-formulaire.component';
import { BoutonComponent } from '../../composants/bouton/bouton.component';

/**
 * Page d'inscription
 */
@Component({
  selector: 'app-inscription',
  templateUrl: './inscription.component.html',
  styleUrls: ['./inscription.component.scss'],
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterLink,
    ChampFormulaireComponent,
    BoutonComponent
  ]
})
export class InscriptionComponent implements OnInit {
  formulaireInscription: FormGroup;
  erreurMessage: string = '';
  enChargement: boolean = false;
  
  // Messages d'erreur pour les validations
  messagesErreur = {
    username: {
      required: 'Le nom d\'utilisateur est requis',
      minlength: 'Le nom d\'utilisateur doit contenir au moins 3 caractères',
      maxlength: 'Le nom d\'utilisateur ne peut pas dépasser 50 caractères'
    },
    email: {
      required: 'L\'email est requis',
      email: 'Veuillez entrer une adresse email valide'
    },
    password: {
      required: 'Le mot de passe est requis',
      minlength: 'Le mot de passe doit contenir au moins 8 caractères'
    }
  };

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {
    this.formulaireInscription = this.fb.group({
      username: ['', [Validators.required, Validators.minLength(3), Validators.maxLength(50)]],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(8)]]
    });
  }

  ngOnInit(): void {
    // Si déjà connecté, rediriger vers la page d'accueil
    if (this.authService.estConnecte()) {
      this.router.navigate(['/profil']);
    }
  }

  /**
   * Soumission du formulaire d'inscription
   */
  onSubmit(): void {
    console.log('Formulaire soumis:', this.formulaireInscription.value);
    console.log('État du formulaire:', {
      valid: this.formulaireInscription.valid, 
      errors: this.formulaireInscription.errors,
      dirty: this.formulaireInscription.dirty,
      touched: this.formulaireInscription.touched,
      values: this.formulaireInscription.value
    });
    
    // Afficher l'état de chaque contrôle pour le débogage
    Object.keys(this.formulaireInscription.controls).forEach(key => {
      const control = this.formulaireInscription.get(key);
      console.log(`Contrôle ${key}:`, {
        valid: control?.valid,
        errors: control?.errors,
        value: control?.value,
        dirty: control?.dirty,
        touched: control?.touched
      });
    });

    if (this.formulaireInscription.invalid) {
      // Marquer tous les champs comme touchés pour afficher les erreurs
      Object.keys(this.formulaireInscription.controls).forEach(key => {
        const control = this.formulaireInscription.get(key);
        control?.markAsTouched();
        control?.markAsDirty(); // Ajouter ceci pour s'assurer que les contrôles sont marqués comme modifiés
      });
      return;
    }

    this.enChargement = true;
    this.erreurMessage = '';

    this.authService.inscription(this.formulaireInscription.value).subscribe({
      next: () => {
        this.enChargement = false;
        // Rediriger vers la page de connexion après inscription réussie
        this.router.navigate(['/connexion'], { 
          queryParams: { registered: 'success' } 
        });
      },
      error: (erreur) => {
        this.enChargement = false;
        this.erreurMessage = erreur.message || 'Erreur lors de l\'inscription';
      }
    });
  }
}