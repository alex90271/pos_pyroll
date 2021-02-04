# python -m pip install tkcalendar
# python -m pip install pandas
# python -m pip install dbfread
# python -m pip install xlsxwriter
# python -m pip install python-quickbooks

import pandas as pd 
import configparser
import os
import datetime
import timeit
import numpy as np
from dbfread import DBF

def day_list(first_day: datetime, last_day: datetime, increment = 1):
    '''converts a start date and an end date into a list of all dates in between, based on the increment value'''

    if type(first_day) and type(last_day) == str:
        first_day = datetime.datetime.strptime(first_day, "%Y%m%d")
        last_day = datetime.datetime.strptime(last_day, "%Y%m%d")
    elif type(first_day) or type(last_day) != str or datetime.date:
        raise TypeError('must pass datetime or string')

    delta = datetime.timedelta(days=increment)
    days = []

    while first_day <= last_day:
        #cur_day = first_day.strftime("%Y%m%d")
        days.append(first_day)
        first_day += delta
    
    return days

class Config():

    def __init__(self, file_name='config2.ini'):
        self.file_name = file_name
        self.config = configparser.ConfigParser()

    def generate_config (self):
        self.config['DEFAULT'] = {
                            'tip_sales_percent': 0.03,
                            'tip_amt_percent': 100,
                            'percent_sale_codes': 1,
                            'percent_tip_codes': 11, 
                            'tipped_codes': '2,3,5,10,11,12,13,14', 
                            'tracked_labor': 8, 
                            'pay_period_days': 15,
                            'count_salary': True, 
                            'debug': False,
                            'database': 'D:\\Bootdrv\\Aloha\\',# set config.ini to database\ for testing
                            'use_aloha_tipshare': True
                            }
        with open (self.file_name, 'w') as configfile:
            self.config.write(configfile)

    def query (self, query):
        '''returns config settings as a string

            Ex. usage for single config settings
            query('database') = 'D:\\Bootdrv\\Aloha\\'
            
            possible options: 
            register, server, tipout_recip, tip_percent,
            tracked_labor, pay_period, debug, database, and salary
        '''

        if os.path.isfile(self.file_name):
            self.config.read(self.file_name)
        else:
            print ('generating new ' + self.file_name)
            self.generate_config()

        return self.config.get("DEFAULT", query)

class DatabaseQuery():
    def __init__(self, day):
        self.day = day
    
    def set_day(self, day):
        self.day = day
    
    def set_dbloc(self, db_loc):
        self.db_loc = db_loc

    def get_day(self):
        return self.day
    
    def dbf_to_list(self, dbf):
        c = Config()
        a = []
        for record in DBF(c.query('database') + self.day + dbf, char_decode_errors='ignore'):
            a.append(record)
        return a

    def process_df(self, db_type):
        _dbf = ''
        if db_type == 'employees':
            a = self.dbf_to_list('/EMP.Dbf')
            df = pd.DataFrame(a, columns=['ID', 'FIRSTNAME', 'LASTNAME', 'TERMINATED'])
            df.set_index('ID')
            return df
        elif db_type == 'jobcodes':
            a = self.dbf_to_list('/JOB.Dbf')
            df = pd.DataFrame(a, columns=['ID', 'SHORTNAME'])
            df.set_index('ID')
            return df
        elif db_type == 'labor':
            a = self.dbf_to_list('/ADJTIME.DBF')
            db_type = db_type + self.day
            df = pd.DataFrame(a, columns=['SYSDATEIN','INVALID','JOBCODE','EMPLOYEE','HOURS','OVERHRS','CCTIPS','DECTIPS','COUTBYEOD','SALES','INHOUR','INMINUTE','OUTHOUR','OUTMINUTE','RATE', 'TIPSHCON'])
            df = df.loc[df['INVALID'] == 'N']
            df.set_index('EMPLOYEE')
            return df

    def process_names(self, *df):
        job = self.process_df('jobcodes')
        job = job.rename(columns={'ID': 'JOBCODE'})
        job = job.rename(columns={'SHORTNAME': 'JOB_NAME'})

        emp = self.process_df('employees')
        emp = emp.rename(columns={'ID':'EMPLOYEE'})

        if df is not None:
            df = self.process_df('labor')
        else:
            df = df[0]

        df = df.merge(job, on='JOBCODE')
        df = df.merge(emp, on='EMPLOYEE')
        return df

class Labor_Process():
    #'SYSDATEIN','INVALID','JOBCODE','EMPLOYEE','HOURS','OVERHRS','CCTIPS','DECTIPS','COUTBYEOD','SALES','INHOUR','INMINUTE','OUTHOUR','OUTMINUTE','RATE', 'SALES'
    def __init__(self, day):
        d = DatabaseQuery(day)
        c = Config()
        self.percent_tips_codes = c.query('percent_tip_codes').split(',') #jobcodes that contribute based on a percentage of tips
        self.percent_sales_codes = c.query('percent_sale_codes').split(',') #jobcodes that contribute based on a percentage of sales
        self.tipped_code = c.query('tipped_codes').split(',')
        self.sales_percent = float(c.query('tip_sales_percent'))
        self.tip_percent = float(c.query('tip_amt_percent'))
        self.tracked_labor = c.query('tracked_labor').split(',')
        self.pay_period = int(c.query('pay_period_days'))
        self.use_aloha_tipshare = bool(c.query('use_aloha_tipshare'))
        self.df = d.process_names()
        self.total_pool = 0
        self.to_cctip = 0
        self.to_cashtip = 0

    def get_percent_sales(self):
        '''returns tip share from server jobcodes'''
        cur_df = self.df.loc[self.df['JOBCODE'].isin(self.percent_sales_codes)]
        total = 0

        if self.use_aloha_tipshare:
            total = cur_df['TIPSHCON'].sum()
        else:
            total = cur_df['SALES'].sum() * self.sales_percent

        return total

    def get_percent_tips(self):
        '''returns tip share from register jobcodes'''
        cur_df = self.df.loc[self.df['JOBCODE'].isin(self.percent_tips_codes)]
        total = cur_df['CCTIPS'].sum() + cur_df['DECTIPS'].sum()

        return total

if __name__ == '__main__':
    b = Labor_Process('20210106')
    pool = b.get_percent_tips()
    print(pool)


