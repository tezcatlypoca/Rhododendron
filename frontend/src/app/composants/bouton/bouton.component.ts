// src/app/composants/bouton/bouton.component.ts
import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';

/**
 * Composant bouton réutilisable
 * Supporte différents types et états
 */
@Component({
  selector: 'app-bouton',
  templateUrl: './bouton.component.html',
  styleUrls: ['./bouton.component.scss'],
  standalone: true,
  imports: [CommonModule]
})
export class BoutonComponent {
  @Input() texte: string = '';
  @Input() type: 'button' | 'submit' | 'reset' = 'button';
  @Input() variante: 'primaire' | 'secondaire' | 'tertiaire' = 'primaire';
  @Input() desactive: boolean = false;
  @Input() chargement: boolean = false;
  @Output() clic = new EventEmitter<Event>();

  /**
   * Gère l'événement de clic
   */
  onClick(event: Event): void {
    if (!this.desactive && !this.chargement) {
      this.clic.emit(event);
    }
  }
}