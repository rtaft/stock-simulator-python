import { Component, OnInit} from '@angular/core';

import { TraderService } from '../services/traders';

@Component({
  selector: 'app-traders',
  templateUrl: './traders.component.html',
  styleUrls: ['./traders.component.scss']
})
export class TradersComponent  implements OnInit {
  traders = []
  constructor(private traderService: TraderService) { }

  ngOnInit() {
    this.traderService.listTraders().toPromise().then( result => this.traders = result)
  }

}
