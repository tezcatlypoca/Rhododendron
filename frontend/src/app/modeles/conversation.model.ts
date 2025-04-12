// src/app/modeles/conversation.model.ts
export interface Message {
    id: string;
    sender: 'user' | 'agent';
    content: string;
    timestamp: Date;
  }
  
  export interface Conversation {
    id: string;
    agentId: string;
    messages: Message[];
    lastActivity: Date;
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