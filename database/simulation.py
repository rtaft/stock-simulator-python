from sqlalchemy import between, and_, distinct
from database.database import Simulation, Transaction

def add_simulation(session, start_date, end_date, starting_balance, simulation_date, trader_id, description):
    sim = Simulation(start_date=start_date, end_date=end_date, starting_balance=starting_balance, 
                     simulation_date=simulation_date, trader_id=trader_id, description=description)
    session.add(sim)
    return sim

def add_transaction(session, simulation_id, transaction_date, transaction_quantity, transaction_price, transaction_type, symbol):
    trans = Transaction(simulation_id=simulation_id, transaction_date=transaction_date, transaction_quantity=transaction_quantity, transaction_price=transaction_price, transaction_type=transaction_type, symbol=symbol)
    session.add(trans)
    return trans