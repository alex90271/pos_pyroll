import datetime
import numpy as np
import pandas as pd
import os
from cfg import cfg
from query_db import query_db as db


class process_labor():
    #'SYSDATEIN','INVALID','JOBCODE','EMPLOYEE','HOURS','OVERHRS','CCTIPS','DECTIPS','COUTBYEOD','SALES','INHOUR','INMINUTE','OUTHOUR','OUTMINUTE','RATE', 'SALES'

    def __init__(self, day):
        self.db = db(day)
        self.df = self.db.process_names()
        self.day = day
        #config options
        c = cfg()
        self.tracked_labor = c.query('tracked_labor').split(',')
        self.pay_period = int(c.query('pay_period_days'))
        self.debug = True
    
    def get_day(self, fmt="%a %b %e"):
        day = datetime.datetime.strptime(self.day, "%Y%m%d") #20210101
        return day.strftime(fmt) #Mon Jan 1

    def calc_salary(self):
        '''returns a dataframe of the salary employees'''
        if not os.path.exists('salary.csv'):
            self.db.gen_salary()
        salary_df = pd.read_csv('salary.csv')
        salary_df.loc[:,('HOURS')] = np.divide(salary_df.loc[:,('HOURS')], self.pay_period)
        salary_df.loc[:,('OVERHRS')] = np.divide(salary_df.loc[:,('OVERHRS')], self.pay_period)
        return salary_df

    def calc_labor_cost(
                        self, 
                        salary=True
                        ):
        '''returns a dataframe with pay based on pay rate and hours on tracked labor
           use salary=False to skip calculating salary'''
        cur_df = self.df.loc[self.df.loc[:, ('JOBCODE')].isin(self.tracked_labor)].copy()
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
        cur_df = self.df.loc[self.df.loc[:, ('JOBCODE')].isin(self.tracked_labor)].copy()
        total = np.add(np.sum(cur_df.loc[:, ('HOURS')]), np.sum(cur_df.loc[:,('OVERHRS')]))
        return total
    
    def get_labor_rate(self):
        labor_cost = self.get_labor_cost()
        sales = self.db.get_total_sales()
        if sales == 0:
            return 0
        else:
            return np.round(np.multiply(np.divide(labor_cost, sales), 100),2)

if __name__ == '__main__':
    print("loading process_labor.py")
    print(process_labor("20210109").get_labor_hours())