import json
import random
import pandas as pd
#chose July 4th - 10th as that is a Sunday through Saturday
class Debugger():

    def __init__(self, debug_name='chip.debug'):
        self.debug_name = 'data/'+debug_name

    def gen_int(self, top, bottom):
        return random.randint(top, bottom)
    
    def gen_data_dbfs(self, db_type):
        data = []
        if db_type == 'EMP': #needs 10 employees
            names = [
                    ('Daenerys','Targaryen'),('Cersei','Lannister'),
                    ('Robert','Baratheon'),('Tyrion','Lannister'),
                    ('Samwell','Tarly'),('Jeor','Mormont'),
                    ('Brienne','of Tarth'),('Sansa','Stark'),
                    ('Ed','Stark'),('John','Snow')
                    ]
            data_header = ['ID', 'FIRSTNAME', 'LASTNAME', 'TERMINATED', 'JOBCODE1']
            for i in range(1001,1011):
                data.append([i,names[i-1001][0],names[i-1001][1],'N', self.gen_int(1,5)])
            data.append([2001,'Harold','Terminated','Y', 1])

        elif db_type == 'JOBCODES': #needs 5 jobcodes
            names=['Server','Host','Kitchen','Dish','Takeout'] #1,2,3,4,5
            data_header = ['ID', 'SHORTNAME']
            for i in range(0,5):
                data.append([i+1,names[i]])

        #print(data)
        return pd.DataFrame(data, columns=data_header)


    def generate_debug_db(self, datestr):
        '''generates the default config file, with default settings. To reset config file, just delete it'''
        header = ['SYSDATEIN','INVALID','JOBCODE','EMPLOYEE','HOURS','OVERHRS','CCTIPS','AUTGRTTOT','DECTIPS','COUTBYEOD','SALES','INHOUR','INMINUTE','OUTHOUR','OUTMINUTE','RATE','TIPSHCON','EXP_ID']
        data = []
        for i in range (0,5):
            data.append([datestr, #sysdate
                    'N', #invalid
                    self.gen_int(1,5), # 5 jobcodes
                    self.gen_int(1001,1010), #10 employee numbers
                    self.gen_int(6,10), #hours
                    self.gen_int(0,5), #overtime
                    self.gen_int(75,150), #CCtips
                    self.gen_int(0,25), #auto gratuity
                    self.gen_int(0,5), #decl tips
                    'N', #coutbyeod
                    self.gen_int(400,1700), #sales
                    '8', #inhour
                    '00', #inminute
                    '22', #outhour
                    '00', #outminute
                    20,
                    30, 
                    0]
            )
        return [header,data]


if __name__ == '__main__':
    print("loading debugger.py")
    d = Debugger().generate_debug_db("20210920")
    print(pd.DataFrame(data=d[1], columns=d[0]))
    print(Debugger().gen_data_dbfs('JOBCODES'))
    print(Debugger().gen_data_dbfs('EMP'))