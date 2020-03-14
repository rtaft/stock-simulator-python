import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { HttpClientModule } from '@angular/common/http'; 
import { FormsModule } from '@angular/forms';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { MDBBootstrapModule } from 'angular-bootstrap-md';
import { NgxDatatableModule } from '@swimlane/ngx-datatable';

import { MenuComponent } from './base/menu.component';
import { DashboardComponent } from './base/dashboard.component';
import { TradersComponent } from './simulations/traders.component';
import { SimulationsComponent } from './simulations/simulations.component';
import { RunComponent } from './simulations/run.component';
import { SettingsComponent } from './simulations/settings.component';
import { SimulationComponent } from './simulations/simulation/simulation.component';
import { ViewComponent } from './data/view.component';
import { AddComponent } from './data/add.component';
import { SearchComponent } from './data/search.component';

/* Services */
import { TraderService } from './services/traders';
import { SimulationService } from './services/simulations';
import { ResultsComponent } from './simulations/simulation/results.component';


@NgModule({
  declarations: [
    AppComponent,
    MenuComponent,
    DashboardComponent,
    TradersComponent,
    SimulationsComponent,
    RunComponent,
    SettingsComponent,
    ViewComponent,
    AddComponent,
    SearchComponent,
    SimulationComponent,
    ResultsComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    FormsModule,
    HttpClientModule,
    MDBBootstrapModule.forRoot(),
    NgxDatatableModule
  ],
  providers: [
    SimulationService,
    TraderService
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
