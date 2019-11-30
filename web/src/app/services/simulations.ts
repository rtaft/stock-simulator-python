import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { Simulation } from '../models/simulation';

@Injectable()
export class SimulationService {
    constructor(private httpClient: HttpClient) {}

    runSimulation(trader_id: String, start_date: Date, end_date: Date): Observable<number> {
        return this.httpClient.post<number>('/api/simulation', {trader_id: trader_id, start_date: start_date, end_date: end_date});
    } 

    getSimulationStatus(simulation_id: number): Observable<number> {
        return this.httpClient.get<number>('/api/simulation/' + simulation_id + '/status');
    }

    getSimulation(simulation_id: number): Observable<Simulation> {
        return this.httpClient.get<number>('/api/simulation/' + simulation_id);
    }

}