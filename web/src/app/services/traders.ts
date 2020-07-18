import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { Trader } from '../models/trader';

@Injectable()
export class TraderService {
    constructor(private httpClient: HttpClient) {}

    listTraders(): Observable<Trader[]> {
        return this.httpClient.get<Trader[]>('/api/trader');
    }

    listTradersOnDisk(): Observable<string[]> {
        return this.httpClient.get<string[]>('/api/trader?location=disk');
    }

    editTrader(trader_id: number, trader: Trader){
        return this.httpClient.put('/api/trader/' + trader_id, trader);
    }

    addTrader(trader: Trader) {
        return this.httpClient.post('/api/trader', trader);
    }

    deleteTrader(trader_id: number) {
        return this.httpClient.delete('/api/trader/' + trader_id);
    }

    getSchema(trader_id: number) {
        return this.httpClient.get<Trader[]>('/api/trader/' + trader_id + '/schema');
    }
}