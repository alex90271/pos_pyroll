import datetime
import numpy as np
import pandas as pd
import timeit
from cfg import cfg
from dbfread import DBF
#from itertools import izip

class query_db():
    def __init__(self, day: str):
        self.day = day

    def get_day(self):
        return self.day
    
    def dbf_to_list(self, dbf, newdata=False):
        c = cfg()
        d = self.day #use a temp variable so we can change it
        if newdata:
            d = 'Data' #data points to the temp database with the latest data 
        a = DBF(c.query('SETTINGS','database') + d + dbf, char_decode_errors='ignore', load=False)
        return a

    def process_db(self, db_type):
        '''possible options: employees, jobcodes, labor'''
        _dbf = ''
        #print("processing_db")
        if db_type == 'employees':
            a = self.dbf_to_list('/EMP.Dbf')
            df = pd.DataFrame(a, columns=['ID', 'FIRSTNAME', 'LASTNAME', 'TERMINATED']).sort_values(by='ID')
            return df
        elif db_type == 'jobcodes':
            a = self.dbf_to_list('/JOB.Dbf')
            df = pd.DataFrame(a, columns=['ID', 'SHORTNAME']).sort_values(by='ID')
            return df
        elif db_type == 'labor':
            a = self.dbf_to_list('/ADJTIME.DBF')
            db_type = db_type + self.day
            df = pd.DataFrame(a, columns=['SYSDATEIN','INVALID','JOBCODE','EMPLOYEE','HOURS','OVERHRS',
                                          'CCTIPS','DECTIPS','COUTBYEOD','SALES','INHOUR','INMINUTE','OUTHOUR','OUTMINUTE',
                                          'RATE', 'TIPSHCON'])
            df = df.loc[np.where(df['INVALID'] == 'N')] #get rid of any invalid shifts (deleted or shifts that have been edited)
            df['HOURS'] = np.subtract(df['HOURS'].values, df['OVERHRS'].values) #when the data is pulled in and HOURS includes OVERHRS
            return df
        elif db_type == 'transactions':
            db_type = db_type + self.day
            a = self.dbf_to_list('/GNDTndr.dbf')
            df = pd.DataFrame(a)
            df = df.loc[np.where(df['TYPE'] == 1)] #type ID 1 in Aloha Docs are normal transactions
            return df

    def process_names(self, df, rename_columns=True):
        '''takes in a dataframe, with employee IDs and appends the employee name
            assumes the employee number columns is named 'ID'

            this function was implemented to decrese processing time by more than half. 
            Only reads the massive name database and appends right before returning as report
        '''
        #print('adding names')
        job = self.process_db('jobcodes')
        emp = self.process_db('employees')

        if rename_columns:
            emp = emp.rename(columns={'ID':'EMPLOYEE'})
            job = job.rename(columns={'ID': 'JOBCODE'})
            job = job.rename(columns={'SHORTNAME': 'JOB_NAME'})
        else:
            print('process_names function: rename columns is set to false')

        df = df.merge(job, on='JOBCODE')
        df = df.merge(emp, on='EMPLOYEE')

        return df

    def jobcode_list(self):
        ''''returns a list of jobcodes from the latest data'''
        return self.process_db('jobcodes')

    def employee_list(self):
        ''''returns a list of employees from the latest data'''
        return self.process_db('employees')

if __name__ == '__main__':
    print("loading query_db.py")

    def main():
        #print("loading process_tips.py")
        print(query_db("20210520").process_db('jobcodes'))
    r = 1
    f = timeit.repeat("main()", "from __main__ import main", number=1, repeat=r)
    print("completed with an average of " + str(np.round(np.mean(f),6)) + " seconds over " + str(r) + " tries \n total time: " + str(np.round(np.sum(f),3)) + "s")
