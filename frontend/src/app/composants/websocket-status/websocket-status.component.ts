// src/app/composants/websocket-status/websocket-status.component.ts
import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { WebsocketService } from '../../services/websocket.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-websocket-status',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="ws-status" [ngClass]="{'connected': isConnected, 'disconnected': !isConnected}">
      <span class="status-dot"></span>
      <span class="status-text">{{ statusText }}</span>
    </div>
  `,
  styles: [`
    .ws-status {
      display: flex;
      align-items: center;
      padding: 0.25rem 0.5rem;
      border-radius: 4px;
      font-size: 0.8rem;
      gap: 0.25rem;
    }
    
    .status-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
    }
    
    .connected {
      background-color: rgba(76, 175, 80, 0.1);
      color: #2e7d32;
    }
    
    .connected .status-dot {
      background-color: #2e7d32;
    }
    
    .disconnected {
      background-color: rgba(244, 67, 54, 0.1);
      color: #d32f2f;
    }
    
    .disconnected .status-dot {
      background-color: #d32f2f;
    }
  `]
})
export class WebsocketStatusComponent implements OnInit, OnDestroy {
  isConnected: boolean = false;
  private subscription: Subscription = new Subscription();

  constructor(private websocketService: WebsocketService) {}

  ngOnInit(): void {
    this.subscription = this.websocketService.connectionStatus$.subscribe(
      status => {
        this.isConnected = status;
      }
    );
  }

  ngOnDestroy(): void {
    this.subscription.unsubscribe();
  }

  get statusText(): string {
    return this.isConnected ? 'Connecté' : 'Déconnecté';
  }
}