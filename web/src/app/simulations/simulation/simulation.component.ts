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
  private transactions: Transaction[] = [];
  private selectedTransactions: Transaction[];
  private screen: string;

  constructor(private route: ActivatedRoute,
              private simulationService: SimulationService) { }

  ngOnInit() {
    this.sub = this.route.params.subscribe(params => {
      this.simulation_id = +params['simulation_id']; // (+) converts string 'id' to a number
      this.simulationService.getSimulation(this.simulation_id).toPromise().then(result => {
        this.simulationTraders = result;
        for (let simTrader of this.simulationTraders) {
          this.simulationService.getTransactions(simTrader.simulation_trader_id).toPromise().then(result => this.transactions = this.transactions.concat(result));
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
    if (this.selectedTrader) {
      this.selectedTransactions = this.transactions.filter( transaction => transaction.simulation_trader_id == simulation_trader_id);
      let cash = this.selectedTrader.starting_balance;
      for (const transaction of this.selectedTransactions) {
        cash += transaction.transaction_total;
        transaction.balance = cash;
      }
    }
  }

  show(screen: string) {
    this.screen = screen;
  }

  getClass(simulation_trader_id: number) {
    if (simulation_trader_id == this.selected) {
      return "menu-item selected-menu-item";
    } else {
      return "menu-item";
    }
  }

  getScreenClass(screen: string) {
    if (screen == this.screen) {
      return "menu-item submenu selected-menu-item";
    } else {
      return "menu-item submenu";
    }
  }
}
