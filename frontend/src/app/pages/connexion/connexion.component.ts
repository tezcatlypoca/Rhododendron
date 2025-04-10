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
    // Si déjà connecté, rediriger vers le tableau de bord
    if (this.authService.estConnecte()) {
      this.router.navigate(['/dashboard']);
    }
  }

  /**
   * Soumission du formulaire de connexion
   */
  onSubmit(): void {
    if (this.formulaireConnexion.invalid) {
      // Marquer tous les champs comme touchés pour afficher les erreurs
      Object.keys(this.formulaireConnexion.controls).forEach(key => {
        const control = this.formulaireConnexion.get(key);
        control?.markAsTouched();
        control?.markAsDirty();
      });
      return;
    }

    this.enChargement = true;
    this.erreurMessage = '';

    this.authService.connexion(this.formulaireConnexion.value).subscribe({
      next: () => {
        this.enChargement = false;
        
        // Attendre un court instant pour s'assurer que l'état est mis à jour
        setTimeout(() => {
          this.router.navigate(['/dashboard']).then(() => {
            // Forcer un rafraîchissement des données utilisateur après navigation
            this.authService.chargerProfilUtilisateur().subscribe();
          });
        }, 100);
      },
      error: (erreur) => {
        this.enChargement = false;
        this.erreurMessage = erreur.message || 'Erreur de connexion';
      }
    });
  }
}