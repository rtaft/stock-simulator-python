import { Component, OnInit, ɵɵcontainerRefreshEnd } from '@angular/core';
//import {webSocket, WebSocketSubject} from 'rxjs/webSocket';
import { Socket } from 'ngx-socket-io';
import { Observable, Subscription } from "rxjs";
import { Router } from '@angular/router';
import { Trader } from '../models/trader';

import { TraderService } from '../services/traders';
import { SimulationService } from '../services/simulations';
import { Simulation, SimulationStatus } from '../models/simulation';
import { StockService } from '../services/stock';

@Component({
  selector: 'app-run',
  templateUrl: './run.component.html',
  styleUrls: ['./run.component.scss']
})
export class RunComponent implements OnInit {
  traders: Trader[] = []
  selectedTraders: string[] = [];
  tradeStartDate: Date = new Date(2010, 1, 1);
  tradeEndDate: Date = new Date(2011, 1, 1);
  startingCash: number = 10000;
  description: string;
  simulationId: number;
  running = false;
  status: string = 'Not Started'
  stockLists = []
  selectedStockList = 'DOW'
  progress: Observable<string>;
  subscription: Subscription;

  constructor(private traderService: TraderService,
              private simulationService: SimulationService, 
              private stockService: StockService,
              private socket: Socket,
              private router: Router ) { 
  }

  ngOnInit() {
    this.refresh();
  }

  refresh() {
    this.traderService.listTraders().toPromise().then( result => this.traders = result);
    this.stockService.getStockList().toPromise().then( result => this.stockLists = result)
  }

  runSimulation() {
    if (this.selectedTraders != null && this.tradeStartDate != null && this.tradeEndDate != null && this.tradeStartDate < this.tradeEndDate) {
      this.running = true;
      this.simulationService.runSimulation(this.selectedTraders, this.tradeStartDate, this.tradeEndDate, this.startingCash, this.description, this.selectedStockList).
          toPromise().then( result => this.setSimulationId(result)).catch(result => this.running = false);
    }
  }

  setSimulationId(simId) {
    this.simulationId = simId;
    if (this.subscription == null) {
      this.progress = this.socket.fromEvent<string>('/simulation/' + simId);
      this.subscription = this.progress.subscribe(data => this.updateStatus(data));
    }
  }

  updateStatus(status:string) {
    this.status = status;
    if (this.status === 'Completed.') {
      this.running = false;
      this.subscription.unsubscribe();
      this.subscription = null;
      this.router.navigate(['/simulations/' + this.simulationId]);
    } 
  }
}
