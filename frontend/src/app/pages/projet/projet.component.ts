import { Component } from '@angular/core';
import { ProjetService } from '../../services/projet.service';
import { ProjetCreate } from '../../models/projet.model';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-projet',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './projet.component.html',
  styleUrl: './projet.component.scss'
})
export class ProjetComponent {
  projet: ProjetCreate = {
    nom: '',
    description: ''
  };

  constructor(
    private projetService: ProjetService,
    private router: Router
  ) {}

  onSubmit() {
    this.projetService.createProjet(this.projet).subscribe({
      next: (projet) => {
        console.log('Projet créé avec succès:', projet);
        this.router.navigate(['/projets']);
      },
      error: (error) => {
        console.error('Erreur lors de la création du projet:', error);
      }
    });
  }
}
