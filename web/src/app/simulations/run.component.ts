import { Component, OnInit, ɵɵcontainerRefreshEnd } from '@angular/core';

import { Trader } from '../models/trader';

import { TraderService } from '../services/traders';
import { SimulationService } from '../services/simulations';
import { Simulation, SimulationStatus } from '../models/simulation';

@Component({
  selector: 'app-run',
  templateUrl: './run.component.html',
  styleUrls: ['./run.component.scss']
})
export class RunComponent implements OnInit {
  traders: Trader[] = []
  selectedTrader: string = '0';
  tradeStartDate: Date;
  tradeEndDate: Date;
  startingCash: number = 10000;
  description: string;
  simulationId: number;
  running = false;
  status: string = 'Not Started'
  
  constructor(private traderService: TraderService, private simulationService: SimulationService) { }

  ngOnInit() {
    this.refresh();
  }

  refresh() {
    this.traderService.listTraders().toPromise().then( result => this.traders = result);
  }

  runSimulation() {
    if (this.selectedTrader != null && this.tradeStartDate != null && this.tradeEndDate != null && this.tradeStartDate < this.tradeEndDate) {
      this.running = true;
      this.simulationService.runSimulation(this.selectedTrader, this.tradeStartDate, this.tradeEndDate, this.startingCash, this.description).
          toPromise().then( result => this.setSimulationId(result)).catch(result => this.running = false);
    }
  }

  setSimulationId(simId) {
    this.simulationId = simId;
    this.pollStatus();
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
