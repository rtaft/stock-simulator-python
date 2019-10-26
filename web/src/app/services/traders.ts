import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';


@Injectable()
export class TraderService {
    constructor(private httpClient: HttpClient) {}

    listTraders(): Observable<string[]> {
        return this.httpClient.get<string[]>('/api/trader');
    }
}