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
                            'database': 'D:\\Bootdrv\\Aloha\\', # set config.ini to database\ for testing
                            'use_aloha_tipshare': False
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

    def gen_salary(self, data={'FIRSTNAME':['TEST'], 'LASTNAME':['TEST'], 'RATE':[0], 'HOURS':[0], 'OVERHRS':[0], 'JOB_NAME':['Salary']}):
        df = pd.DataFrame(data=data)
        df.to_csv('salary.csv')

    def get_total_sales(self):
        df = self.process_df('labor')
        return np.sum(df.loc[:,('SALES')])

class Labor_Process():
    #'SYSDATEIN','INVALID','JOBCODE','EMPLOYEE','HOURS','OVERHRS','CCTIPS','DECTIPS','COUTBYEOD','SALES','INHOUR','INMINUTE','OUTHOUR','OUTMINUTE','RATE', 'SALES'

    def __init__(self, day):
        c = Config()
        self.db = DatabaseQuery(day)
        self.df = self.db.process_names()
        self.day = day
        #config options
        self.percent_tips_codes = c.query('percent_tip_codes').split(',') #jobcodes that contribute based on a percentage of tips
        self.percent_sales_codes = c.query('percent_sale_codes').split(',') #jobcodes that contribute based on a percentage of sales
        self.tipped_code = c.query('tipped_codes').split(',') #jobcodes that receive
        self.sales_percent = float(c.query('tip_sales_percent'))
        self.tip_percent = float(c.query('tip_amt_percent'))
        self.tracked_labor = c.query('tracked_labor').split(',')
        self.pay_period = int(c.query('pay_period_days'))
        self.use_aloha_tipshare = bool(c.query('use_aloha_tipshare'))
    
    def get_day(self, fmt="%a %b %e"):
        day = datetime.datetime.strptime(self.day, "%Y%m%d") #20210101
        return day.strftime(fmt) #Mon Jan 1

    def get_percent_sales(self):
        '''returns tip share from server jobcodes'''
        cur_df = self.df.loc[self.df.loc[:, ('JOBCODE')].isin(self.percent_sales_codes)]
        total = 0
        if self.use_aloha_tipshare:
            total = np.sum(cur_df.loc[:,('TIPSHCON')])
        else:
            total = np.multiply(np.sum(cur_df.loc[:,('SALES')]), self.sales_percent)
        return total

    def get_percent_tips(self):
        '''returns tip share from register jobcodes'''
        cur_df = self.df.loc[self.df.loc[:, ('JOBCODE')].isin(self.percent_tips_codes)]
        total = np.add(np.sum(cur_df.loc[:,('CCTIPS')]), np.sum(cur_df.loc[:,('DECTIPS')]))
        return total

    def get_tipped_hours(self):
        '''returns total hours to be tipped'''
        cur_df = self.df.loc[self.df.loc[:, ('JOBCODE')].isin(self.tipped_code)]
        total = np.add(np.sum(cur_df.loc[:, ('HOURS')]), np.sum(cur_df.loc[:,('OVERHRS')]))
        return total

    def get_tip_rate(self):
        '''returns hourly rate rounded to the nearest cent'''
        tipped_hours = self.get_tipped_hours()
        total_pool = np.add(self.get_percent_sales(), self.get_percent_tips())
        return np.round(np.divide(total_pool, tipped_hours),2)

    def calc_tipout(self):
        '''calculates tipouts and returns a dataframe with added tipout values'''
        cur_df=self.df.loc[self.df.loc[:, ('JOBCODE')].isin(self.tipped_code)]
        #cur_df.apply(lambda x: np.multiply(np.add(cur_df['HOURS'], cur_df['OVERHRS']), self.get_tip_rate()), axis=1, result_type='expand')
        cur_df.loc[:,('TIPOUT')] = np.multiply(np.add(cur_df.loc[:,('HOURS')], cur_df.loc[:,('OVERHRS')]), self.get_tip_rate())
        return cur_df

    def calc_servtips(self):
        cur_df=self.df.loc[self.df.loc[:, ('JOBCODE')].isin(self.percent_sales_codes)]
        cur_df.loc[:,('SRVTIPS')] = np.subtract(np.add(cur_df.loc[:,('HOURS')], cur_df.loc[:,('OVERHRS')]), self.get_tip_rate())
        return cur_df
    
    def calc_salary(self):
        '''returns a dataframe of the salary employees'''
        if not os.path.exists('salary.csv'):
            self.db.gen_salary()
        salary_df = pd.read_csv('salary.csv')
        salary_df.loc[:,'HOURS'] = np.divide(salary_df.loc[:,'HOURS'], self.pay_period)
        salary_df.loc[:,'OVERHRS'] = np.divide(salary_df.loc[:,'OVERHRS'], self.pay_period)
        return salary_df

    def calc_labor_cost(self, salary=True):
        '''returns a dataframe with pay based on pay rate and hours on tracked labor
           use salary=False to skip calculating salary'''
        cur_df = self.df.loc[self.df.loc[:, ('JOBCODE')].isin(self.tracked_labor)]
        if salary:
            cur_df = cur_df.append(self.calc_salary())
        reg = np.multiply(cur_df.loc[:,('HOURS')], cur_df.loc[:,('RATE')])
        over = np.multiply(cur_df.loc[:,('OVERHRS')], np.multiply(cur_df.loc[:,('RATE')],1.5))
        cur_df.loc[:,('REGPAY')] = reg
        cur_df.loc[:,('OVERPAY')] = over
        cur_df.loc[:,('TOTAL_PAY')] = np.add(reg,over)
        return cur_df
    
    def get_labor_cost(self):
        '''returns total cost of labor'''
        cur_df = self.calc_labor_cost()
        total = np.sum(cur_df.loc[:, ('TOTAL_PAY')])
        return total

    def get_labor_hours(self):
        '''returns total hours tracked on the labor tracker'''
        cur_df = self.df.loc[self.df.loc[:, ('JOBCODE')].isin(self.tracked_labor)]
        total = np.add(np.sum(cur_df.loc[:, ('HOURS')]), np.sum(cur_df.loc[:,('OVERHRS')]))
        return total
    
    def get_labor_rate(self):
        labor_cost = self.get_labor_cost()
        sales = self.db.get_total_sales()
        if sales == 0:
            return 0
        else:
            return np.round(np.multiply(np.divide(labor_cost, sales), 100),2)

