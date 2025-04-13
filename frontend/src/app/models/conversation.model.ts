export interface Conversation {
  id: string;
  title: string;
  createdAt: Date;
  updatedAt: Date;
  agent?: {
    id: string;
    name: string;
    model_type: string;
    role: string;
    config: any;
  };
  metadata?: any;
}
