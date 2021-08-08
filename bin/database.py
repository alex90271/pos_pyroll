#from bin.query_db import QueryDB
import sqlite3
from query_db import QueryDB
from sqlite3.dbapi2 import DataError

class DatabaseHandler():
    def __init__(self, date) -> None:
        #print(f'connecting to: {date}')
        self.date = date
        self.connection = sqlite3.connect('data.db')
        self.cursor = self.create_schema()

    def save(self):
        self.connection.commit()

    def close(self):
        self.connection.close()

    def create_schema(self):
        '''Creates and ensures the schema is correct -- and returns a cursor object'''
        #could use some cleanup
        cur = self.connection.cursor()

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
            #print('generated new net_changes table')
        except:
            #print('using existing net_changes table')
            pass

        #table for daily calculations, to implement a sort of caching system
        try:
            cur.execute('''CREATE TABLE daily_calc_cache
               (date text, 
               current_hash text, 
               tip_rate real, 
               labor_rate real)''')
            #print('generated new calc table')
        except:
            #print('using existing calc table')
            pass
        
        self.save()
        return cur
    
    def read_db(self, table, query):
        pass
    
    def write_net_changes(self,  
               LASTNAME, 
               FIRSTNAME, 
               DESC, 
               HOURS, 
               OVERHRS, 
               SRVTIPS, 
               TIPOUT, 
               DECTIPS, 
               MEALS):
        changes =[self.date, LASTNAME, FIRSTNAME, DESC, HOURS, OVERHRS, SRVTIPS, TIPOUT, DECTIPS, MEALS]
        self.cursor.executemany("INSERT INTO net_changes VALUES (?,?,?,?,?,?,?,?,?,?)", [changes])
        self.save()
        return True

    def write_daily_cache(self, CURRENT_HASH, TIP_RATE, LABOR_RATE):
        #cache = ('20210231','8a4751c078d26d89ab5a4fe8647e4fafe46d4bde06eec834fa5949d522d40b32', 12.075865365,15.997778955)
        cache = [self.date, CURRENT_HASH, TIP_RATE, LABOR_RATE]
        self.cursor.executemany("INSERT INTO daily_calc_cache VALUES (?,?,?,?)", [cache])
        self.save()
        return True

    def get_data(self, table):
        '''returns a list with the daily cache for the initialized day'''
        data = self.cursor.execute(f"SELECT * FROM {table} WHERE DATE={self.date}") ##NOT FOR PRODUCTION. INSECURE
        fetched = data.fetchone()
        if fetched == None:
            return False
        else: 
            return fetched

if __name__ == '__main__':
    print('loading database.py')
    day = '20210231'

    db = DatabaseHandler(day)
    #db.write_daily_cache('8a4751c078d26d89ab5a4fe8647e4fafe46d4bde06eec834fa5949d522d40b32', 999.075865365, 999.075865365)
    #db.write_net_changes('Alex', 'Alder', 'test change', 0, 4, 0, 10, 0, 10)

    print(db.get_data('net_changes'))
    print(db.get_data('daily_calc_cache'))
    
    print('done')

