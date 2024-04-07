import datetime
import json
import numpy as np
import pandas as pd
import sqlite3
from chip_config import ChipConfig
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
        self.verbose_debug = ChipConfig().query(
            'SETTINGS', 'verbose_debug', return_type='bool')
        self.df = self.db.process_db('labor').copy()
        self.day = day
        self.pool_rates = {}
        self.cash_contributions = {}
        self.total_contributions = {}
        self.total_hours = {}
        self.pool_info = self.get_pool_info()
        self.pool_names = list(self.pool_info)

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
        return self.pooler()

    def get_pool_info(self):
        with open('data/tip_pools.json') as jsonfile:
            return json.load(jsonfile)
    
    def get_adjustments(self):
        '''check the adjustments database for any changes
        
            does not work yet as of 20240406
        '''
        conn = sqlite3.connect('data/adjustments.db')
        df = pd.read_sql('SELECT * from tip_adjustments', conn)
        conn.close()
        df['DATE'] = pd.to_datetime(df['DATE'], format='%Y%m%d')
        matching_rows = df[df['DATE'] == pd.to_datetime(self.day)]
        print(matching_rows)
        return matching_rows

    def pooler(self):
        '''loops through the tip_pools.json and calculates tip pools based on if a sales, tip or equal pool type
        '''
        return_df = self.df.copy()
        adjustments_df = self.get_adjustments()
        #subtract the CC tips here

        #find which row to adjust
        if not adjustments_df.empty:
            for emp in adjustments_df.itertuples():
                # Filter by employee and job code within return_df
                match_condition = (return_df['EMPLOYEE'].astype(int) == int(emp[2])) & \
                                (return_df['JOBCODE'].astype(int) == int(emp[3]))

                # Modify CCTIPS directly in the filtered DataFrame
                return_df.loc[match_condition, 'CCTIPS'] += float(emp[4])
                if emp[4] > 0:
                    print('Positive adjustment made')
                else:
                    print('Negative adjustment made')
        else:
            print('No adjustments')
        
        print(return_df)

        for pool in self.pool_names:
            if self.verbose_debug:
                print("processing " + pool + " for " + self.day)
            c = self.df.loc[self.df['JOBCODE'].isin(
                self.pool_info[pool]["contribute"])].copy()
            
            if self.pool_info[pool]["type"] == 'sales':
                #calculating a tip pool by taking a percentage of sales
                c['c_'+pool] = np.multiply(c['SALES'].values,
                                           (int(self.pool_info[pool]["percent"])/100))
                self.cash_contributions[pool] = 0
                # return the rest of the tips after the tip pool
                c['CCTIP_'+pool] = c['CCTIPS'] - c['c_'+pool]
                return_df['CCTIP_'+pool] = c['CCTIP_'+pool]

            elif self.pool_info[pool]["type"] == 'tips':
                #calculating a tip pool based on a percentage of tips
                c['c_'+pool] = np.multiply(np.add(c['CCTIPS'].values, c['DECTIPS'].values),
                                           (int(self.pool_info[pool]["percent"])/100))
                self.cash_contributions[pool] = c['DECTIPS'].sum()
                return_df['CCTIP_'+pool] = 0

            elif self.pool_info[pool]["type"] == 'equal':
                print("Helo")
                #calculating a tip pool by evenly splitting the tips
                c['c_'+pool] = c['CCTIPS'].values
                #get the total tips, and divide by total splitting it. to split equally
                self.cash_contributions[pool] = c['DECTIPS'].sum()
                return_df['CCTIP_'+pool] = 0
            else:
                raise ValueError("invalid pool type in tip_pools.json")
            

            #record all the contributions, even though that isn't what each person has earned. 
            return_df['c_'+pool] = c['c_'+pool]

            #now we are applying the calculations to the specific pool 
            r = self.df.loc[self.df['JOBCODE'].isin(self.pool_info[pool]["receive"])].copy()

            if self.pool_info[pool]["type"] == 'equal':
                #split equally
                self.pool_rates[pool] = 0
                r[pool] = np.divide(c['CCTIPS'].sum(), len(c.index))
                return_df[pool] = r[pool]
            else:
                #split based on a rate formula
                hr_sum = r['HOURS'].sum()
                cont_sum = c['c_'+pool].sum()
                #ignores the divide by zero error
                with np.errstate(invalid='ignore'):
                    r_tiprate = np.divide(cont_sum, hr_sum)
                r[pool] = np.multiply(r['HOURS'].values, r_tiprate)
                return_df[pool] = r[pool]
                self.pool_rates[pool] = r_tiprate
            print(cont_sum, hr_sum, pool)
            self.total_contributions[pool] = cont_sum
            self.total_hours[pool] = hr_sum
            
        if self.verbose_debug:
            return_df.to_csv('debug/pooler' + self.day + '.csv')
        return_df['TTL_TIPS'] = np.add(return_df[self.pool_names].sum(
            axis=1), return_df[['CCTIP_' + pool for pool in self.pool_names]].sum(axis=1))
        return_df['TTL_CONTRIBUTION'] = return_df[[
            'c_' + pool for pool in self.pool_names]].sum(axis=1)
        # c_ prefix means contribution, CCTIPS_ prefix means tip after a sales type contribution

        return return_df

if __name__ == '__main__':
    print("loading Processpool_info.py")
    #print(ProcessPools('20230909').pooler())
    ProcessPools('20230909').pooler()
