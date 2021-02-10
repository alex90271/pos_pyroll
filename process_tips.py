import datetime
import numpy as np
import pandas as pd
import os
from cfg import cfg
from query_db import query_db as db

class process_tips():
    #'SYSDATEIN','INVALID','JOBCODE','EMPLOYEE','HOURS','OVERHRS','CCTIPS','DECTIPS','COUTBYEOD','SALES','INHOUR','INMINUTE','OUTHOUR','OUTMINUTE','RATE', 'SALES'

    def __init__(self, day):
        self.db = db(day)
        self.df = self.db.process_names()
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

    def get_percent_tips(self):
        '''returns tip share from register jobcodes'''
        cur_df = self.df.loc[self.df['JOBCODE'].isin(self.percent_tips_codes)].copy()
        cur_df['TIP_CONT'] = np.add(cur_df['CCTIPS'].values, cur_df['DECTIPS'].values)
        total = np.sum(cur_df['TIP_CONT'].values)
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
        if tipped_hours and total_pool == 0:
            return 0
        rate = np.true_divide(total_pool, tipped_hours)
        #print('tip rate ' + str(rate))
        return rate

    def calc_tipout(self):
        '''calculates tipouts and returns a dataframe with added tipout values'''
        cur_df = self.df.loc[self.df['JOBCODE'].isin(self.tipped_code)].copy()
        cur_df['TIPOUT'] = np.round(np.multiply(cur_df['HOURS'].values, self.get_tip_rate()),2)

        if self.debug:
            cur_df.to_csv('debug/calc_tipout' + self.day + '.csv')

        return cur_df

    def calc_servtips(self, merge=False): 
        cur_df = self.df.loc[self.df['JOBCODE'].isin(self.percent_sales_codes)].copy()

        if self.use_aloha_tipshare:
            cur_df['TIP_CONT'] = cur_df['TIPSHCON'].values
        else:
            cur_df['TIP_CONT'].values = np.multiply(cur_df['SALES'].values, self.sales_percent)

        cur_df['SRVTIPS'] = np.subtract(cur_df['CCTIPS'].values, cur_df['TIP_CONT'].values)

        if merge:
            return self.df.merge(cur_df, on='EMPLOYEE', suffixes=(False, False))

        return cur_df
    
    def calc_tiprate_df(self, r=1):
        df = pd.DataFrame(data={
                    'Date': [self.get_day()], 
                    'Rate': [np.round(self.get_tip_rate(),r)],
                    'Cash Tips': [0],
                    'Takeout Tips': [np.round(self.get_percent_tips(),r)],
                    'Server Tipshare': [np.round(self.get_percent_sales(),r)],
                    'Total Pool': [np.round(np.add(self.get_percent_sales(),self.get_percent_tips()),r)], 
                    'Tipped Hours': [np.round(self.get_tipped_hours(),r)]
                    #TODO finish
                })
        return df

    def calc_all_tips(self):
        s = self.calc_servtips()[["TIP_CONT", "SRVTIPS"]]
        t = self.calc_tipout()[["TIPOUT"]]
        df = self.df
        tdf = df.join([s,t])
        return tdf

if __name__ == '__main__':
    print("loading process_tips.py")
    print(process_tips("20210109").get_percent_tips())