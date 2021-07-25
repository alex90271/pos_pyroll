import sqlite3

class DatabaseHandler():
    def __init__(self, date) -> None:
        print(f'connecting to: {date}')
        self.date = date
        self.connection = sqlite3.connect('data.db')
        self.cursor = self.connection.cursor()

    def save(self):
        self.connection.commit()
        self.connection.close()

    def create_schema(self):
        cur = self.cursor
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
            cur.execute("INSERT INTO net_changes VALUES (?,?,?,?,?,?,?,?,?,?)", (self.date,'TEST','TEST','*TEST* Added 250 Meals',0,0,0,0,0,250))

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
            cur.execute("INSERT INTO daily_calc_cache VALUES (?,?,?,?)", ('20210230','8a4751c078d26d89ab5a4fe8647e4fafe46d4bde06eec834fa5949d522d40b32', 12.075865365,18.997778955))
        
        self.save()

if __name__ == '__main__':
    print('loading database.py')
    DatabaseHandler('20210419').create_schema()
