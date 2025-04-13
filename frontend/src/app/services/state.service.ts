// src/app/services/state.service.ts
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { Agent } from '../modeles/agent.model';
import { Conversation } from '../modeles/conversation.model';
import { Message } from '../modeles/message.model';

/**
 * Service de gestion de l'état global de l'application
 * Centralise les données partagées entre composants
 */
@Injectable({
  providedIn: 'root'
})
export class StateService {
  // État des agents
  private agentsSubject = new BehaviorSubject<Agent[]>([]);
  agents$ = this.agentsSubject.asObservable();

  // État des conversations
  private conversationsSubject = new BehaviorSubject<Conversation[]>([]);
  conversations$ = this.conversationsSubject.asObservable();

  // État de la conversation active
  private activeConversationSubject = new BehaviorSubject<Conversation | null>(null);
  activeConversation$ = this.activeConversationSubject.asObservable();

  // État des messages de la conversation active
  private activeConversationMessagesSubject = new BehaviorSubject<Message[]>([]);
  activeConversationMessages$ = this.activeConversationMessagesSubject.asObservable();

  constructor() {}

  // Agents
  updateAgents(agents: Agent[]): void {
    this.agentsSubject.next(agents);
  }

  addAgent(agent: Agent): void {
    const currentAgents = this.agentsSubject.value;
    this.agentsSubject.next([...currentAgents, agent]);
  }

  updateAgent(updatedAgent: Agent): void {
    const currentAgents = this.agentsSubject.value;
    const index = currentAgents.findIndex(agent => agent.id === updatedAgent.id);

    if (index !== -1) {
      const newAgents = [...currentAgents];
      newAgents[index] = updatedAgent;
      this.agentsSubject.next(newAgents);
    }
  }

  // Conversations
  updateConversations(conversations: Conversation[]): void {
    this.conversationsSubject.next(conversations);
  }

  addConversation(conversation: Conversation): void {
    const currentConversations = this.conversationsSubject.value;
    this.conversationsSubject.next([...currentConversations, conversation]);
  }

  updateConversation(updatedConversation: Conversation): void {
    const currentConversations = this.conversationsSubject.value;
    const index = currentConversations.findIndex(conv => conv.id === updatedConversation.id);

    if (index !== -1) {
      const newConversations = [...currentConversations];
      newConversations[index] = updatedConversation;
      this.conversationsSubject.next(newConversations);
    }
  }

  deleteConversation(conversationId: string): void {
    const currentConversations = this.conversationsSubject.value;
    this.conversationsSubject.next(currentConversations.filter(conv => conv.id !== conversationId));
  }

  // Conversation active
  setActiveConversation(conversation: Conversation | null): void {
    this.activeConversationSubject.next(conversation);
    if (conversation) {
      this.activeConversationMessagesSubject.next(conversation.messages || []);
    } else {
      this.activeConversationMessagesSubject.next([]);
    }
  }

  // Messages de la conversation active
  updateActiveConversationMessages(messages: Message[]): void {
    console.log('StateService: mise à jour des messages:', messages);
    // S'assurer que les messages sont dans le bon ordre
    const sortedMessages = [...messages].sort((a, b) =>
      new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    );
    this.activeConversationMessagesSubject.next(sortedMessages);

    // Mettre à jour également la conversation active
    const activeConversation = this.activeConversationSubject.value;
    if (activeConversation) {
      const updatedConversation = {
        ...activeConversation,
        messages: sortedMessages
      };
      this.activeConversationSubject.next(updatedConversation);
    }
  }

  addMessageToActiveConversation(message: Message): void {
    const currentMessages = this.activeConversationMessagesSubject.value;
    this.activeConversationMessagesSubject.next([...currentMessages, message]);

    // Mettre à jour également la conversation active
    const activeConversation = this.activeConversationSubject.value;
    if (activeConversation) {
      const updatedConversation = {
        ...activeConversation,
        messages: [...currentMessages, message]
      };
      this.activeConversationSubject.next(updatedConversation);

      // Mettre à jour la liste des conversations
      this.updateConversation(updatedConversation);
    }
  }
}
