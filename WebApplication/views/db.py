import sqlite3

def get_db_connection():
    ## dodělat ošetření
    conn = sqlite3.connect('db.sqlite')
    conn.row_factory = sqlite3.Row
    return conn
