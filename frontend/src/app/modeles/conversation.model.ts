import { Message } from './message.model';

export interface Agent {
  id: string;
  name: string;
  model_type: string;
  role: string;
  config: any;
}

export interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  agent_id?: string;
  agent?: Agent;
  metadata?: any;
  messages: Message[];
}
