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

def get_transactions(session, sim_trader_id):
    return session.query(Transaction).filter(Transaction.simulation_trader_id == sim_trader_id).all()

def get_simulations(session, index=None, length=None):
    query = session.query(SimulationTrader, Simulation, Trader).join(Simulation).join(Trader)
    query = query.order_by(Simulation.simulation_id.desc())
    if index:
        query = query.offset(index*length)
    if length:
        query = query.limit(length)

    return get_clean_data(query.all())

def get_simulation_traders(session, simulation_id=None):
    query = session.query(SimulationTrader, Simulation, Trader).join(Simulation).join(Trader)
    if simulation_id:
        query = query.filter(SimulationTrader.simulation_id == simulation_id)

    return get_clean_data(query.all())
    
def get_clean_data(results):
    data = []
    for result in results:
        row = dict()
        data.append(row)
        for item in result:
            row.update(item.__dict__)
        del row['_sa_instance_state']
    return data
