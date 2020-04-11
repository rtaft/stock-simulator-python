import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable()
export class StockService {
    constructor(private httpClient: HttpClient) {}

    getStockHistory(symbols: string[], start_date: string, end_date: string): Observable<any> {
        return this.httpClient.get<any>('/api/stock/history', {params: {symbols: symbols.join(), start_date: start_date, end_date:end_date}});
    }

    getStockList(): Observable<string[]> {
        return this.httpClient.get<string[]>('/api/stock/dataset');
    }
}
