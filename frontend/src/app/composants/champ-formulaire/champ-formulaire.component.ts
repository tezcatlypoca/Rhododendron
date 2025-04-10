// src/app/composants/champ-formulaire/champ-formulaire.component.ts
import { Component, Input, forwardRef } from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR, AbstractControl, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

/**
 * Composant réutilisable pour les champs de formulaire
 * Gère l'affichage des erreurs et l'état du champ
 */
@Component({
  selector: 'app-champ-formulaire',
  templateUrl: './champ-formulaire.component.html',
  styleUrls: ['./champ-formulaire.component.scss'],
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => ChampFormulaireComponent),
      multi: true
    }
  ]
})
export class ChampFormulaireComponent implements ControlValueAccessor {
  @Input() label: string = '';
  @Input() type: string = 'text';
  @Input() placeholder: string = '';
  @Input() control!: AbstractControl;
  @Input() erreurMessages: { [key: string]: string } = {};
  
  value: any = '';
  onChange: any = () => {};
  onTouched: any = () => {};
  disabled: boolean = false;

  /**
   * Écrit une nouvelle valeur dans le champ
   */
  writeValue(value: any): void {
    this.value = value;
  }

  /**
   * Enregistre la fonction de changement
   */
  registerOnChange(fn: any): void {
    this.onChange = fn;
  }

  /**
   * Enregistre la fonction de toucher
   */
  registerOnTouched(fn: any): void {
    this.onTouched = fn;
  }

  /**
   * Active ou désactive le champ
   */
  setDisabledState(isDisabled: boolean): void {
    this.disabled = isDisabled;
  }

  /**
   * Gère le changement de valeur
   */
  onValueChange(event: Event): void {
    const value = (event.target as HTMLInputElement).value;
    this.value = value;
    this.onChange(value);
    
    // Mettre à jour le contrôle si il existe
    if (this.control) {
      this.control.setValue(value, { emitEvent: false });
    }
  }

  /**
   * Marque le champ comme touché
   */
  onBlur(): void {
    this.onTouched();
    if (this.control) {
      this.control.markAsTouched();
      this.control.updateValueAndValidity();
    }
  }

  /**
   * Vérifie si le champ a des erreurs et a été touché
   */
  get aDesErreurs(): boolean {
    return this.control && this.control.invalid && this.control.touched;
  }

  /**
   * Obtient les messages d'erreur pour le champ
   */
  get messagesErreur(): string[] {
    if (!this.control?.errors) {
      return [];
    }
    
    return Object.keys(this.control.errors)
      .filter(key => this.erreurMessages[key])
      .map(key => this.erreurMessages[key]);
  }
  
  /**
   * Détermine l'attribut autocomplete approprié en fonction du type de champ
   */
  getAutocompleteAttribute(): string {
    switch (this.type) {
      case 'password':
        return 'current-password';
      case 'email':
        return 'email';
      case 'text':
        if (this.label.toLowerCase().includes('utilisateur') || this.label.toLowerCase().includes('username')) {
          return 'username';
        }
        return 'off';
      default:
        return 'off';
    }
  }
}