class Generate_Report():

    def tip_rate(self, days):
        a = []
        for day in days:
            labor = Labor_Process(day)
            a.append(
                pd.DataFrame(data={
                    'day': [labor.get_day()], 
                    'hours': [round(labor.get_tipped_hours(),2)], 
                    'tipshare': [round(labor.get_percent_sales(),2)], 
                    'tippool': [round(labor.get_percent_tips(),2)], 
                    'tip rate': [round(labor.get_tip_rate(),2)],
                }))

        return a


    def labor_rate(self, days):
        a = []
        for day in days:
            labor = Labor_Process(day)
            a.append(
                pd.DataFrame(data={
                    'day': [labor.get_day()],
                    'rate': [np.round(labor.get_labor_rate(),2)]
            }))

        return a

    def labor_main(self, days): #concatenates the data
        df = pd.DataFrame()
        for day in days:
            labor = Labor_Process(day)
            db = DatabaseQuery(day).process_names()
            srv_df = labor.calc_servtips()
            tipout_df = labor.calc_tipout()
            df = pd.concat([df, srv_df, tipout_df, db], axis=0, copy=False)
        _df = df.pivot_table(df, index=['LASTNAME', 'FIRSTNAME','JOB_NAME'], aggfunc=np.sum, fill_value=np.NaN, margins=True, margins_name='TOTAL')
        _df = _df[['HOURS', 'OVERHRS', 'SRVTIPS', 'TIPOUT', 'DECTIPS']]

        return _df

if __name__ == '__main__':
    def day_list(first_day, last_day, increment = 1):
        '''converts a start date and an end date into a list of all dates in between, based on the increment value'''

        if type(first_day) and type(last_day) == str:
            first_day = datetime.datetime.strptime(first_day, "%Y%m%d")
            last_day = datetime.datetime.strptime(last_day, "%Y%m%d")
        elif type(first_day) or type(last_day) != str or datetime.date:
            raise TypeError('must pass datetime or string')

        delta = datetime.timedelta(days=increment)
        days = []

        while first_day <= last_day:
            cur_day = first_day.strftime("%Y%m%d")
            days.append(cur_day)
            first_day += delta
        
        return days

    def main():
        first_day = '20210101'
        last_day = '20210115'
        days = day_list(first_day, last_day)
        rpt = Generate_Report()
        df = rpt.labor_main(days)
        df.to_csv('csv.csv')


    f = timeit.timeit("main()", "from __main__ import main, DatabaseQuery, Labor_Process, Config", number=1)
    print("completed in " + str(np.round(f,2)) + " seconds")


