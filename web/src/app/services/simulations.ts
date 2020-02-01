import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { Simulation, SimulationStatus } from '../models/simulation';

@Injectable()
export class SimulationService {
    constructor(private httpClient: HttpClient) {}

    runSimulation(trader_id: string, start_date: Date, end_date: Date, starting_cash: number, description: string): Observable<number> {
        return this.httpClient.post<number>('/api/simulation', {trader_id: trader_id, start_date: start_date, end_date: end_date, 
                                                                starting_cash: starting_cash, description: description});
    } 

    getSimulationStatus(simulation_id: number): Observable<SimulationStatus> {
        return this.httpClient.get<SimulationStatus>('/api/simulation/' + simulation_id + '/status');
    }

    getSimulation(simulation_id: number): Observable<Simulation> {
        return this.httpClient.get<Simulation>('/api/simulation/' + simulation_id);
    }

    getSimulations(index: number, length: number): Observable<Simulation[]> {
        return this.httpClient.get<Simulation[]>('/api/simulation');
    }
}