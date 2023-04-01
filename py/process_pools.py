import datetime
import json
import numpy as np
import pandas as pd
from query_db import QueryDB


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
        self.pool_rates = {}
        self.cash_contributions = {}
        self.total_contributions = {}
        self.total_hours = {}
        self.pool_names = self.get_pool_names()
        self.pool_out = self.pooler()

    def get_day(self, fmt="%a %b %e"):
        '''returns the current day for the process labor object'''
        day = datetime.datetime.strptime(self.day, "%Y%m%d")  # 20210101
        return day.strftime(fmt)  # Mon Jan 1

    def get_cash_contribution(self):
        return self.cash_contributions

    def get_total_hours(self):
        return self.total_hours

    def get_total_contribution(self):
        return self.total_contributions

    def get_tip_rate(self):
        return self.pool_rates

    def get_pool_data(self):
        return self.pool_out

    def get_pool_names(self):
        with open('data/pools.json') as jsonfile:
            return json.load(jsonfile)

    def pooler(self):
        return_df = self.df.copy()
        for pool in self.pool_names:
            print("processing " + pool)
            c = self.df.loc[self.df['JOBCODE'].isin(
                self.pool_names[pool]["contribute"])].copy()
            if self.pool_names[pool]["type"] == 'sales':
                c['c_'+pool] = np.multiply(c['SALES'].values,
                                           (int(self.pool_names[pool]["percent"])/100))
                self.cash_contributions[pool] = 0
                # return the rest of the tips after the tip pool
                c['CCTIP_'+pool] = c['CCTIPS'] - c['c_'+pool]
                return_df['CCTIP_'+pool] = c['CCTIP_'+pool]
            elif self.pool_names[pool]["type"] == 'tips':
                c['c_'+pool] = np.multiply(np.add(c['CCTIPS'].values, c['DECTIPS'].values),
                                           (int(self.pool_names[pool]["percent"])/100))
                self.cash_contributions[pool] = c['DECTIPS'].sum()
                return_df['CCTIP_'+pool] = 0
            return_df['c_'+pool] = c['c_'+pool]

            r = self.df.loc[self.df['JOBCODE'].isin(
                self.pool_names[pool]["receive"])].copy()
            hr_sum = r['HOURS'].sum()
            cont_sum = c['c_'+pool].sum()
            r_tiprate = np.divide(cont_sum, hr_sum)
            r[pool] = np.multiply(r['HOURS'].values, r_tiprate)
            return_df[pool] = r[pool]
            self.total_contributions[pool] = cont_sum
            self.total_hours[pool] = hr_sum
            self.pool_rates[pool] = r_tiprate

        return_df['TTL_TIP'] = np.add(return_df[self.pool_names].sum(
            axis=1), return_df[['CCTIP_' + pool for pool in self.pool_names]].sum(axis=1))
        return_df['TTL_CONT'] = return_df[[
            'c_' + pool for pool in self.pool_names]].sum(axis=1)
        # c_ prefix means contribution, CCTIPS_ prefix means tip after a sales type contribution

        return return_df

if __name__ == '__main__':
    print("loading Processpool_names.py")
    ProcessPools('20230304').get_pool_data().to_csv('out.csv')