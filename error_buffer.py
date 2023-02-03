# A class encapuslating a buffer that holds errors. In this implementation, we do that using a SQLite database. 
import os
import sqlite3
import datetime

class ErrorBuffer:
    DATABASE_FILENAME = "errors_database.db"
    DATABASE_NAME = "errors"

    # A simple constructor
    def __init__(self):
        super().__init__()
        self.con = self.get_database_connection()
    
    # Gets a connection to the database, setting one up if necessary
    @classmethod
    def get_database_connection(cls):
        if not os.path.isfile(cls.DATABASE_FILENAME): print("Database file not found; creating...")
        con = sqlite3.connect(cls.DATABASE_FILENAME)
        cur = con.cursor()
        if not (cls.DATABASE_NAME,) in cur.execute("SELECT name FROM sqlite_master").fetchall():
            print("Database table not found; creating...")
            cur.execute(f"CREATE TABLE {cls.DATABASE_NAME}(timestamp, message)")
        con.commit()
        return con
    
    # Add an entry to the ErrorBuffer
    def append(self, msg):
        cur = self.con.cursor()
        timestamp = datetime.datetime.now().timestamp()
        cur.execute(f"INSERT INTO {self.DATABASE_NAME} VALUES (?, ?)", (timestamp, msg))
        self.con.commit()
    
    # Get the entire contents of the ErrorBuffer as a list of strings
    def to_list(self):
        cur = self.con.cursor()
        result_packed = cur.execute("SELECT message from errors ORDER BY timestamp ASC").fetchall()
        self.con.commit()
        return [tup[0] for tup in result_packed]
    
    # Get the number of entries in the ErrorBuffer
    def num_entries(self):
        cur = self.con.cursor()
        result_packed = cur.execute("SELECT COUNT(*) from errors ORDER BY timestamp ASC").fetchall()
        self.con.commit()
        return result_packed[0][0]
    
    # Delete all entries from the ErrorBuffer
    def clear(self):
        cur = self.con.cursor()
        cur.execute(f"DELETE FROM {self.DATABASE_NAME}")
        self.con.commit()
