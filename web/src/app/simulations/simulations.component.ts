import { Component, OnInit } from '@angular/core';
import { Router, RouterModule } from '@angular/router';
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

  constructor(public router: Router,
              private simulationService: SimulationService) { }

  ngOnInit() {
      this.simulationService.getSimulations(1, 1).toPromise().then(result => this.simulations = result);
  }

  onSelect(event) {
    if (event.type == 'click') {
      this.router.navigateByUrl('simulations/' + event.row.simulation_id, event.row);
    }
  }
}
