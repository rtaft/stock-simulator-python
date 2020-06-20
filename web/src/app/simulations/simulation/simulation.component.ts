import { Component, Input, OnInit, ChangeDetectorRef, OnDestroy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import {map} from 'rxjs/operators';
import {Observable } from 'rxjs';

import { Simulation, SimulationTrader, Transaction, CapitalGain} from '../../models/simulation';
import { SimulationService } from '../../services/simulations';

@Component({
  selector: 'app-simulation',
  templateUrl: './simulation.component.html',
  styleUrls: ['./simulation.component.scss']
})
export class SimulationComponent implements OnInit, OnDestroy {
  private simulation_id: number;
  private sub: any;
  private simulationTraders: SimulationTrader[];
  private selected = -1;
  private selectedTrader: SimulationTrader;
  private transactions: Record<number, Transaction[]>;
  private capitalGains: Record<number, CapitalGain[]>;
  private selectedTransactions: Transaction[];
  private screen: string;

  constructor(private route: ActivatedRoute,
              private simulationService: SimulationService,
              private changeRef: ChangeDetectorRef) { }

  ngOnInit() {
    
    this.sub = this.route.params.subscribe(params => {
      this.simulation_id = +params['simulation_id']; // (+) converts string 'id' to a number
      this.simulationService.getSimulation(this.simulation_id).toPromise().then(result => {
        this.simulationTraders = result;
        this.simulationService.getCapitalGains(this.simulation_id).toPromise().then(result => {
          this.capitalGains = result;
          for (const sim_trader_id of Object.keys(result)) {
            for (const capitalGain of result[sim_trader_id]) {
              capitalGain['profit'] = capitalGain['proceeds'] + capitalGain['cost_basis']
              capitalGain['profit_percent'] = (capitalGain['proceeds'] + capitalGain['cost_basis']) / capitalGain['cost_basis'] * -1
            }
          }
        });
        this.simulationService.getTransactions(this.simulation_id).toPromise().then(result => {
          this.transactions = result;
        });
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
      this.selectedTransactions = this.transactions[simulation_trader_id];
      let cash = this.selectedTrader.starting_balance;
      for (const transaction of this.selectedTransactions) {
        cash += transaction.transaction_total;
        transaction.balance = cash;
      }
    }
    this.show('trader');
  }

  show(screen: string) {
    this.screen = screen;
  }

  getClass(simulation_trader_id: number) {
    if (simulation_trader_id == this.selected && this.screen == 'trader') {
      return "menu-item selected-menu-item";
    } else {
      return "menu-item";
    }
  }

  getParentClass(simulation_trader_id: number) {
    if (simulation_trader_id == this.selected) {
      return "trader-item";
    }
  }

  getScreenClass(screen: string) {
    if (screen == this.screen) {
      return "submenu selected-menu-item";
    } else {
      return "submenu";
    }
  }
}
