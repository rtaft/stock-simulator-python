import { Component, Input, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import {map} from 'rxjs/operators';
import {Observable } from 'rxjs';

import { Simulation, SimulationTrader, Transaction} from '../../models/simulation';
import { SimulationService } from '../../services/simulations';

@Component({
  selector: 'app-simulation',
  templateUrl: './simulation.component.html',
  styleUrls: ['./simulation.component.scss']
})
export class SimulationComponent implements OnInit {
  private simulation_id: number;
  private sub: any;
  private simulationTraders: SimulationTrader[];
  private selected = -1;
  private selectedTrader: SimulationTrader;
  private transactions: Transaction[];
  private selectedTransactions: Transaction[];

  constructor(private route: ActivatedRoute,
              private simulationService: SimulationService) { }

  ngOnInit() {
    this.sub = this.route.params.subscribe(params => {
      this.simulation_id = +params['simulation_id']; // (+) converts string 'id' to a number
      console.log(this.simulation_id);
      this.simulationService.getSimulation(this.simulation_id).toPromise().then(result => {
        this.simulationTraders = result;
        for (let simTrader of this.simulationTraders) {
          this.simulationService.getTransactions(simTrader.simulation_trader_id).toPromise().then(result => this.transactions = result);
        }
      });
    });
  }

  ngOnDestroy() {
    this.sub.unsubscribe();
  }

  select(simulation_trader_id: number) {
    this.selected = simulation_trader_id;
    this.selectedTrader = this.simulationTraders.find( simTrader => simTrader.simulation_trader_id == simulation_trader_id);
    this.selectedTransactions = this.transactions.filter( transaction => transaction.simulation_trader_id == simulation_trader_id);
  }

  getClass(simulation_trader_id: number) {
    if (simulation_trader_id == this.selected) {
      return "menu-item selected-menu-item";
    } else {
      return "menu-item";
    }
  }
}
