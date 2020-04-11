import { Component, OnInit, Input } from '@angular/core';
import { SimulationTrader, Transaction } from 'src/app/models/simulation';

@Component({
  selector: 'app-simulation-transactions',
  templateUrl: './transactions.component.html',
  styleUrls: ['./transactions.component.scss']
})
export class TransactionsComponent implements OnInit {
  @Input() simulationTrader: SimulationTrader;
  @Input() transactions: Transaction[];

  constructor() { }

  ngOnInit() {

  }

  getCellClass() {
    return ' table-cells';
  }

}
