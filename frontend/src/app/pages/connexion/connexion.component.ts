// src/app/pages/connexion/connexion.component.ts
import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth.service';
import { ChampFormulaireComponent } from '../../composants/champ-formulaire/champ-formulaire.component';
import { BoutonComponent } from '../../composants/bouton/bouton.component';

/**
 * Page de connexion
 */
@Component({
  selector: 'app-connexion',
  templateUrl: './connexion.component.html',
  styleUrls: ['./connexion.component.scss'],
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterLink,
    ChampFormulaireComponent,
    BoutonComponent
  ]
})
export class ConnexionComponent implements OnInit {
  formulaireConnexion: FormGroup;
  erreurMessage: string = '';
  enChargement: boolean = false;
  
  // Messages d'erreur pour les validations
  messagesErreur = {
    username: {
      required: 'L\'identifiant est requis'
    },
    password: {
      required: 'Le mot de passe est requis'
    }
  };

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {
    this.formulaireConnexion = this.fb.group({
      username: ['', [Validators.required]],
      password: ['', [Validators.required]]
    });
  }

  ngOnInit(): void {
    // Si déjà connecté, rediriger vers la page d'accueil
    if (this.authService.estConnecte()) {
      this.router.navigate(['/profil']);
    }
  }

  /**
   * Soumission du formulaire de connexion
   */
  onSubmit(): void {
    console.log('Formulaire soumis:', this.formulaireConnexion.value);
    console.log('État du formulaire:', {
      valid: this.formulaireConnexion.valid, 
      errors: this.formulaireConnexion.errors,
      dirty: this.formulaireConnexion.dirty,
      touched: this.formulaireConnexion.touched
    });
    
    // Afficher l'état de chaque contrôle pour le débogage
    Object.keys(this.formulaireConnexion.controls).forEach(key => {
      const control = this.formulaireConnexion.get(key);
      console.log(`Contrôle ${key}:`, {
        valid: control?.valid,
        errors: control?.errors,
        value: control?.value,
        dirty: control?.dirty,
        touched: control?.touched
      });
    });

    if (this.formulaireConnexion.invalid) {
      // Marquer tous les champs comme touchés pour afficher les erreurs
      Object.keys(this.formulaireConnexion.controls).forEach(key => {
        const control = this.formulaireConnexion.get(key);
        control?.markAsTouched();
        control?.markAsDirty(); // Ajouter ceci pour s'assurer que les contrôles sont marqués comme modifiés
      });
      return;
    }

    this.enChargement = true;
    this.erreurMessage = '';

    this.authService.connexion(this.formulaireConnexion.value).subscribe({
      next: () => {
        this.enChargement = false;
        this.router.navigate(['/profil']);
      },
      error: (erreur) => {
        this.enChargement = false;
        this.erreurMessage = erreur.message || 'Erreur de connexion';
      }
    });
  }
}