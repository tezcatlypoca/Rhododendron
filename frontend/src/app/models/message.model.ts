export interface Message {
  id: string;
  content: string;
  role: MessageRole;
  conversation_id: string;
  created_at: Date;
}

export interface MessageCreate {
  content: string;
  role: MessageRole;
}

export enum MessageRole {
  USER = 'user',
  ASSISTANT = 'assistant',
  SYSTEM = 'system'
}
