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
import { StockService } from './services/stock';
import { TransactionsComponent } from './simulations/simulation/transactions.component';
import { CapitalgainsComponent } from './simulations/simulation/capitalgains.component';

import { SocketIoModule, SocketIoConfig } from 'ngx-socket-io';
import { SummaryComponent } from './simulations/simulation/summary.component';
const config: SocketIoConfig = { url: 'http://localhost:4200', options: {} };

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
    TransactionsComponent,
    CapitalgainsComponent,
    SummaryComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    FormsModule,
    HttpClientModule,
    MDBBootstrapModule.forRoot(),
    NgxDatatableModule,
    SocketIoModule.forRoot(config)
  ],
  providers: [
    SimulationService,
    StockService,
    TraderService
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
