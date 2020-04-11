import { Component, OnInit, Input } from '@angular/core';
import { SimulationTrader, Transaction } from 'src/app/models/simulation';
import { StockService } from 'src/app/services/stock';

@Component({
  selector: 'app-simulation-capitalgains',
  templateUrl: './capitalgains.component.html',
  styleUrls: ['./capitalgains.component.scss']
})
export class CapitalgainsComponent implements OnInit {
  @Input() simulationTrader: SimulationTrader;
  @Input() transactions: Transaction[];
  constructor(private stockService: StockService) { }

  ngOnInit() {
    const symbols = [];
    for (const transaction of this.transactions) {
      if (transaction.transaction_type == 'BUY') {
        symbols.push(transaction.symbol);
      }
    }
    this.stockService.getStockHistory(symbols, this.simulationTrader.end_date, this.simulationTrader.end_date).toPromise().then(result => console.log(result))
  }

}
