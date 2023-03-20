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
        
    def pooler(self):
        return_df = self.df.copy()
        return_df['c_'] = pd.DataFrame
        for pool in self.pools:
            print("processing " + pool)
            c = self.df.loc[self.df['JOBCODE'].isin(self.pools[pool]["contribute"])].copy()
            if self.pools[pool]["type"] == 'sales':
                c['c_'+pool] = np.multiply(c['SALES'].values, (int(self.pools[pool]["percent"])/100))
                #return the rest of the tips after the tip pool
                c['SRV_TIP'] = c['CCTIPS'] - c['c_'+pool]
                return_df['SRV_TIP'] = c['SRV_TIP']
            elif self.pools[pool]["type"] == 'tips': 
                c['c_'+pool] = np.add(c['CCTIPS'].values, c['DECTIPS'].values)
            return_df['c_'+pool] = c['c_'+pool]
            total_pool = c['c_'+pool].sum()

            r = self.df.loc[self.df['JOBCODE'].isin(self.pools[pool]["receive"])].copy()
            with np.errstate(divide='ignore'):
                r_tiprate = np.divide(total_pool,r['HOURS'].sum(),)
            r[pool] = np.multiply(r['HOURS'].values, r_tiprate)
            return_df[pool] = r[pool]

        return_df['TTL_TIP'] = return_df[self.pools].sum(axis=1)
        return_df['TTL_CONT'] = return_df[['c_' + pool for pool in self.pools]].sum(axis=1)
        return return_df
        
if __name__ == '__main__':
    print("loading ProcessPools.py")
    print(ProcessPools('20230303').pooler())
 
