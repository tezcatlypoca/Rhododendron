// src/app/core/services/notification.service.ts
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

export enum NotificationType {
  SUCCESS = 'success',
  ERROR = 'error',
  WARNING = 'warning',
  INFO = 'info'
}

export interface Notification {
  type: NotificationType;
  message: string;
  details?: string;
  autoClose?: boolean;
  duration?: number;
}

@Injectable({
  providedIn: 'root'
})
export class NotificationService {
  private notificationsSubject = new BehaviorSubject<Notification[]>([]);
  notifications$: Observable<Notification[]> = this.notificationsSubject.asObservable();

  constructor() {}

  // Ajouter une notification
  addNotification(notification: Notification): void {
    const currentNotifications = this.notificationsSubject.value;
    this.notificationsSubject.next([...currentNotifications, {
      ...notification,
      autoClose: notification.autoClose !== undefined ? notification.autoClose : true,
      duration: notification.duration || 5000
    }]);

    // Auto-fermeture si activée
    if (notification.autoClose !== false) {
      setTimeout(() => {
        this.removeNotification(notification);
      }, notification.duration || 5000);
    }
  }

  // Supprimer une notification
  removeNotification(notificationToRemove: Notification): void {
    const currentNotifications = this.notificationsSubject.value;
    this.notificationsSubject.next(
      currentNotifications.filter(notification => notification !== notificationToRemove)
    );
  }

  // Méthodes d'aide pour différents types de notifications
  success(message: string, details?: string): void {
    this.addNotification({ type: NotificationType.SUCCESS, message, details });
  }

  error(message: string, details?: string): void {
    this.addNotification({ 
      type: NotificationType.ERROR, 
      message, 
      details, 
      autoClose: false 
    });
  }

  warning(message: string, details?: string): void {
    this.addNotification({ type: NotificationType.WARNING, message, details });
  }

  info(message: string, details?: string): void {
    this.addNotification({ type: NotificationType.INFO, message, details });
  }

  // Méthode pour les erreurs de validation de formulaire
  formValidationError(formErrors: { [key: string]: string }): void {
    const errorMessages = Object.values(formErrors);
    if (errorMessages.length > 0) {
      this.error(
        'Le formulaire contient des erreurs',
        errorMessages.join('\n')
      );
    }
  }

  // Vider toutes les notifications
  clearAll(): void {
    this.notificationsSubject.next([]);
  }
}