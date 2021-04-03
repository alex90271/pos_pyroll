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
        self.df = self.db.process_db('labor')
        self.day = day
        #config options
        c = cfg()
        self.tracked_labor = c.query('SETTINGS','tracked_labor').split(',')
        self.pay_period = int(c.query('SETTINGS','pay_period_days'))
        self.salary = c.query('SETTINGS','count_salary')
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
    
    def get_labor_rate(self):
        labor_cost = self.get_total_pay()
        sales = self.db.get_total_sales()
        if sales == 0:
            return 0
        else:
            return np.round(np.multiply(np.divide(labor_cost, sales), 100),2)

    def calc_laborrate_df(self, r=3):
        return pd.DataFrame(data={
                    'Tracked Codes': [self.tracked_labor],
                    'Day': [self.get_day()],
                    'Rate (%)': [np.round(self.get_labor_rate(),r)],
                    'Total Pay': [np.round(self.get_total_pay(),r)],
                    'Total Sales': [np.round(self.db.get_total_sales(),r)],
                    'Reg Hours': [np.round(self.get_total_hours(reg=True),r)],
                    'Over Hours': [np.round(self.get_total_hours(over=True),r)],
                    'Total Hours': [np.round(self.get_total_hours(reg=True, over=True),r)]
            })

        
if __name__ == '__main__':
    print("loading process_labor.py")
    print(process_labor("20210109").calc_laborrate_df())