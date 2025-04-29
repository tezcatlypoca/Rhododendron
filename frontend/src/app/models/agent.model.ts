export interface Agent {
  id: string;
  name: string;
  model_type: string;
  role: string;
  config: Record<string, any>;
  created_at: Date;
  updated_at: Date;
}

export interface AgentCreate {
  name: string;
  model_type: string;
  role: string;
  config: Record<string, any>;
}

export interface AgentUpdate {
  name?: string;
  model_type?: string;
  role?: string;
  config?: Record<string, any>;
} 