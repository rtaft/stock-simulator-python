import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { Simulation, SimulationStatus, SimulationTrader, Transaction, CapitalGain } from '../models/simulation';

@Injectable()
export class SimulationService {
    constructor(private httpClient: HttpClient) {}

    runSimulation(trader_id: string, start_date: Date, end_date: Date, starting_cash: number, description: string, stockList: string): Observable<number> {
        return this.httpClient.post<number>('/api/simulation', {trader_id: trader_id, start_date: start_date, end_date: end_date, 
                                                                starting_cash: starting_cash, description: description, stock_list: stockList});
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

    getTransactions(sim_trader_id: number): Observable<Transaction[]> {
        return this.httpClient.get<Transaction[]>('/api/transaction/' + sim_trader_id);
    }

    getCapitalGains(sim_trader_id: number): Observable<CapitalGain[]> {
        return this.httpClient.get<CapitalGain[]>('/api/capital_gains/' + sim_trader_id);
    }
}
