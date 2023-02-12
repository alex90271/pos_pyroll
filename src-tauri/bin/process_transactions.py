import datetime
import numpy as np
import pandas as pd
import timeit
import os
from chip_config import ChipConfig
from query_db import QueryDB
from database import DatabaseHandler

class ProcessTransactions():
    '''
    The process labor class handles all of the data calculations and database connections
    gets instantiated with one day, and the calculations are pulled via class functions
    functions that start with 'get' return a number, functions that start with 'calc' return a dataframe
    
    '''
    def __init__(self, day):
        #instantiate a single day to process data
        self.db = QueryDB(day)
        self.df = self.db.process_db('transactions')
        self.day = day

        #config options
        c = ChipConfig()
        self.debug = c.query('SETTINGS','debug', return_type='bool')

        if self.debug:
            if not os.path.exists('debug'):
                os.mkdir('debug')
    
    def get_day(self, fmt="%a %b %e"):
        '''returns the current day for the process labor object'''
        day = datetime.datetime.strptime(self.day, "%Y%m%d") #20210101
        return day.strftime(fmt) #Mon Jan 1

    def get_transactions(self):
        return self.df


if __name__ == '__main__':
        print(ProcessTransactions('20220501').get_transactions())
        