import { Component, OnInit } from '@angular/core';
import { SimulationService } from '../services/simulations';
import { Simulation } from '../models/simulation';

@Component({
  selector: 'app-simulations',
  templateUrl: './simulations.component.html',
  styleUrls: ['./simulations.component.scss']
})
export class SimulationsComponent implements OnInit {

  simulations: Simulation[] = [];

  columns = [
    { name: 'Simulation Id', prop: 'simulation_id'},
    { name: 'Simulation Date', prop: 'simulation_date'},
    { name: 'Description'},
    { name: 'Starting Balance', prop: 'starting_balance'},
    { name: 'Start Date', prop: 'start_date'},
    { name: 'End Date', prop: 'end_date'},
  ];

  constructor(private simulationService: SimulationService) { }

  ngOnInit() {
      this.simulationService.getSimulations(1, 1).toPromise().then(result => this.simulations = result);
  }



}
