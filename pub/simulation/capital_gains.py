import decimal
import flask
from flask import request
import flask_restful as restful
from marshmallow import Schema, fields, validate

from api.helpers import success, created
from api.exceptions import NotFound
from api.restful import API

import app_config
from database.simulation import get_transactions_by_sim_trader, get_simulation_traders

@API.route('/capital_gains/<int:simulation_id>/<int:sim_trader_id>', methods=['GET'])
class CapitalGainsTraderHandler (restful.Resource):
    def get(self, simulation_id, sim_trader_id):
        return success(get_capital_gains(get_transactions_by_sim_trader(flask.g.db, sim_trader_id)))

@API.route('/capital_gains/<int:simulation_id>', methods=['GET'])
class CapitalGainsHandler (restful.Resource):
    def get(self, simulation_id):
        sim_traders = get_simulation_traders(flask.g.db, simulation_id)
        return success(get_capital_gains(get_transactions_by_sim_trader(flask.g.db, [trader['simulation_trader_id'] for trader in sim_traders])))

def get_capital_gains(transactions):
    # FIFO, LIFO, Highest Cost, Lowest Cost, Tax Efficient (lowest gains)
    # TODO LIFO what to do with splits
    purchases_by_symbol = dict()
    capital_gains = dict()
    for sim_trader_id in transactions.keys():
        for transaction, symbol in transactions[sim_trader_id]:
            purchases = purchases_by_symbol.setdefault(symbol, [])
            if transaction.transaction_type == 'BUY':
                purchases.append(transaction)
            
            if transaction.transaction_type == 'SPLIT':
                for purchase in purchases:
                    purchase.transaction_quantity = purchase.transaction_quantity * transaction.transaction_quantity
                    purchase.transaction_quantity = purchase.transaction_quantity//1

            if transaction.transaction_type == 'SELL':
                #FIFO
                gain = dict(cost_basis=0, sell_date=transaction.transaction_date, proceeds=transaction.transaction_total, symbol=symbol, 
                            company_id=transaction.company_id, quantity=-1*transaction.transaction_quantity)
                for purchase in purchases:
                    if purchase.transaction_quantity == 0:
                        pass
                    elif purchase.transaction_quantity <= abs(transaction.transaction_quantity):
                        gain['cost_basis'] += purchase.transaction_total
                        purchase.transaction_quantity = 0
                        purchase.transaction_total = 0
                        if 'initial_purchase_date' not in gain:
                            gain['initial_purchase_date'] = purchase.transaction_date
                        if purchase.transaction_quantity == transaction.transaction_quantity:
                            break
                    elif purchase.transaction_quantity > abs(transaction.transaction_quantity):
                        if 'initial_purchase_date' not in gain:
                            gain['initial_purchase_date'] = purchase.transaction_date
                        ratio = decimal.Decimal(abs(transaction.transaction_quantity / purchase.transaction_quantity)) # .5
                        gain['cost_basis'] += purchase.transaction_total * ratio
                        purchase.transaction_quantity -= purchase.transaction_quantity * ratio
                        purchase.transaction_total -= purchase.transaction_total * ratio
                        break
                    else:
                        print("ERROR No case?")
                gains_list = capital_gains.setdefault(sim_trader_id, [])
                gains_list.append(gain)
        for transaction, symbol in transactions[sim_trader_id]:
            if transaction.transaction_type == 'BUY' and transaction.transaction_quantity != 0:
                print('NOT 0 {} {}'.format(symbol, transaction.transaction_quantity))
    return capital_gains
