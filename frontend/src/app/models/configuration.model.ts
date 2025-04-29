export interface Configuration {
  id: string;
  name: string;
  description: string;
  settings: Record<string, any>;
  createdAt: Date;
  updatedAt: Date;
}

export interface ConfigurationUpdate {
  name?: string;
  description?: string;
  settings?: Record<string, any>;
} 