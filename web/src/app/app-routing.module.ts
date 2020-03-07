import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { DashboardComponent } from './base/dashboard.component';
import { TradersComponent } from './simulations/traders.component';
import { SimulationsComponent } from './simulations/simulations.component';
import { RunComponent } from './simulations/run.component';
import { SettingsComponent } from './simulations/settings.component';
import { SimulationComponent } from './simulations/simulation/simulation.component';
import { ViewComponent } from './data/view.component';
import { AddComponent } from './data/add.component';
import { SearchComponent } from './data/search.component';

const routes: Routes = [ 
  { path: '', component: DashboardComponent},
  { path: 'traders', component: TradersComponent },
  { path: 'simulations', component: SimulationsComponent },
  { path: 'simulations/:simulation_id', component: SimulationComponent },
  { path: 'run', component: RunComponent },
  { path: 'settings', component: SettingsComponent },
  { path: 'data/view', component: ViewComponent },
  { path: 'data/add', component: AddComponent },
  { path: 'data/search', component: SearchComponent },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
