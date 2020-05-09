import flask
from flask import request
import flask_restful as restful
from marshmallow import Schema, fields, validate

from api.helpers import success, created
from api.exceptions import NotFound
from api.restful import API

import app_config
from database.simulation import get_transactions

@API.route('/capital_gains/<int:sim_trader_id>', methods=['GET'])
class CapitalGainsHandler (restful.Resource):
    def get(self, sim_trader_id):
        return success(get_capital_gains(get_transactions(flask.g.db, sim_trader_id)))

def get_capital_gains(transactions):
    # FIFO, LIFO, Highest Cost, Lowest Cost, Tax Efficient (lowest gains)
    # TODO LIFO what to do with splits
    purchases_by_symbol = dict()
    capital_gains = []

    for transaction, symbol in transactions:
        purchases = purchases_by_symbol.setdefault(symbol, [])
        if transaction.transaction_type == 'BUY':
            purchases.append(transaction)
        
        if transaction.transaction_type == 'SPLIT':
            for purchase in purchases:
                purchase.transaction_quantity = purchase.transaction_quantity * transaction.transaction_quantity

        if transaction.transaction_type == 'SELL':
            #FIFO
            gain = dict(cost_basis=0, sell_date=transaction.transaction_date, proceeds=transaction.transaction_total, symbol=symbol, 
                        company_id=transaction.company_id, quantity=transaction.transaction_quantity)
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
                    ratio = abs(transaction.transaction_quantity / purchase.transaction_quantity) # .5
                    gain['cost_basis'] += purchase.transaction_total * ratio
                    purchase.transaction_quantity -=  purchase.transaction_quantity * ratio
                    purchase.transaction_total -= purchase.transaction_total * ratio
                    break
                else:
                    print("ERROR No case?")
            capital_gains.append(gain)
    for transaction, symbol in transactions:
        if transaction.transaction_type == 'BUY' and transaction.transaction_quantity != 0:
            print('NOT 0 {} {}'.format(symbol, transaction.transaction_quantity))
    return capital_gains
