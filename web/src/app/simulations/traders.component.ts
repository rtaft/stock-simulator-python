import { Component, OnInit, ɵɵcontainerRefreshEnd } from '@angular/core';

import { Trader } from '../models/trader';

import { TraderService } from '../services/traders';

@Component({
  selector: 'app-traders',
  templateUrl: './traders.component.html',
  styleUrls: ['./traders.component.scss']
})
export class TradersComponent implements OnInit {
  newTrader = new Trader()
  traderLocation = 'local';
  fileLocation: string = '0';
  gitRepo: string;
  tradersOnDisk = []
  traders: Trader[] = []
  constructor(private traderService: TraderService) { }

  ngOnInit() {
    this.refresh();
  }

  refresh() {
    this.traderService.listTraders().toPromise().then(result => this.traders = result)
    this.traderService.listTradersOnDisk().toPromise().then(result => this.tradersOnDisk = result)
  }

  addTrader() {
    if (this.traderLocation == 'local') {
      this.newTrader.location = 'file://' + this.fileLocation;
      this.newTrader.location_type = 'local';
      this.newTrader.name = this.tradersOnDisk.find(trader => trader.filename === this.fileLocation).name
      this.traderService.addTrader(this.newTrader).toPromise().then(result => this.refresh());
    } else if (this.traderLocation == 'repo') {
      this.newTrader.location = this.gitRepo;
      this.newTrader.location_type = 'repo'
      this.traderService.addTrader(this.newTrader).toPromise().then(result => this.refresh());
    }

    this.newTrader = new Trader();
  }
}
