import { Component, OnInit } from '@angular/core';
import { SimulationService } from '../services/simulations';
import { Simulation } from '../models/simulation';  
import { ColumnMode } from '@swimlane/ngx-datatable/public-api';

@Component({
  selector: 'app-simulations',
  templateUrl: './simulations.component.html',
  styleUrls: ['./simulations.component.scss']
})
export class SimulationsComponent implements OnInit {
  columnMode: ColumnMode.flex;
  simulations: Simulation[] = [];

  constructor(private simulationService: SimulationService) { }

  ngOnInit() {
      this.simulationService.getSimulations(1, 1).toPromise().then(result => this.simulations = result);
  }
}
