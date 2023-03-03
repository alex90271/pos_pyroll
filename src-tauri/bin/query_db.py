import datetime
import numpy as np
import pandas as pd
import timeit
import os
from debug import Debugger
from chip_config import ChipConfig
from dbfread import DBF

from debug import Debugger
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
        #print("DATA:",data)
        if data == datetime.datetime.today().strftime("%Y%m%d"): #if the date is TODAY, use latest data
            self.data = 'Data'
            #print('WARNING: Using data from the Data folder. This data should be considered unoffical and may change')
        elif data == '': #if the data is left empty, it assumes you want to access the latest data
            #print('WARNING: Using data from the Data folder. This data should be considered unoffical and may change')
            self.data = 'Data'
        elif data > datetime.datetime.today().strftime("%Y%m%d"): #if someone tries to use a future day, throw an error. 
            raise ValueError('ERROR: Future data cannot be used. It does not exist')
        else:
            self.data = data #data, meaning the date folder

        if ChipConfig().query('SETTINGS','debug'):
            try:
                count = os.environ['debug_db_warning_count_var']
            except:
                print('RUNNING DEBUG DATABASE [query_db.py)]')
            os.environ['debug_db_warning_count_var'] = 'True'

    def get_day(self):
        return self.data
    
    def dbf_to_list(self, dbf):
        '''takes in a database object and reads it as a list for further processing'''
        path = ChipConfig().query('SETTINGS','database')
        dbf_list = pd.DataFrame([])
        if ChipConfig().query('SETTINGS','debug'):
            if dbf == '/ADJTIME.DBF':
                return Debugger().generate_debug_db(self.data)

            elif dbf == '/EMP.Dbf':
                a = Debugger().gen_data_dbfs('EMP')
                return a

            elif dbf == '/JOB.Dbf':
                a = Debugger().gen_data_dbfs('JOBCODES')
                return a
            
        try:
            dbf_list = DBF(path + self.data + dbf, char_decode_errors='ignore', load=False)
        except:
            print(path + self.data + dbf + ' could not be accessed or does not exist')
    
        return dbf_list

    def process_db(self, db_type):
        '''possible options: employees, jobcodes, labor'''
        #print("processing_db")
        if db_type == 'employees':
            a = self.dbf_to_list('/EMP.Dbf')
            if ChipConfig().query('SETTINGS','debug'):
                d = pd.DataFrame(a)
            else:
                d = pd.DataFrame(a, columns=['ID', 'FIRSTNAME', 'LASTNAME', 'TERMINATED']).sort_values(by='ID')
            return d
        elif db_type == 'jobcodes':
            a = self.dbf_to_list('/JOB.Dbf')
            if ChipConfig().query('SETTINGS','debug'):
                d = pd.DataFrame(a)
            else:
                d = pd.DataFrame(a, columns=['ID', 'SHORTNAME']).sort_values(by='ID')
            return d
        elif db_type == 'labor':
            if self.data == 'Data':
                raise ValueError('ERROR: NO DATE GIVEN FOR LABOR DATA')
            a = self.dbf_to_list('/ADJTIME.DBF')
            if ChipConfig().query('SETTINGS','debug'):
                data = pd.DataFrame(pd.DataFrame(data=a[1], columns=a[0]))
                return data
            else:
                db_type = db_type + self.data
                df = pd.DataFrame(a, columns=['SYSDATEIN','INVALID','JOBCODE','EMPLOYEE','HOURS','OVERHRS',
                                            'CCTIPS','DECTIPS','COUTBYEOD','SALES','INHOUR','INMINUTE','OUTHOUR','OUTMINUTE',
                                            'RATE', 'TIPSHCON', 'EXP_ID'])
                df = df.loc[np.where(df['INVALID'] == 'N')] #get rid of any invalid shifts (deleted or shifts that have been edited)
                df['HOURS'] = np.subtract(df['HOURS'].values, df['OVERHRS'].values) #when the data is pulled in and HOURS includes OVERHRS
                return df

        elif db_type == 'transactions': #this isn't used yet
            if self.data == 'Data':
                raise ValueError('ERROR: NO DATE GIVEN FOR TRANSACTION DATA')
            a = self.dbf_to_list('/GNDTndr.dbf')
            df = pd.DataFrame(a)
            return df
        
        elif db_type == 'house_acct':
            if self.data == 'Data':
                raise ValueError('ERROR: NO DATE GIVEN FOR TRANSACTION DATA')
            a = self.dbf_to_list('/HSE.DBF')
            df = pd.DataFrame(a)
            return df
        
        elif db_type == 'labor_hourly':
            shared_cols = ['DOB','STARTHOUR','STARTMIN','STOPHOUR','STOPMIN', 'STOREID', 'REGIONID', 'OCCASIONID']
            if self.data == 'Data':
                raise ValueError('ERROR: NO DATE GIVEN FOR LABOR DATA')
            a_df = pd.DataFrame(self.dbf_to_list('/GNDLBSUM.DBF')) #15 minute intervals of sales
            b_df = pd.DataFrame(self.dbf_to_list('/GNDSLSUM.DBF')) #15 minute invervales of labor cost
            try:
                b_df = b_df.loc[np.where(b_df['KEYVOLUME'] == 1)]
                b_df = b_df.loc[np.where(b_df['CATID'] == 10)]
                b_df.drop(columns=['REVID', 'CATID', 'KEYVOLUME'], axis=1, inplace=True)
            except:
                print(self.data +' was empty')
                return pd.DataFrame([])
            df = a_df.merge(b_df, on=shared_cols, how='left') #merge them on their shared columns and return the result
            return df

    def process_names(self, df, rename_columns=True, emp_bool=True, job_bool=True):
        '''takes in a dataframe, with employee IDs and appends the employee name
            assumes the employee number columns is named 'ID'

            this function was implemented to decrese processing time by more than half. 
            Only reads the massive name database and appends right before returning as report
        '''
        #print('adding names')
        if job_bool:
            job = self.process_db('jobcodes')
        if emp_bool:
            emp = self.process_db('employees')

        if rename_columns:
            if emp_bool:
                emp.rename(columns={'ID':'EMPLOYEE'}, inplace=True)
                #print(emp)
            if job_bool:
                job.rename(columns={'ID': 'JOBCODE'}, inplace=True)
                job.rename(columns={'SHORTNAME': 'JOB_NAME'},inplace=True)
                #print(job)
        else:
            print('process_names function: rename columns is set to false')

        if job_bool:
            df = df.merge(job, on='JOBCODE')
        if emp_bool:
            df = df.merge(emp, on='EMPLOYEE')

        return df

    def return_jobname(self, job_num):
        df = self.process_db('jobcodes')
        df = df.loc[df['ID'].isin(job_num)]

        return df['SHORTNAME'].to_list()

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
        result = QueryDB("20210803").process_db('labor')
        print(result)
    r = 1
    f = timeit.repeat("main()", "from __main__ import main", number=1, repeat=r)
    print("completed with an average of " + str(np.round(np.mean(f),6)) + " seconds over " + str(r) + " tries \n total time: " + str(np.round(np.sum(f),3)) + "s")
