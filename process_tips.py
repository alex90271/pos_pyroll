import datetime
import numpy as np
import pandas as pd
import os
import xlsxwriter
import timeit
from cfg import cfg
from query_db import query_db as db

class process_tips():
    #'SYSDATEIN','INVALID','JOBCODE','EMPLOYEE','HOURS','OVERHRS','CCTIPS','DECTIPS','COUTBYEOD','SALES','INHOUR','INMINUTE','OUTHOUR','OUTMINUTE','RATE', 'SALES'

    def __init__(self, day):
        self.db = db(day)
        self.df = self.db.process_db('labor')
        self.day = day
        #config options
        c = cfg()
        self.percent_tips_codes = c.query('percent_tip_codes').split(',') #jobcodes that contribute based on a percentage of tips
        self.percent_sales_codes = c.query('percent_sale_codes').split(',') #jobcodes that contribute based on a percentage of sales
        self.tipped_code = c.query('tipped_codes').split(',') #jobcodes that receive
        self.sales_percent = float(c.query('tip_sales_percent'))
        self.tip_percent = float(c.query('tip_amt_percent'))
        self.use_aloha_tipshare = bool(c.query('use_aloha_tipshare'))
        self.debug = False
    
    def get_day(self, fmt="%a %b %e"):
        day = datetime.datetime.strptime(self.day, "%Y%m%d") #20210101
        return day.strftime(fmt) #Mon Jan 1

    def get_percent_sales(self):
        '''returns tip share from server jobcodes'''
        cur_df = self.calc_servtips()
        total = np.sum(cur_df.loc[:,('TIP_CONT')].values)
        #print('tipshare ' + str(total))
        return total

    def get_percent_tips(self, only_decl=False, total=False):
        '''returns tip share from register jobcodes
           if only_decl=True, it will return declared tips. 
           if total is true, it will only be evaluted if only_decl = false
        '''
        cur_df = self.df.loc[self.df['JOBCODE'].isin(self.percent_tips_codes)].copy()
        if only_decl:
            total = np.sum(cur_df['DECTIPS'].values)
        else:
            if total:
                total = np.sum(np.add(cur_df['CCTIPS'].values,cur_df['DECTIPS'].values))
            else:
                total = np.sum(cur_df['CCTIPS'].values)
        #print('reg tips ' + str(total))
        return total

    def get_tipped_hours(self):
        '''returns total hours to be tipped'''
        cur_df = self.df.loc[self.df['JOBCODE'].isin(self.tipped_code)].copy()
        total = np.add(np.sum(cur_df['HOURS'].values), np.sum(cur_df['OVERHRS'].values))
        #print('total hours ' + str(total))
        return total

    def get_tip_rate(self):
        '''returns hourly rate rounded to the nearest cent'''
        tipped_hours = self.get_tipped_hours()
        total_pool = np.add(self.get_percent_sales(), self.get_percent_tips())
        with np.errstate(invalid='ignore'): #some days may return zero and thats okay
            return np.divide(total_pool, tipped_hours)

    def calc_tipout(self):
        '''calculates tipouts and returns a dataframe with added tipout values'''
        cur_df = self.df.loc[self.df['JOBCODE'].isin(self.tipped_code)].copy()
        cur_df['TIPOUT'] = np.multiply(cur_df['HOURS'].values, self.get_tip_rate())

        if self.debug:
            cur_df.to_csv('debug/calc_tipout' + self.day + '.csv')

        return cur_df

    def calc_servtips(self, merge=False): 
        '''calculates server tips and returns a dataframe with added values'''
        cur_df = self.df.loc[self.df['JOBCODE'].isin(self.percent_sales_codes)].copy()

        if self.use_aloha_tipshare:
            cur_df['TIP_CONT'] = cur_df['TIPSHCON'].values
        else:
            cur_df['TIP_CONT'].values = np.multiply(cur_df['SALES'].values, self.sales_percent)

        cur_df['SRVTIPS'] = np.subtract(cur_df['CCTIPS'].values, cur_df['TIP_CONT'].values)

        if merge:
            return self.df.merge(cur_df, on='EMPLOYEE', suffixes=(False, False))

        return cur_df
    
    def calc_tiprate_df(self, r=3):
        '''returns a dataframe with a daily summary report, use r to change rounding'''
        df = pd.DataFrame(data={
                    'Date': [self.get_day()], 
                    'Tip Hourly': [np.round(self.get_tip_rate(),r)],
                    'Cash Tips': [np.round(self.get_percent_tips(only_decl=True),r)],
                    'Takeout CC Tips': [np.round(self.get_percent_tips(),r)],
                    'Server Tipshare': [np.round(self.get_percent_sales(),r)],
                    'Total Tip Pool': [np.round(np.add(self.get_percent_sales(),self.get_percent_tips(total=True)), r)], 
                    'Total Tip\'d Hours': [np.round(self.get_tipped_hours(),r)]
                })
        return df

    def calc_payroll(self):
        s = self.calc_servtips()[["TIP_CONT", "SRVTIPS"]]
        t = self.calc_tipout()[["TIPOUT"]]
        df = self.df
        tdf = df.join([s,t])

        return tdf

if __name__ == '__main__':

    def main():
        #print("loading process_tips.py")
        process_tips("20210116").calc_tiprate_df()
    r = 5
    f = timeit.repeat("main()", "from __main__ import main", number=1, repeat=r)
    print("completed with an average of " + str(np.round(np.mean(f),2)) + " seconds over " + str(r) + " tries \n total time: " + str(np.round(np.sum(f),2)) + "s")