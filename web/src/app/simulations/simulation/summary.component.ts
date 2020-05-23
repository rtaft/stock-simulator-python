import { Component, OnInit, Input, OnChanges } from '@angular/core';
import { SimulationTrader, Transaction } from 'src/app/models/simulation';
import { SimulationService } from 'src/app/services/simulations';

@Component({
  selector: 'app-summary',
  templateUrl: './summary.component.html',
  styleUrls: ['./summary.component.scss']
})
export class SummaryComponent implements OnInit, OnChanges {
  @Input() simulationTraders: SimulationTrader[];
  @Input() transactions: Transaction[] = [];
  dividends = {}
  dividend_taxes = {}
  capitalGains = {}

  constructor(private simulationService: SimulationService) { }

  ngOnChanges(): void {
    if (this.simulationTraders) {
      for (const trader of this.simulationTraders) {
        this.dividends[trader.simulation_trader_id] = 0
        this.dividend_taxes[trader.simulation_trader_id] = 0
        this.simulationService.getCapitalGains(trader.simulation_trader_id).toPromise().then(result => {
          this.capitalGains[trader.simulation_trader_id] = 0
          for (const gain of result) {
            this.capitalGains[trader.simulation_trader_id] += gain['proceeds'] + gain['cost_basis']
          }
        });
      }
      for (const transaction of this.transactions) {
        if (transaction.transaction_type == 'DIV') {
          this.dividends[transaction.simulation_trader_id] += transaction.transaction_total;
          this.dividend_taxes[transaction.simulation_trader_id] += transaction.transaction_tax;
        }
      }
    }
  }

  ngOnInit() {
    
  }
}
