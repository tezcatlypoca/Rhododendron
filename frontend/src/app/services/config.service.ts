import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { Configuration, ConfigurationUpdate } from '../models/configuration.model';

@Injectable({
  providedIn: 'root'
})
export class ConfigService {
  private apiUrl = `${environment.apiUrl}/configurations`;

  constructor(private http: HttpClient) {}

  getConfigurations(): Observable<Configuration[]> {
    return this.http.get<Configuration[]>(this.apiUrl);
  }

  getConfiguration(id: string): Observable<Configuration> {
    return this.http.get<Configuration>(`${this.apiUrl}/${id}`);
  }

  createConfiguration(configuration: Configuration): Observable<Configuration> {
    return this.http.post<Configuration>(this.apiUrl, configuration);
  }

  updateConfiguration(id: string, configuration: ConfigurationUpdate): Observable<Configuration> {
    return this.http.patch<Configuration>(`${this.apiUrl}/${id}`, configuration);
  }

  deleteConfiguration(id: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`);
  }
} 