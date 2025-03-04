import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { OrchestreCardComponent } from '../orchestre-card/orchestre-card.component';
import { Orchestre } from '../models';

@Component({
  selector: 'app-orchestre-galerie',
  standalone: true,
  imports: [CommonModule, OrchestreCardComponent],
  templateUrl: './orchestre-galerie.component.html',
  styleUrls: ['./orchestre-galerie.component.scss']
})
export class OrchestreGalerieComponent {
  @Input() orchestres: Orchestre[] = [];
  @Output() ouvrirOrchestre = new EventEmitter<number>();
  @Output() configurerOrchestre = new EventEmitter<number>();
  @Output() creerOrchestre = new EventEmitter<void>();

  handleOuvrirOrchestre(id: number): void {
    this.ouvrirOrchestre.emit(id);
  }

  handleConfigurerOrchestre(id: number): void {
    this.configurerOrchestre.emit(id);
  }

  handleCreerOrchestre(): void {
    this.creerOrchestre.emit();
  }
}