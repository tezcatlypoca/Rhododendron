import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { OrchestreGalerieComponent, Orchestre } from '../orchestre_cards';
import { OrchestreService } from '../core/services/orchestre.service';

@Component({
  selector: 'app-accueil',
  standalone: true,
  imports: [CommonModule, OrchestreGalerieComponent],
  templateUrl: './accueil.component.html',
  styleUrls: ['./accueil.component.scss']
})
export class AccueilComponent implements OnInit {
  orchestres: Orchestre[] = [];
  isLoading = true;
  error: string | null = null;

  constructor(
    private orchestreService: OrchestreService,
    private router: Router
  ) { }

  ngOnInit(): void {
    this.orchestreService.getAllOrchestres().subscribe({
      next: (data) => {
        this.orchestres = data;
        this.isLoading = false;
        console.log('Orchestres chargés:', this.orchestres); // Pour le debug
      },
      error: (err) => {
        this.error = 'Erreur lors du chargement des orchestres';
        this.isLoading = false;
        console.error('Erreur lors du chargement des orchestres:', err);
        // Initialiser avec un tableau vide en cas d'erreur
        this.orchestres = [];
      }
    });
  }

  handleOuvrirOrchestre(id: number): void {
    console.log(`Ouvrir l'orchestre ${id}`);
    this.router.navigate(['/orchestre', id]);
  }

  handleConfigurerOrchestre(id: number): void {
    console.log(`Configurer l'orchestre ${id}`);
    this.router.navigate(['/orchestre', id, 'configurer']);
  }

  creerNouvelOrchestre(): void {
    console.log('Création d\'un nouvel orchestre');
    this.router.navigate(['/nouvelle-orchestre']);
  }
}