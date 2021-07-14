import datetime
import numpy as np
import pandas as pd
import timeit
from chip_config import ChipConfig
from dbfread import DBF
#from itertools import izip

class QueryDB():
    '''
        The QueryDB class is used to access data from the Aloha Database
        Currently supports: Labor, Jobcodes, Employee Names, and Total Sales.
        WIP: Transaction data. Currently, cannot access live Aloha data, restricted to previous dates of buisness

        set 'Data' to the desired date for processing. Ex. 20210711 = July 11th, 2021
        leave empty for 'Today'
    '''
    def __init__(self, data=''):
        if data == datetime.datetime.today().strftime("%Y%m%d"): #if the date is TODAY, use latest data
            self.data = 'Data'
            print('WARNING: Using data from the Data folder. This data should be considered unoffical and may change')
        elif data == '': #if the data is left empty, it assumes you want to access the latest data
            self.data = 'Data'
        elif data > datetime.datetime.today().strftime("%Y%m%d"): #if someone tries to use a future day, throw an error. 
            raise ValueError('ERROR: Future data cannot be used. It does not exist')
        else:
            self.data = data #data, meaning the date folder

    def get_day(self):
        return self.data
    
    def dbf_to_list(self, dbf):
        '''takes in a database object and reads it as a list for further processing'''
        c = ChipConfig()
        a = DBF(c.query('SETTINGS','database') + self.data + dbf, char_decode_errors='ignore', load=False)
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
            if self.data == 'Data':
                raise ValueError('ERROR: NO DATE GIVEN FOR LABOR DATA')
            a = self.dbf_to_list('/ADJTIME.DBF')
            db_type = db_type + self.data
            df = pd.DataFrame(a, columns=['SYSDATEIN','INVALID','JOBCODE','EMPLOYEE','HOURS','OVERHRS',
                                          'CCTIPS','DECTIPS','COUTBYEOD','SALES','INHOUR','INMINUTE','OUTHOUR','OUTMINUTE',
                                          'RATE', 'TIPSHCON'])
            df = df.loc[np.where(df['INVALID'] == 'N')] #get rid of any invalid shifts (deleted or shifts that have been edited)
            df['HOURS'] = np.subtract(df['HOURS'].values, df['OVERHRS'].values) #when the data is pulled in and HOURS includes OVERHRS
            return df
        elif db_type == 'transactions': #this isn't used yet
            if self.data == 'Data':
                raise ValueError('ERROR: NO DATE GIVEN FOR TRANSACTION DATA')
            db_type = db_type + self.data
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
    print("loading QueryDB.py")

    def main():
        #print("loading process_tips.py")
        print(QueryDB("20210712").process_db('jobcodes'))
    r = 1
    f = timeit.repeat("main()", "from __main__ import main", number=1, repeat=r)
    print("completed with an average of " + str(np.round(np.mean(f),6)) + " seconds over " + str(r) + " tries \n total time: " + str(np.round(np.sum(f),3)) + "s")
