// src/app/modeles/agent.model.ts
export interface Agent {
  id: string;
  name: string;
  model_type: string;
  is_active: boolean;
  created_at: string;
  last_used?: string;
  config: Record<string, any>;
}

export interface AgentCreateDTO {
  name: string;
  model_type: string;
  config?: Record<string, any>;
}

export interface AgentUpdateDTO {
  name?: string;
  model_type?: string;
  is_active?: boolean;
  config?: {
    role?: string;
    personality?: string;
    temperature?: number;
    max_tokens?: number;
    context_window?: number;
    context_strategy?: string;
    [key: string]: any;
  };
}
