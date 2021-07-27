#from bin.query_db import QueryDB
import sqlite3
from query_db import QueryDB
from sqlite3.dbapi2 import DataError

class DatabaseHandler():
    def __init__(self, date) -> None:
        print(f'connecting to: {date}')
        self.date = date
        self.connection = sqlite3.connect('data.db')
        self.cursor = self.connection.cursor()

    def save(self):
        self.connection.commit()

    def close(self):
        self.connection.close()

    def create_schema(self):
        '''Creates and ensures the schema is correct -- and returns a cursor object'''
        #could use some cleanup
        cur = self.cursor
        #create the table for net_changes. if it exsits, try putting test data into it
        try:
            cur.execute('''CREATE TABLE net_changes
               (DATE text, 
               LASTNAME text, 
               FIRSTNAME text, 
               DESC text, 
               HOURS real, 
               OVERHRS real, 
               SRVTIPS real, 
               TIPOUT real, 
               DECTIPS real, 
               MEALS real )''')
            print('generated new net_changes table')
        except:
            print('using existing net_changes table')
        finally:
            try:
                cur.execute("INSERT INTO net_changes VALUES (?,?,?,?,?,?,?,?,?,?)", 
                    (self.date,'TEST','TEST','*TEST* Added 250 Meals',0,0,0,0,0,250))
            except:
                raise DataError('Schema is invalid')
        #table for daily calculations, to implement a sort of caching system
        try:
            cur.execute('''CREATE TABLE daily_calc_cache
               (date text, 
               current_hash text, 
               tip_rate real, 
               labor_rate real)''')
            print('generated new calc table')
        except:
            print('using existing calc table')
        finally:
            try:
                cur.execute("INSERT INTO daily_calc_cache VALUES (?,?,?,?)", 
                    ('20210230','8a4751c078d26d89ab5a4fe8647e4fafe46d4bde06eec834fa5949d522d40b32', 12.075865365,18.997778955))
            except: 
                raise DataError('Schema is invalid')
        
        self.save()
        return cur
    
    def write_net_changes(self, changes):
        pass
    def write_daily_cache(self, cache):
        pass

if __name__ == '__main__':
    print('loading database.py')
    day = '20210419'
    cur = DatabaseHandler(day).create_schema()
    data = (
        '20210231',
        '8a4751c078d26d89ab5a4fe8647e4fafe46d4bde06eec834fa5949d522d40b32', 
        12.075865365,
        15.997778955
        )
    cur.executemany("INSERT INTO daily_calc_cache VALUES (?,?,?,?)",
        (data))
    print('done')

