import { Component, Input, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import {map} from 'rxjs/operators';
import {Observable } from 'rxjs';

import { Simulation, SimulationTrader} from '../../models/simulation';
import { SimulationService } from '../../services/simulations';

@Component({
  selector: 'app-simulation',
  templateUrl: './simulation.component.html',
  styleUrls: ['./simulation.component.scss']
})
export class SimulationComponent implements OnInit {
  private simulation_id: number;
  private sub: any;
  private simulationTraders: SimulationTrader[];

  constructor(private route: ActivatedRoute,
              private simulationService: SimulationService) { }

  ngOnInit() {
    this.sub = this.route.params.subscribe(params => {
      this.simulation_id = +params['simulation_id']; // (+) converts string 'id' to a number
      console.log(this.simulation_id);
      this.simulationService.getSimulation(this.simulation_id).toPromise().then(result => {
        this.simulationTraders = result;
        for (let simTrader of this.simulationTraders) {
          this.simulationService.getTransactions(simTrader.simulation_trader_id).toPromise().then(result => console.log(result))
        }
      });
    });
  }

  ngOnDestroy() {
    this.sub.unsubscribe();
  }
}
