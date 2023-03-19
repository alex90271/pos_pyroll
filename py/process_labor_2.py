import datetime
import json
import numpy as np
import pandas as pd
import timeit
import os
from chip_config import ChipConfig
from query_db import QueryDB
from database import DatabaseHandler


class ProcessLabor2():
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
        for pool in self.pools:
            print("processing " + pool)
            c = self.df.loc[self.df['JOBCODE'].isin(self.pools[pool]["contribute"])].copy()
            r = self.df.loc[self.df['JOBCODE'].isin(self.pools[pool]["receive"])].copy()
            print(c,r)
            
        
if __name__ == '__main__':
    print("loading processlabor2.py")
    print(ProcessLabor2('20230301').pooler())

