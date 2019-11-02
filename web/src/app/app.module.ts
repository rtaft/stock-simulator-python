import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { HttpClientModule } from '@angular/common/http'; 
import { FormsModule } from '@angular/forms';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { MDBBootstrapModule } from 'angular-bootstrap-md';

import { MenuComponent } from './base/menu.component';
import { DashboardComponent } from './base/dashboard.component';
import { TradersComponent } from './simulations/traders.component';
import { SimulationsComponent } from './simulations/simulations.component';
import { RunComponent } from './simulations/run.component';
import { SettingsComponent } from './simulations/settings.component';
import { ViewComponent } from './data/view.component';
import { AddComponent } from './data/add.component';
import { SearchComponent } from './data/search.component';

/* Services */
import { TraderService } from './services/traders';

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
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    FormsModule,
    HttpClientModule,
    MDBBootstrapModule.forRoot()
  ],
  providers: [
    TraderService
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
