import { Component, Inject, OnInit } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material';
import { TraderService } from '../services/traders';
import { Trader } from '../models/trader';

@Component({
  selector: 'app-add-trader',
  templateUrl: './add-trader.component.html',
  styleUrls: ['./add-trader.component.scss']
})
export class AddTraderComponent implements OnInit {
  schema: any;
  selectedTrader: string;
  traders: Trader[];

  constructor(private traderService: TraderService,
             public dialogRef: MatDialogRef<AddTraderComponent>, 
             @Inject(MAT_DIALOG_DATA) public data: Trader[]) {
    this.traders = data;
  }

  ngOnInit() {

  }

  validate() {
    if (this.selectedTrader && this.schema) {
      for (const item of this.schema) {
        if (!item['value'] && item['required']) {
          return false;
        }
      }
      return true;
    }
    return false;
  }

  titleCase(text: string) {
    return text.replace('_', ' ').toLowerCase().split(' ').map((word) => word.replace(word[0], word[0].toUpperCase())).join(' ');
  }

  selectTrader() {
    this.traderService.getSchema(parseInt(this.selectedTrader)).toPromise().then(result => {
      let traderName = '';
      for (const trader of this.data) {
        if (trader['trader_id'] == parseInt(this.selectedTrader)) {
          traderName = trader['name']
        }
      }
      this.schema = [{title: "trader_id", value:this.selectedTrader}, {title: "trader_name", value: traderName},]
      if (result) {
        for (const key of Object.keys(result)) {
          this.schema.push(result[key]);
          if (!result[key]['fieldname']) {
            result[key]['fieldname'] = this.titleCase(key);
          }
        }
      }
    });
  }

  add() {
    const data = {}
    for (const item of this.schema) {
      data[item['title']] = item;
    }
    this.dialogRef.close(data);
  }

  cancel() {
    this.dialogRef.close();
  }

}
