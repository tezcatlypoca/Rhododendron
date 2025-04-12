// src/app/app.config.ts
import { ApplicationConfig } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { routes } from './app.routes';
import { authInterceptor } from './core/intercepteurs/auth.interceptor';
import { AgentService } from './services/agent.service';
import { ConversationService } from './services/conversation.service';
import { StateService } from './services/state.service';
import { WebsocketService } from './services/websocket.service';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    provideHttpClient(withInterceptors([authInterceptor])),
    AgentService,
    ConversationService,
    StateService,
    WebsocketService
  ]
};