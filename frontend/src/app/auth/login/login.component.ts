// src/app/auth/login/login.component.ts
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { NotificationService } from '../../core/services/notification.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent implements OnInit {
  loginForm!: FormGroup;
  loading = false;
  returnUrl: string = '/';

  constructor(
    private fb: FormBuilder,
    private route: ActivatedRoute,
    private router: Router,
    private authService: AuthService,
    private notificationService: NotificationService
  ) {}
  
  ngOnInit(): void {
    // Rediriger vers l'accueil si déjà connecté
    if (this.authService.isAuthenticated()) {
      this.router.navigate(['/']);
      return;
    }

    // Initialiser le formulaire
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', Validators.required],
      rememberMe: [false]
    });

    // Récupérer l'URL de retour des paramètres ou utiliser l'accueil par défaut
    this.returnUrl = this.route.snapshot.queryParams['returnUrl'] || '/';
  }

  // Getter pour un accès facile aux contrôles du formulaire
  get f() { return this.loginForm.controls; }

  onSubmit(): void {
    // Arrêter ici si le formulaire est invalide
    if (this.loginForm.invalid) {
      Object.keys(this.f).forEach(key => {
        const control = this.f[key];
        if (control.invalid) {
          control.markAsTouched();
        }
      });
      return;
    }

    this.loading = true;
    const { email, password } = this.loginForm.value;

    this.authService.login(email, password)
      .subscribe({
        next: (user) => {
          this.notificationService.success(
            'Connexion réussie', 
            `Bienvenue, ${user.firstName || user.username} !`
          );
          this.router.navigate([this.returnUrl]);
        },
        error: error => {
          this.notificationService.error('Échec de la connexion', error.message);
          this.loading = false;
        }
      });
  }
}