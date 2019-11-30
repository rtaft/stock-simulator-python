import { Component, OnInit, ɵɵcontainerRefreshEnd } from '@angular/core';

import { Trader } from '../models/trader';

import { TraderService } from '../services/traders';
import { SimulationService } from '../services/simulations';

@Component({
  selector: 'app-run',
  templateUrl: './run.component.html',
  styleUrls: ['./run.component.scss']
})
export class RunComponent implements OnInit {
  traders: Trader[] = []
  selectedTrader: String = '0';
  tradeStartDate: Date;
  tradeEndDate: Date;
  simulationId: Number;
  
  constructor(private traderService: TraderService, private simulationService: SimulationService) { }

  ngOnInit() {
    this.refresh();
  }

  refresh() {
    this.traderService.listTraders().toPromise().then( result => this.traders = result);
  }

  runSimulation() {
    this.simulationService.runSimulation(this.selectedTrader, this.tradeStartDate, this.tradeEndDate).toPromise().then( result => this.simulationId = result);
  }
}
