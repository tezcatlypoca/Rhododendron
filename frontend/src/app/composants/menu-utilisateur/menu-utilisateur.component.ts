// src/app/composants/menu-utilisateur/menu-utilisateur.component.ts
import { Component, Input, OnInit, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { Utilisateur } from '../../modeles/auth.model';

@Component({
  selector: 'app-menu-utilisateur',
  templateUrl: './menu-utilisateur.component.html',
  styleUrls: ['./menu-utilisateur.component.scss'],
  standalone: true,
  imports: [CommonModule, RouterLink]
})
export class MenuUtilisateurComponent implements OnInit {
  @Input() utilisateur: Utilisateur | null = null;
  menuOuvert: boolean = false;

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {}

  /**
   * Ouvre ou ferme le menu déroulant
   */
  toggleMenu(): void {
    this.menuOuvert = !this.menuOuvert;
  }

  /**
   * Déconnecte l'utilisateur
   */
  deconnexion(): void {
    this.menuOuvert = false; // Ferme le menu
    this.authService.deconnexion();
    this.router.navigate(['/connexion']);
  }

  /**
   * Gère les clics sur le document pour fermer le menu
   */
  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent): void {
    // Vérifier si le clic est à l'extérieur du composant
    const target = event.target as HTMLElement;
    const clickedInside = target.closest('.utilisateur-menu');
    
    if (!clickedInside && this.menuOuvert) {
      this.menuOuvert = false;
    }
  }
}