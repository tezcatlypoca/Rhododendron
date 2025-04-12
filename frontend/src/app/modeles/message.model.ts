export enum MessageRole {
  USER = "user",
  ASSISTANT = "assistant",
  SYSTEM = "system"
}

export interface Message {
  id: string;
  conversation_id: string;
  role: string;
  content: string;
  timestamp: string;
  metadata: any;
}
