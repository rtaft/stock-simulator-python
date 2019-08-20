import app_config
from database.mysql_db import MySQLDatabase
from database.sqlite_db import SQLiteDatabase

def connect():
    #if app_config.DB_TYPE == 'mysql':
    database = MySQLDatabase()
    database.connect(user=app_config.DB_USER, password=app_config.DB_PASS, database=app_config.DB_NAME)
    return database
    #if app_config.DB_TYPE == 'sqlite':
    #    database = SQLiteDatabase()
    #    database.connect(database=app_config.DB_NAME)
    #    return database
