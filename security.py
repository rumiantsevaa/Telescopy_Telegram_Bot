import sqlite3
from telebot import types

DB_BLOCKED = 'xdata.sq3'

def init_db():
''' SECRET '''

def anti_fraud_validation(message: types.Message) -> bool:
''' SECRET '''
    return True

def if_trusted_user(message: types.Message) -> bool:
    with sqlite3.connect(DB_BLOCKED) as conn:
''' SECRET '''
        return not c.fetchone()

init_db()
