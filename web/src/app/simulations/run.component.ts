import { Component, OnInit, ɵɵcontainerRefreshEnd } from '@angular/core';

import { Trader } from '../models/trader';

import { TraderService } from '../services/traders';

@Component({
  selector: 'app-run',
  templateUrl: './run.component.html',
  styleUrls: ['./run.component.scss']
})
export class RunComponent implements OnInit {
  newTrader = new Trader()
  traderLocation = 'local';
  fileLocation: string = '0';

  tradersOnDisk: string[] = []
  traders: Trader[] = []
  constructor(private traderService: TraderService) { }

  ngOnInit() {
    this.refresh();
  }

  refresh() {
    this.traderService.listTraders().toPromise().then( result => this.traders = result)
    this.traderService.listTradersOnDisk().toPromise().then( result => this.tradersOnDisk = result)
  }

}
