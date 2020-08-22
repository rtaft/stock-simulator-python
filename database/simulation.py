from sqlalchemy import between, and_, distinct
from database.database import Company, Simulation, Transaction, SimulationTrader, Trader

def add_simulation(session, start_date, end_date, simulation_date, description, stock_list):
    sim = Simulation(start_date=start_date, end_date=end_date, simulation_date=simulation_date, 
                     description=description, stock_list=stock_list)
    session.add(sim)
    return sim

def add_simulation_trader(session, simulation_id, trader_id, starting_balance, description, params):
    sim_trader = SimulationTrader(simulation_id=simulation_id, trader_id=trader_id, starting_balance=starting_balance, 
                                  description=description, params=params)
    print(sim_trader)
    session.add(sim_trader)
    return sim_trader

def add_transaction(session, sim_trader_id, transaction_date, transaction_quantity, transaction_price, transaction_tax,
                    transaction_type, transaction_total, company_id):
    trans = Transaction(simulation_trader_id=sim_trader_id, transaction_date=transaction_date, transaction_quantity=transaction_quantity, 
                        transaction_price=transaction_price, transaction_tax=transaction_tax, transaction_type=transaction_type, transaction_total=transaction_total, company_id=company_id)
    session.add(trans)
    return trans

def get_transactions(session, sim_trader_id):
    return session.query(Transaction, Company.symbol).filter(Company.company_id == Transaction.company_id).filter(Transaction.simulation_trader_id == sim_trader_id).all()

def get_transactions_by_sim_trader(session, sim_trader_ids):
    if not isinstance(sim_trader_ids, list):
        sim_trader_ids = [sim_trader_ids]
    results = session.query(Transaction, Company.symbol).filter(Company.company_id == Transaction.company_id).filter(Transaction.simulation_trader_id.in_(sim_trader_ids)).all()
    transactions = dict()
    for result in results:
        grouped_transactions = transactions.setdefault(result[0].simulation_trader_id, [])
        grouped_transactions.append(result)
    return transactions

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
