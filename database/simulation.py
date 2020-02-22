from sqlalchemy import between, and_, distinct
from database.database import Simulation, Transaction, SimulationTrader, Trader

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
    query = session.query(SimulationTrader, Simulation, Trader).join(Simulation).join(Trader)
    query = query.order_by(Simulation.simulation_id.desc())
    if index:
        query = query.offset(index*length)
    if length:
        query = query.limit(length)

    results = query.all()
    data = []
    for result in results:
        row = dict()
        data.append(row)
        for item in result:
            row.update(item.__dict__)
        del row['_sa_instance_state']
    return data

def get_simulation_traders(session, simulation_ids=None):
    query = session.query(SimulationTrader)

    if simulation_ids:
        query = query.where(SimulationTrader.simulation_id.in_(simulation_ids))
    
    return query.all()
