import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { Simulation, SimulationStatus, SimulationTrader, Transaction, CapitalGain } from '../models/simulation';

@Injectable()
export class SimulationService {
    constructor(private httpClient: HttpClient) {}

    runSimulation(traders: {}, start_date: Date, end_date: Date, description: string, stockList: string): Observable<number> {
        return this.httpClient.post<number>('/api/simulation', {traders: traders, start_date: start_date, end_date: end_date, 
                                                                description: description, stock_list: stockList});
    } 

    getSimulationStatus(simulation_id: number): Observable<SimulationStatus> {
        return this.httpClient.get<SimulationStatus>('/api/simulation/' + simulation_id + '/status');
    }

    getSimulation(simulation_id: number): Observable<SimulationTrader[]> {
        return this.httpClient.get<SimulationTrader[]>('/api/simulation/' + simulation_id);
    }

    getSimulations(index: number, length: number): Observable<Simulation[]> {
        return this.httpClient.get<Simulation[]>('/api/simulation');
    }

    getTransactions(simulation_id: number): Observable<Record<number, Transaction[]>> {
        return this.httpClient.get<Record<number, Transaction[]>>('/api/transaction/' + simulation_id);
    }

    getCapitalGains(simulation_id: number): Observable<Record<number, CapitalGain[]>> {
        return this.httpClient.get<Record<number, CapitalGain[]>>('/api/capital_gains/' + simulation_id);
    }
}
