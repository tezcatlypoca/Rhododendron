import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { Projet, ProjetCreate, ProjetUpdate } from '../models/projet.model';

@Injectable({
  providedIn: 'root'
})
export class ProjetService {
  private apiUrl = `${environment.apiUrl}/projets`;

  constructor(private http: HttpClient) { }

  // Créer un nouveau projet
  createProjet(projet: ProjetCreate): Observable<Projet> {
    return this.http.post<Projet>(this.apiUrl, projet);
  }

  // Récupérer tous les projets
  getProjets(): Observable<Projet[]> {
    return this.http.get<Projet[]>(this.apiUrl);
  }

  // Récupérer un projet par son ID
  getProjet(id: string): Observable<Projet> {
    return this.http.get<Projet>(`${this.apiUrl}/${id}`);
  }

  // Mettre à jour un projet
  updateProjet(id: string, projet: ProjetUpdate): Observable<Projet> {
    return this.http.put<Projet>(`${this.apiUrl}/${id}`, projet);
  }

  // Supprimer un projet
  deleteProjet(id: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${id}`);
  }
}
