import psycopg2
from psycopg2.extras import RealDictCursor
import logging

def get_connection():
    return psycopg2.connect(
        dbname="telegram_bot_db",
        user="postgres",
        password="qwas12",
        host="localhost",
        port="5432"
    )
