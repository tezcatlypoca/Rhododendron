import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Orchestre, Instrument } from '../models';

@Component({
  selector: 'app-orchestre-card',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './orchestre-card.component.html',
  styleUrls: ['./orchestre-card.component.scss']
})
export class OrchestreCardComponent {
  @Input() orchestre?: Orchestre; // Changé de ! à ?
  @Output() ouvrirOrchestre = new EventEmitter<number>();
  @Output() configurerOrchestre = new EventEmitter<number>();

  getPreviewInstruments(): Instrument[] {
    if (!this.orchestre || !this.orchestre.instruments) {
      return [];
    }
    return this.orchestre.instruments.slice(0, 3);
  }

  getProjectsCount(): number {
    if (!this.orchestre || !this.orchestre.projets) {
      return 0;
    }
    return this.orchestre.projets.length;
  }
  getMoreInstrumentsCount(): number {
    if (!this.orchestre || !this.orchestre.instruments) {
      return 0;
    }
    return this.orchestre.instruments.length - 3;
  }

  hasMoreInstruments(): boolean {
    return !!this.orchestre?.instruments && this.orchestre.instruments.length > 3;
  }

  onOuvrirClick(): void {
    if (this.orchestre) {
      this.ouvrirOrchestre.emit(this.orchestre.id);
    }
  }

  onConfigurerClick(): void {
    if (this.orchestre) {
      this.configurerOrchestre.emit(this.orchestre.id);
    }
  }
}