import { Component, OnInit, Input } from '@angular/core';
import { SimulationTrader, Transaction } from 'src/app/models/simulation';

@Component({
  selector: 'app-simulation-results',
  templateUrl: './results.component.html',
  styleUrls: ['./results.component.scss']
})
export class ResultsComponent implements OnInit {
  @Input() simulationTrader: SimulationTrader;
  @Input() transactions: Transaction[];

  constructor() { }

  ngOnInit() {

  }

}
