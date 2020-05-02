import { Component, OnInit, Input } from '@angular/core';
import { SimulationTrader, CapitalGain } from 'src/app/models/simulation';
import { SimulationService } from 'src/app/services/simulations';

@Component({
  selector: 'app-simulation-capitalgains',
  templateUrl: './capitalgains.component.html',
  styleUrls: ['./capitalgains.component.scss']
})
export class CapitalgainsComponent implements OnInit {
  @Input() simulationTrader: SimulationTrader;
  @Input() capitalGains: CapitalGain[];

  constructor(private simulationService: SimulationService) { }

  ngOnInit() {
    this.simulationService.getCapitalGains(this.simulationTrader.simulation_trader_id).toPromise().then(result => this.capitalGains = result);
  }

  getCellClass() {
    return ' table-cells';
  }

}
