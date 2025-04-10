// src/app/pages/profil/profil.component.ts
import { Component, OnInit } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { CommonModule, DatePipe } from '@angular/common';
import { AuthService } from '../../services/auth.service';
import { Utilisateur } from '../../modeles/auth.model';

/**
 * Page de profil utilisateur
 * Affiche les informations de l'utilisateur connecté
 */
@Component({
  selector: 'app-profil',
  templateUrl: './profil.component.html',
  styleUrls: ['./profil.component.scss'],
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    DatePipe
  ]
})
export class ProfilComponent implements OnInit {
  utilisateur: Utilisateur | null = null;
  chargement: boolean = true;
  erreur: string = '';

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.chargerUtilisateur();
  }

  /**
   * Charge les informations de l'utilisateur
   */
  chargerUtilisateur(): void {
    this.chargement = true;
    this.erreur = '';

    this.authService.chargerProfilUtilisateur().subscribe({
      next: (utilisateur) => {
        this.utilisateur = utilisateur;
        this.chargement = false;
      },
      error: (erreur) => {
        this.erreur = 'Impossible de charger les informations utilisateur';
        this.chargement = false;
        console.error('Erreur de chargement du profil:', erreur);
      }
    });
  }

  /**
   * Déconnecte l'utilisateur
   */
  deconnexion(): void {
    this.authService.deconnexion();
    this.router.navigate(['/connexion']);
  }
}