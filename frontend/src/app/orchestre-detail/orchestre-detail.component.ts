import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { OrchestreService } from '../core/services/orchestre.service';
import { Orchestre, Instrument, Projet } from '../orchestre_cards/models';

@Component({
  selector: 'app-orchestre-detail',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './orchestre-detail.component.html',
  styleUrls: ['./orchestre-detail.component.scss']
})
export class OrchestreDetailComponent implements OnInit {
  orchestre?: Orchestre;
  isLoading = true;
  error: string | null = null;
  activeTab: 'instruments' | 'projets' = 'instruments';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private orchestreService: OrchestreService
  ) {}

  ngOnInit(): void {
    // Récupération de l'ID depuis l'URL
    this.route.paramMap.subscribe(params => {
      const id = Number(params.get('id'));
      if (isNaN(id)) {
        this.error = 'ID d\'orchestre invalide';
        this.isLoading = false;
        return;
      }

      this.loadOrchestre(id);
    });
  }

  loadOrchestre(id: number): void {
    this.orchestreService.getOrchestreById(id).subscribe({
      next: (data) => {
        this.orchestre = data;
        this.isLoading = false;
      },
      error: (err) => {
        this.error = 'Erreur lors du chargement de l\'orchestre';
        this.isLoading = false;
        console.error('Erreur:', err);
      }
    });
  }

  setActiveTab(tab: 'instruments' | 'projets'): void {
    this.activeTab = tab;
  }

  navigateToEdit(): void {
    if (this.orchestre) {
      this.router.navigate(['/orchestre', this.orchestre.id, 'configurer']);
    }
  }

  navigateBack(): void {
    this.router.navigate(['/']);
  }
}