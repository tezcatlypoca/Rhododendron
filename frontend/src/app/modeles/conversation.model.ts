// src/app/modeles/conversation.model.ts
export enum MessageRole {
  USER = "user",
  ASSISTANT = "assistant",
  SYSTEM = "system"
}

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: string; // String pour compatibilité avec le backend
  agent_id?: string;
  metadata?: Record<string, any>;
}

export interface Conversation {
  id: string;
  title: string;
  created_at: string; // String pour compatibilité avec le backend
  updated_at: string; // String pour compatibilité avec le backend
  messages: Message[];
  participants: string[];
  agent_id?: string;
  metadata?: Record<string, any>;
}

export interface MessageRequest {
  prompt: string;
  parameters?: Record<string, any>;
}

export interface MessageResponse {
  status: string;
  response: string;
  timestamp: string;
}