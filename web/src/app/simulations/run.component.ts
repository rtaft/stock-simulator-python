import { Component, OnInit, ɵɵcontainerRefreshEnd } from '@angular/core';
//import {webSocket, WebSocketSubject} from 'rxjs/webSocket';
import { Socket } from 'ngx-socket-io';
import { Observable } from "rxjs";

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
  selectedTrader: string = '0';
  tradeStartDate: Date = new Date(2010, 1, 1);
  tradeEndDate: Date = new Date(2011, 1, 1);
  startingCash: number = 10000;
  description: string;
  simulationId: number;
  running = false;
  status: string = 'Not Started'
  stockLists = []
  selectedStockList = 'DOW'
  progress;

  constructor(private traderService: TraderService,
              private simulationService: SimulationService, 
              private stockService: StockService,
              private socket: Socket) { 

    this.progress = this.socket.fromEvent<string>('ws')
  }

  ngOnInit() {
    this.refresh();
  }

  refresh() {
    this.traderService.listTraders().toPromise().then( result => this.traders = result);
    this.stockService.getStockList().toPromise().then( result => this.stockLists = result)
  }

  runSimulation() {
    if (this.selectedTrader != null && this.tradeStartDate != null && this.tradeEndDate != null && this.tradeStartDate < this.tradeEndDate) {
      this.running = true;
      this.simulationService.runSimulation(this.selectedTrader, this.tradeStartDate, this.tradeEndDate, this.startingCash, this.description, this.selectedStockList).
          toPromise().then( result => this.setSimulationId(result)).catch(result => this.running = false);
    }
  }

  setSimulationId(simId) {
    this.simulationId = simId;
    this.progress.subscribe(data => console.log(data))
    //this.pollStatus();
  }

  wsTest() {
    //const myWebSocket: WebSocketSubject<string> = webSocket('ws://localhost:5000/socket.io/');
    //myWebSocket.asObservable().subscribe(dataFromServer => console.log(dataFromServer));
    this.socket.emit("new-message", 'message');
  }

  pollStatus() {
    this.simulationService.getSimulationStatus(this.simulationId).toPromise().then(result => this.updateStatus(result));
  }

  updateStatus(status:SimulationStatus) {
    this.status = status.status;
    if (this.status === 'Completed.') {
      this.running = false;
      // TODO redirect to results
    } else {
      setTimeout(() => {this.pollStatus()}, 1000)
    }
  }
}
