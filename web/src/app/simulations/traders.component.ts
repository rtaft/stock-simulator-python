import { Component, OnInit, ɵɵcontainerRefreshEnd} from '@angular/core';

import { Trader } from '../models/trader';

import { TraderService } from '../services/traders';

@Component({
  selector: 'app-traders',
  templateUrl: './traders.component.html',
  styleUrls: ['./traders.component.scss']
})
export class TradersComponent  implements OnInit {
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

  

  addTrader() {
    if (this.traderLocation == 'local') {
      this.newTrader.location = 'file://' + this.fileLocation; 
      this.traderService.addTrader(this.newTrader).toPromise().then( result => this.refresh());
    }

    this.newTrader = new Trader();
  }

}
