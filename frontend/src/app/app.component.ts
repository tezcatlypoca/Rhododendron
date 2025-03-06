// src/app/app.component.ts
import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { NotificationsComponent } from './shared/notifications/notifications.component';
import { HeaderComponent } from './shared/header/header.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, NotificationsComponent, HeaderComponent],
  template: `
    <app-header></app-header>
    <div class="app-container">
      <app-notifications></app-notifications>
      <main class="app-content">
        <router-outlet></router-outlet>
      </main>
    </div>
  `,
  styles: [`
    .app-container {
      padding-top: 64px; /* Correspond à la hauteur du header */
      min-height: 100vh;
    }
    
    .app-content {
      max-width: 1200px;
      margin: 0 auto;
      padding: 1.5rem;
    }
  `]
})
export class AppComponent {
  title = 'CrewAI-Locale';
}