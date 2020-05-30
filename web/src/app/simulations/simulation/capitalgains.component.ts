import { Component, OnInit, Input, OnChanges } from '@angular/core';
import { SimulationTrader, CapitalGain } from 'src/app/models/simulation';
import { SimulationService } from 'src/app/services/simulations';

@Component({
  selector: 'app-simulation-capitalgains',
  templateUrl: './capitalgains.component.html',
  styleUrls: ['./capitalgains.component.scss']
})
export class CapitalgainsComponent {
  @Input() simulationTrader: SimulationTrader;
  @Input() capitalGains: CapitalGain[];

  constructor(private simulationService: SimulationService) { }

  getCellClass() {
    return ' table-cells';
  }

}
