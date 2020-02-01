from sqlalchemy import between, and_, distinct
from database.database import Simulation, Transaction, SimulationTrader

def add_simulation(session, start_date, end_date, starting_balance, simulation_date, description):
    sim = Simulation(start_date=start_date, end_date=end_date, starting_balance=starting_balance, 
                     simulation_date=simulation_date, description=description)
    session.add(sim)
    return sim

def add_simulation_trader(session, simulation_id, trader_id):
    sim_trader = SimulationTrader(simulation_id=simulation_id, trader_id=trader_id)
    session.add(sim_trader)
    return sim_trader

def add_transaction(session, sim_trader_id, transaction_date, transaction_quantity, transaction_price, transaction_type, symbol):
    trans = Transaction(simulation_trader_id=sim_trader_id, transaction_date=transaction_date, transaction_quantity=transaction_quantity, transaction_price=transaction_price, transaction_type=transaction_type, symbol=symbol)
    session.add(trans)
    return trans

def get_simulations(session, index=None, length=None):
    query = session.query(Simulation).order_by(Simulation.simulation_id.desc())

    if index:
        query = query.offset(index*length)
    if length:
        query = query.limit(length)

    return query.all()