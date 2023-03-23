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
        # config options
        c = ChipConfig()
        self.debug = c.query('SETTINGS', 'debug', return_type='bool')

        # instantiate a single day to process data
        self.db = QueryDB(day)
        self.day = day
        try:
            self.df = self.db.process_db('transactions')[['EMPLOYEE','CHECK','SYSDATE','TYPE','TYPEID','NAME','UNIT','AMOUNT','TIP','HOUSEID']]
            #self.house = self.db.process_db('house_acct')[['ID','NUMBER','FIRSTNAME','LASTNAME']]
        except:
            if self.debug:
                print(day + ' has no data.. generating blank sheets')
            self.df = pd.DataFrame(data={'EMPLOYEE':[0],'CHECK':[0],'SYSDATE':[0],'TYPE':[0],'TYPEID':[0],'NAME':[0],'UNIT':[0],'AMOUNT':[0],'TIP':[0],'HOUSEID':[0]})

        if self.debug:
            if not os.path.exists('debug'):
                os.mkdir('debug')

    def get_day(self, fmt="%a %b %e"):
        '''returns the current day for the process transactions object'''
        day = datetime.datetime.strptime(self.day, "%Y%m%d")  # 20210101
        return day.strftime(fmt)  # Mon Jan 1

    # type ID 1 are regular transactions, ID 25 are house accounts
    def get_transactions_bytype(self, type=1, id=25):
        '''
            filters transactions, 
            where type determines if the transaction was a comp, sale, or other, 1 are regular sales
            where it equals the payment type, 3 is credit card, 25 is house account
            refer to aloha pos documentation for id numbers
        '''
        _df = self.df
        _df = _df.loc[np.where(_df['TYPE'] == type)].reset_index(
            drop=True)  # filter by transaction type first
        return _df.loc[np.where(_df['TYPEID'] == id)].reset_index(drop=True) # then filter by tender type id
        

    def get_total_byhouseid(self):
        df = self.get_transactions_bytype(id=25)
        df = df.groupby(['HOUSEID']).sum() #sum up duplicates
        return df[['AMOUNT']]



if __name__ == '__main__':
    print(ProcessTransactions('2023').get_total_byhouseid())