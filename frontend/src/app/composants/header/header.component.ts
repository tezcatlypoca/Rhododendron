// src/app/composants/header/header.component.ts
import { Component, Input, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, RouterLinkActive, Router, NavigationEnd } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { Subscription } from 'rxjs';
import { filter } from 'rxjs/operators';
import { MenuUtilisateurComponent } from '../menu-utilisateur/menu-utilisateur.component';

/**
 * Composant de bannière/header réutilisable
 * Affiche la navigation principale et les informations de l'utilisateur connecté
 */
@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss'],
  standalone: true,
  imports: [CommonModule, RouterLink, RouterLinkActive, MenuUtilisateurComponent]
})
export class HeaderComponent implements OnInit, OnDestroy {
  @Input() titre: string = 'Rhododendron';
  estConnecte: boolean = false;
  private subscriptions: Subscription = new Subscription();

  constructor(
    public authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    // S'abonner au changement d'état de l'utilisateur
    const authSub = this.authService.utilisateur$.subscribe(utilisateur => {
      this.estConnecte = !!utilisateur;
    });
    this.subscriptions.add(authSub);

    // S'abonner aux événements de navigation
    const routerSub = this.router.events
      .pipe(filter(event => event instanceof NavigationEnd))
      .subscribe(() => {
        // Vérifier l'authentification après chaque navigation
        this.verifierAuthentification();
      });
    this.subscriptions.add(routerSub);
  }

  ngOnDestroy(): void {
    this.subscriptions.unsubscribe();
  }

  /**
   * Vérifie l'état d'authentification et charge le profil si nécessaire
   */
  verifierAuthentification(): void {
    this.estConnecte = this.authService.estConnecte();
  }
}
