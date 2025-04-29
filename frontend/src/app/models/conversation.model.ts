export interface Conversation {
  id: string;
  title: string;
  created_at: Date;
  updated_at: Date;
  agent_id?: string;
  conversation_metadata: any;
  messages?: Message[];
}

export interface ConversationCreate {
  title: string;
  agent_id?: string;
  conversation_metadata?: any;
}

export interface ConversationUpdate {
  title?: string;
  agent_id?: string;
  conversation_metadata?: any;
}
