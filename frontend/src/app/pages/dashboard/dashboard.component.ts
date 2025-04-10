// src/app/pages/dashboard/dashboard.component.ts
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth.service';
import { Utilisateur } from '../../modeles/auth.model';

/**
 * Page principale du tableau de bord
 */
@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss'],
  standalone: true,
  imports: [
    CommonModule
  ]
})
export class DashboardComponent implements OnInit {
  utilisateur: Utilisateur | null = null;
  enChargement: boolean = true;
  
  constructor(private authService: AuthService) {}
  
  ngOnInit(): void {
    this.chargerInformationsUtilisateur();
  }
  
  /**
   * Charge les informations de l'utilisateur connecté
   */
  chargerInformationsUtilisateur(): void {
    this.authService.utilisateur$.subscribe(utilisateur => {
      this.utilisateur = utilisateur;
      this.enChargement = false;
    });
  }
}