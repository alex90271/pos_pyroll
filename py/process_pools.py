import csv
import datetime
import json
import numpy as np
import pandas as pd
import timeit
import os
from chip_config import ChipConfig
from query_db import QueryDB
from database import DatabaseHandler


class ProcessPools():
    '''
    The process labor class handles all of the data calculations and database connections
    gets instantiated with one day, and the calculations are pulled via class functions
    functions that start with 'get' return a number, functions that start with 'calc' return a dataframe

    '''
    # 'SYSDATEIN','INVALID','JOBCODE','EMPLOYEE','HOURS','OVERHRS','CCTIPS','DECTIPS','COUTBYEOD','SALES','INHOUR','INMINUTE','OUTHOUR','OUTMINUTE','RATE', 'SALES'

    def __init__(self, day):
        # instantiate a single day to process data
        self.db = QueryDB(day)
        self.df = self.db.process_db('labor').copy()
        self.day = day
        self.pools = self.get_pools()

    def get_day(self, fmt="%a %b %e"):
        '''returns the current day for the process labor object'''
        day = datetime.datetime.strptime(self.day, "%Y%m%d")  # 20210101
        return day.strftime(fmt)  # Mon Jan 1

    def get_pools(self):
        with open('data/pools.json') as jsonfile:
            return json.load(jsonfile)
        
    def get_deductions(self):
        try:
            deductions = pd.read_csv('data/_Takeout Mistakes_ - Sheet1.csv', skiprows=[1])
        except:
            print('invalid format or not found')
        deductions = deductions[['EMPLOYEE','COST']]
        return deductions
        
        
    def pooler(self):
        return_df = self.df.copy()
        return_df['TOTAL_TIP'] = 0
        for pool in self.pools:
            print("processing " + pool)
            c = self.df.loc[self.df['JOBCODE'].isin(self.pools[pool]["contribute"])].copy()
            if self.pools[pool]["type"] == 'sales':
                c['TIP_CONT'] = np.multiply(c['SALES'].values, (int(self.pools[pool]["percent"])/100))
                #return the rest of the tips after the tip pool
                c['SRV_TIP'] = c['CCTIPS'] - c['TIP_CONT']
                return_df = return_df.join(c['SRV_TIP'])
                return_df['TOTAL_TIP'] = return_df['TOTAL_TIP'] + return_df['SRV_TIP'] 
            elif self.pools[pool]["type"] == 'tips': 
                c['TIP_CONT'] = np.add(c['CCTIPS'].values, c['DECTIPS'].values)
            #c.to_csv('c_' + pool + '.csv')
            total_pool = c['TIP_CONT'].sum()

            r = self.df.loc[self.df['JOBCODE'].isin(self.pools[pool]["receive"])].copy()
            r_tiprate = np.divide(total_pool,r['HOURS'].sum())
            r[pool] = np.multiply(r['HOURS'].values, r_tiprate)
            return_df = return_df.join(r[pool])
            return_df['TOTAL_TIP'] = return_df[pool]
        return return_df
        
if __name__ == '__main__':
    print("loading ProcessPools.py")
    print(ProcessPools('20230301').get_deductions())
 
