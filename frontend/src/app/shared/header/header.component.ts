// src/app/shared/header/header.component.ts
import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { Subscription } from 'rxjs';
import { AuthService } from '../../core/services/auth.service';
import { NotificationService } from '../../core/services/notification.service';
import { User } from '../../core/models/user.model';
import { UserData } from '../../core/services/mock-users';
import { USER_AVATARS } from '../../core/constants/image-paths';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss']
})
export class HeaderComponent implements OnInit, OnDestroy {
  currentUser: User | null = null;
  userData: UserData | null = null;
  isMenuOpen = false;
  private userSubscription: Subscription = new Subscription();
  private userDataSubscription: Subscription = new Subscription();
  
  // Exposer les constantes au template
  userAvatars = USER_AVATARS;
  
  constructor(
    private authService: AuthService,
    private notificationService: NotificationService
  ) {}
  
  ngOnInit() {
    this.userSubscription = this.authService.currentUser$.subscribe(
      user => this.currentUser = user
    );
    
    this.userDataSubscription = this.authService.userData$.subscribe(
      data => this.userData = data
    );
  }
  
  ngOnDestroy() {
    this.userSubscription.unsubscribe();
    this.userDataSubscription.unsubscribe();
  }
  
  toggleMenu() {
    this.isMenuOpen = !this.isMenuOpen;
  }
  
  logout() {
    this.authService.logout().subscribe({
      next: () => {
        this.notificationService.success('Déconnexion réussie');
      }
    });
  }
  
  getAvatarUrl(): string {
    if (!this.currentUser) {
      return USER_AVATARS.default;
    }
    
    // Correspondance simple basée sur le nom d'utilisateur
    const username = this.currentUser.username.toLowerCase();
    if (username === 'testeur') return USER_AVATARS.testeur;
    if (username === 'kinder') return USER_AVATARS.val;
    if (username === 'samsan') return USER_AVATARS.sam;
    if (username === 'tata') return USER_AVATARS.yo;
    
    return USER_AVATARS.default;
  }
  
  getOrchestreCount(): number {
    return this.userData?.orchestres?.length || 0;
  }
}