import datetime
import numpy as np
import pandas as pd
import os
import xlsxwriter
import timeit
from cfg import cfg
from query_db import query_db

class process_tips():
    #'SYSDATEIN','INVALID','JOBCODE','EMPLOYEE','HOURS','OVERHRS','CCTIPS','DECTIPS','COUTBYEOD','SALES','INHOUR','INMINUTE','OUTHOUR','OUTMINUTE','RATE', 'SALES'
    def __init__(self, day):
        #instantiate a single day to process data
        self.db = query_db(day)
        self.df = self.db.process_db('labor')
        self.day = day

        #config options
        c = cfg()
        self.percent_tips_codes = c.query('SETTINGS','percent_tip_codes', return_type='int_array') #jobcodes that contribute based on a percentage of tips
        self.percent_sales_codes = c.query('SETTINGS','percent_sale_codes', return_type='int_array') #jobcodes that contribute based on a percentage of sales
        self.tipped_code = c.query('SETTINGS','tipped_codes', return_type='int_array') #jobcodes that receive
        self.sales_percent = c.query('SETTINGS','tip_sales_percent', return_type='float')
        self.use_aloha_tipshare = c.query('SETTINGS','use_aloha_tipshare', return_type='bool')
        self.debug = False
    
    def get_day(self, fmt="%a %b %e"):
        day = datetime.datetime.strptime(self.day, "%Y%m%d") #20210101
        return day.strftime(fmt) #Mon Jan 1

    def get_percent_sales(self):
        '''returns tip share  total from server jobcodes'''
        cur_df = self.calc_servtips()
        total = np.sum(cur_df.loc[:,('TIP_CONT')].values)
        #print('tipshare ' + str(total))
        return total

    def get_percent_tips(self, decl=False, cctip=False):
        '''returns tip share from register jobcodes
           if decl=True, it will return declared tips. 
           if cctip=true, it will return cctips
           if BOTH are true, it will return a total
        '''
        cur_df = self.df.loc[self.df['JOBCODE'].isin(self.percent_tips_codes)].copy()
        total = 0

        if decl:
            total += np.sum(cur_df['DECTIPS'].values)
        if cctip:
            total += np.sum(cur_df['CCTIPS'].values)
            
        if decl == False and cctip == False:
            raise ValueError('function get_percent_tips returned 0 as no true args were passed')
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
        total_pool = np.add(self.get_percent_sales(), self.get_percent_tips(decl=True, cctip=True))
        with np.errstate(invalid='ignore'): #some days may return zero and thats okay (closed days)
            return np.divide(total_pool, tipped_hours)

    def calc_tipout(self):
        '''calculates tipouts and returns a dataframe with added tipout values'''
        cur_df = self.df.loc[self.df['JOBCODE'].isin(self.tipped_code)].copy()
        cur_df['TIPOUT'] = np.multiply(cur_df['HOURS'].values, self.get_tip_rate())

        if self.debug:
            cur_df.to_csv('debug/calc_tipout' + self.day + '.csv')

        return cur_df

    def calc_servtips(self, include_names=False): 
        '''calculates server tips and returns a dataframe with added values'''
        cur_df = self.df.loc[self.df['JOBCODE'].isin(self.percent_sales_codes)].copy()


        if self.use_aloha_tipshare:
            cur_df['TIP_CONT'] = cur_df['TIPSHCON'].values
        else:
            cur_df['TIP_CONT'] = np.multiply(cur_df['SALES'].values, self.sales_percent)

        cur_df['SRVTIPS'] = np.subtract(cur_df['CCTIPS'].values, cur_df['TIP_CONT'].values)

        if include_names: #adds employee names, 
            return self.df.merge(cur_df, on='EMPLOYEE', suffixes=(False, False))

        return cur_df
    
    def calc_tiprate_df(self, r=3):
        '''returns a dataframe with a daily summary report, use r to change rounding'''
        names = cfg().query('RPT_TIP_RATE', 'col_names')
        df = pd.DataFrame(data={
            names[0]: [self.get_day()], #date
            names[1]: [np.round(self.get_tip_rate(),r)], #Tip Hourly
            names[2]: [np.round(self.get_percent_tips(decl=True),r)], #Cash Tips
            names[3]: [np.round(self.get_percent_tips(cctip=True),r)], #Takeout CC Tips
            names[4]: [np.round(self.get_percent_sales(),r)], # Server Tipshare
            names[5]: [np.round(np.add(self.get_percent_sales(),self.get_percent_tips(decl=True,cctip=True)), r)], #Total Tip Pool
            names[6]: [np.round(self.get_tipped_hours(),r)] #Total Tipped Hours
            })
        return df

    def calc_payroll(self):
        s = self.calc_servtips()[["TIP_CONT", "SRVTIPS"]]
        t = self.calc_tipout()[["TIPOUT"]]
        df = self.df
        tdf = df.join([s,t])
        
        #remove tips from tipcodes for payroll
        a = tdf.loc[tdf['JOBCODE'].isin(self.percent_tips_codes)]['DECTIPS']
        tdf.update(a.where(a<0, 0))
        return tdf

if __name__ == '__main__':

    def main():
        #print("loading process_tips.py")
        print(process_tips("20210416").calc_tiprate_df())
    r = 5
    f = timeit.repeat("main()", "from __main__ import main", number=1, repeat=r)
    print("completed with an average of " + str(np.round(np.mean(f),2)) + " seconds over " + str(r) + " tries \n total time: " + str(np.round(np.sum(f),2)) + "s")
