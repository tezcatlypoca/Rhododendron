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
    config?: Record<string, any>;
  }
  
  export interface AgentRequestDTO {
    prompt: string;
    parameters?: Record<string, any>;
  }
  
  export interface AgentResponse {
    status: string;
    response: string;
    timestamp: string;
  }