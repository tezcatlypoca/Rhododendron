// src/app/shared/notifications/notifications.component.ts
import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Subscription } from 'rxjs';
import { NotificationService, Notification, NotificationType } from '../../core/services/notification.service';

@Component({
  selector: 'app-notifications',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './notifications.component.html',
  styleUrls: ['./notifications.component.scss']
})
export class NotificationsComponent implements OnInit, OnDestroy {
  notifications: Notification[] = [];
  private subscription: Subscription = new Subscription();
  
  // Pour utiliser l'enum dans le template
  notificationType = NotificationType;

  constructor(private notificationService: NotificationService) {}

  ngOnInit(): void {
    this.subscription = this.notificationService.notifications$.subscribe(
      notifications => {
        this.notifications = notifications;
      }
    );
  }

  ngOnDestroy(): void {
    this.subscription.unsubscribe();
  }

  closeNotification(notification: Notification): void {
    this.notificationService.removeNotification(notification);
  }

  getIconClass(type: NotificationType): string {
    switch (type) {
      case NotificationType.SUCCESS:
        return 'fa-check-circle';
      case NotificationType.ERROR:
        return 'fa-exclamation-circle';
      case NotificationType.WARNING:
        return 'fa-exclamation-triangle';
      case NotificationType.INFO:
        return 'fa-info-circle';
      default:
        return 'fa-info-circle';
    }
  }
}