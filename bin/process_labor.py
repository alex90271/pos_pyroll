import datetime
import numpy as np
import pandas as pd
import os
from chip_config import ChipConfig
from query_db import QueryDB as db


class ProcessLabor():
    #'SYSDATEIN','INVALID','JOBCODE','EMPLOYEE','HOURS','OVERHRS','CCTIPS','DECTIPS','COUTBYEOD','SALES','INHOUR','INMINUTE','OUTHOUR','OUTMINUTE','RATE', 'SALES'

    def __init__(self, day):
        self.db = db(day)
        self.df = self.db.process_db('labor')
        self.day = day
        #config options
        c = ChipConfig()
        self.tracked_labor = c.query('SETTINGS','tracked_labor', return_type='int_array')
        self.pay_period = c.query('SETTINGS','pay_period_days', return_type='int_array')[0] #used for calculating labor costs for salaried employees
        self.salary = c.query('SETTINGS','count_salary')
        self.debug = True
    
    def get_day(self, fmt="%a %b %e"):
        day = datetime.datetime.strptime(self.day, "%Y%m%d") #20210101
        return day.strftime(fmt) #Mon Jan 1

    def calc_salary(self):
        '''returns a dataframe of the salary employees'''
        salary_df = pd.DataFrame #blank dataframe
        salary_path = 'salary.csv' 
        #check if the salary csv already exists
        if not os.path.exists(salary_path):
            salary_df = pd.DataFrame(data={'FIRSTNAME':['NEW'], 'LASTNAME':['NEW'], 'RATE':[0], 'HOURS':[0], 'OVERHRS':[0], 'JOB_NAME':['Salary']})
            salary_df.to_csv(salary_path)
            print('new salary file generated, open salary.csv to add salaried employees')
        else:
            salary_df = pd.read_csv(salary_path)
        salary_df.loc[:,('HOURS')] = np.divide(salary_df.loc[:,('HOURS')], self.pay_period)
        salary_df.loc[:,('OVERHRS')] = np.divide(salary_df.loc[:,('OVERHRS')], self.pay_period)
        return salary_df

    def calc_labor_cost(self):
        '''returns a dataframe with pay based on pay rate and hours on tracked labor
           use salary=False to skip calculating salary'''
        cur_df = self.df.loc[self.df.loc[:, ('JOBCODE')].isin(self.tracked_labor)].copy()
        if self.salary:
            cur_df = cur_df.append(self.calc_salary())
        reg = np.multiply(cur_df.loc[:,('HOURS')], cur_df.loc[:,('RATE')])
        over = np.multiply(cur_df.loc[:,('OVERHRS')], np.multiply(cur_df.loc[:,('RATE')],1.5))
        cur_df.loc[:,('REGPAY')] = reg
        cur_df.loc[:,('OVERPAY')] = over
        cur_df.loc[:,('TOTAL_PAY')] = np.add(reg,over)
        return cur_df
    
    def get_total_pay(self):
        '''returns total cost of labor'''
        cur_df = self.calc_labor_cost()
        total = np.sum(cur_df.loc[:, ('TOTAL_PAY')])
        return total

    def get_total_hours(self, over=False, reg=False):
        '''returns total hours tracked on the labor tracker'''
        cur_df = self.df.loc[self.df.loc[:, ('JOBCODE')].isin(self.tracked_labor)].copy()
        total = 0
        if reg:
            total += np.sum(cur_df.loc[:, ('HOURS')])
        if over:
            total += np.sum(cur_df.loc[:,('OVERHRS')])
        return total

    def get_total_sales(self):
        df = self.df
        return np.round(np.sum(df['SALES'].values),2)
    
    def get_labor_rate(self):
        labor_cost = self.get_total_pay()
        sales = self.get_total_sales()
        if sales == 0:
            return np.nan
        else:
            return np.multiply(np.divide(labor_cost, sales), 100)

    def calc_laborrate_df(self):
        salary = ''
        if self.salary:
            salary = ', Salary'
        return pd.DataFrame(data={
                    'Tracked Codes': [str(self.tracked_labor) + salary],
                    'Day': [self.get_day()],
                    'Rate (%)': [self.get_labor_rate()],
                    'Total Pay': [self.get_total_pay()],
                    'Total Sales': [self.get_total_sales()],
                    'Reg Hours': [self.get_total_hours(reg=True)],
                    'Over Hours': [self.get_total_hours(over=True)],
                    'Total Hours': [self.get_total_hours(reg=True, over=True)]
            })

        
if __name__ == '__main__':
    print("loading ProcessLabor.py")
    print(ProcessLabor("20210109").calc_laborrate_df())