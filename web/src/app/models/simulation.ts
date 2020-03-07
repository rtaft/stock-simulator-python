export class Simulation {
    simulation_id: number;
    simulation_date: Date;
    description: string;
    starting_balance: number;
    start_date: Date;
    end_date: Date;
              
}

export class SimulationStatus {
    status: string;
}

export class SimulationTrader {
    simulation_trader_id: number;
    simulation_id: number;
    trader_id: number;
    ending_value: number;
    description: string;
    end_date: string;
    simulation_date: Date;
    starting_balance: number;
    start_date: string;
    name: string;
}

export class Transaction {
    transaction_id: number;
    simulation_trader_id: number;
    transaction_date: Date;
    transaction_price: number;
    transaction_type: string;
    transaction_quantity: number;
    symbol: string;
}
