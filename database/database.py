# coding: utf-8
from sqlalchemy import CHAR, Column, Date, Float, ForeignKey, Index, String, TIMESTAMP, Table, text
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Company(Base):
    __tablename__ = 'company'

    company_id = Column(INTEGER(11), primary_key=True)
    company_name = Column(String(100))
    symbol = Column(String(10), nullable=False)
    exchange = Column(String(10), nullable=False)
    ipo = Column(INTEGER(11))
    sector = Column(String(60))
    industry = Column(String(255))
    error = Column(CHAR(1))


class DividendHistory(Base):
    __tablename__ = 'dividend_history'

    dividend_id = Column(INTEGER(11), primary_key=True)
    company_id = Column(INTEGER(11), nullable=False, index=True)
    ex_date = Column(Date)
    dividend = Column(Float, nullable=False)


t_price_history = Table(
    'price_history', metadata,
    Column('company_id', INTEGER(11), nullable=False),
    Column('trade_date', Date, nullable=False, index=True),
    Column('trade_close', Float, nullable=False),
    Column('trade_volume', INTEGER(11), nullable=False)
)


t_price_history.bak = Table(
    'price_history.bak', metadata,
    Column('company_id', INTEGER(11), nullable=False),
    Column('trade_date', Date, nullable=False, index=True),
    Column('trade_close', Float, nullable=False),
    Column('trade_volume', INTEGER(11), nullable=False)
)


class Simulation(Base):
    __tablename__ = 'simulation'

    simulation_id = Column(INTEGER(11), primary_key=True)
    simulation_date = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    description = Column(String(2000))
    stock_list = Column(String(50))


class SplitHistoryBak(Base):
    __tablename__ = 'split_history.bak'

    split_id = Column(INTEGER(11), primary_key=True)
    company_id = Column(INTEGER(11), nullable=False, index=True)
    split_date = Column(Date)
    ratio = Column(Float, nullable=False)


class SplitHistoryBak2(Base):
    __tablename__ = 'split_history.bak2'

    split_id = Column(INTEGER(11), primary_key=True)
    company_id = Column(INTEGER(11), nullable=False, index=True)
    split_date = Column(Date)
    ratio = Column(Float, nullable=False)


class StockList(Base):
    __tablename__ = 'stock_list'

    list_id = Column(INTEGER(11), primary_key=True)
    name = Column(String(50), nullable=False)


class Trader(Base):
    __tablename__ = 'traders'

    trader_id = Column(INTEGER(11), primary_key=True)
    name = Column(String(255), nullable=False)
    location = Column(String(2000), nullable=False)


class DividendHistoryBak(Base):
    __tablename__ = 'dividend_history.bak'

    dividend_id = Column(INTEGER(11), primary_key=True)
    company_id = Column(ForeignKey('company.company_id'), nullable=False, index=True)
    ex_date = Column(Date)
    dividend = Column(Float, nullable=False)

    company = relationship('Company')


class SimulationTrader(Base):
    __tablename__ = 'simulation_trader'
    __table_args__ = (
        Index('simulation_id', 'simulation_id', 'trader_id', unique=True),
    )

    simulation_trader_id = Column(INTEGER(11), primary_key=True)
    simulation_id = Column(ForeignKey('simulation.simulation_id'), nullable=False)
    trader_id = Column(ForeignKey('traders.trader_id'), nullable=False, index=True)
    ending_value = Column(Float(asdecimal=True))
    starting_balance = Column(Float(asdecimal=True))

    simulation = relationship('Simulation')
    trader = relationship('Trader')


class SplitHistory(Base):
    __tablename__ = 'split_history'

    split_id = Column(INTEGER(11), primary_key=True)
    company_id = Column(ForeignKey('company.company_id'), nullable=False, index=True)
    split_date = Column(Date)
    ratio = Column(Float, nullable=False)

    company = relationship('Company')


class StockListDatum(Base):
    __tablename__ = 'stock_list_data'

    data_id = Column(INTEGER(11), primary_key=True)
    company_id = Column(ForeignKey('company.company_id'), nullable=False, index=True)
    list_id = Column(ForeignKey('stock_list.list_id'), nullable=False, index=True)
    date_added = Column(Date)
    date_removed = Column(Date)

    company = relationship('Company')
    list = relationship('StockList')


class Transaction(Base):
    __tablename__ = 'transaction'

    transaction_id = Column(INTEGER(11), primary_key=True)
    simulation_trader_id = Column(ForeignKey('simulation_trader.simulation_trader_id'), nullable=False, index=True)
    transaction_date = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    transaction_price = Column(Float, nullable=False)
    transaction_type = Column(String(10), nullable=False)
    transaction_quantity = Column(Float(asdecimal=True), nullable=False)
    transaction_total = Column(Float(asdecimal=True), nullable=False)
    company_id = Column(ForeignKey('company.company_id'), nullable=False, index=True)
    transaction_tax = Column(Float, nullable=False, server_default=text("'0'"))

    company = relationship('Company')
    simulation_trader = relationship('SimulationTrader')
