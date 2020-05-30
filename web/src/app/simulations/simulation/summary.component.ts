import { Component, OnInit, Input, OnChanges } from '@angular/core';
import { SimulationTrader, Transaction, CapitalGain } from 'src/app/models/simulation';
import { SimulationService } from 'src/app/services/simulations';

@Component({
  selector: 'app-summary',
  templateUrl: './summary.component.html',
  styleUrls: ['./summary.component.scss']
})
export class SummaryComponent implements OnInit, OnChanges {
  @Input() simulationTraders: SimulationTrader[];
  @Input() transactions: Map<number, Transaction[]>;
  @Input() capitalGains: Map<number, CapitalGain[]>;
  @Input() change: boolean;

  dividends = {}
  dividend_taxes = {}
  capitalGainsProfit = {}

  constructor(private simulationService: SimulationService) { }

  ngOnChanges(): void {
    if (this.simulationTraders) {
      for (const trader of this.simulationTraders) {
        this.dividends[trader.simulation_trader_id] = 0
        this.dividend_taxes[trader.simulation_trader_id] = 0
        
        this.capitalGainsProfit[trader.simulation_trader_id] = 0
        if (this.capitalGains.get(trader.simulation_trader_id)) {
          for (const gain of this.capitalGains.get(trader.simulation_trader_id)) {
            this.capitalGainsProfit[trader.simulation_trader_id] += gain['proceeds'] + gain['cost_basis']
          }
        }

        if (this.transactions.get(trader.simulation_trader_id)) {
          for (const transaction of this.transactions.get(trader.simulation_trader_id)) {
            if (transaction.transaction_type == 'DIV') {
              this.dividends[transaction.simulation_trader_id] += transaction.transaction_total;
              this.dividend_taxes[transaction.simulation_trader_id] += transaction.transaction_tax;
            }
          }
        }
      }
    }
  }

  ngOnInit() {
    
  }
}
