import datetime
import numpy as np
import pandas as pd
import timeit
import os
from chip_config import ChipConfig
from query_db import QueryDB
from database import DatabaseHandler
from process_pools import ProcessPools as pools


class ProcessLabor():
    '''
    The process labor class handles all of the data calculations and database connections
    gets instantiated with one day, and the calculations are pulled via class functions
    functions that start with 'get' return a number, functions that start with 'calc' return a dataframe

    '''
    # 'SYSDATEIN','INVALID','JOBCODE','EMPLOYEE','HOURS','OVERHRS','CCTIPS','DECTIPS','COUTBYEOD','SALES','INHOUR','INMINUTE','OUTHOUR','OUTMINUTE','RATE', 'SALES'

    def __init__(self, day):
        # instantiate a single day to process data
        self.db = QueryDB(day)
        self.pooler = pools(day)
        self.df = self.pooler.get_pool_data().copy()
        self.pool_names = self.pooler.get_pool_info()

        self.day = day
        # config options
        c = ChipConfig()
        self.pay_period = c.query('SETTINGS', 'pay_period_days')  # used for calculating labor costs for salaried employees
        self.verbose_debug = c.query(
            'SETTINGS', 'verbose_debug', return_type='bool')
        self.totals_tiprate = c.query(
            'SETTINGS', 'totaled_tiprate', return_type='bool')
        
        self.dropped_pools_from_tiprate = c.query('SETTINGS', 'dropped_pools_from_tiprate', return_type='str_array')

        if self.verbose_debug:
            if not os.path.exists('debug'):
                os.mkdir('debug')

    def get_pool_data(self):
        return self.df

    def get_day(self, fmt="%a %b %e"):
        '''returns the current day for the process labor object'''
        day = datetime.datetime.strptime(self.day, "%Y%m%d")  # 20210101
        return day.strftime(fmt)  # Mon Jan 1

    def get_total_pay(self, tracked_labor):
        '''returns total cost of labor'''
        cur_df = self.calc_labor_cost(tracked_labor)
        total = np.sum(cur_df.loc[:, ('TOTAL_PAY')])
        return total

    def get_total_hours(self, tracked_labor, over=False, reg=False):
        '''returns total hours tracked on the labor tracker'''
        if tracked_labor==[]:
            cur_df = self.df.copy()
        else:
            cur_df = self.df.loc[self.df.loc[:,
                                         ('JOBCODE')].isin(tracked_labor)]
        total = 0
        if reg:
            total += np.sum(cur_df.loc[:, ('HOURS')])
        if over:
            total += np.sum(cur_df.loc[:, ('OVERHRS')])
        return total

    def get_total_sales(self):
        '''returns total sales, includes ALL sales reguardless of job or employee'''
        df = self.df
        return np.sum(df['SALES'].values)

    def get_total_tips(self, include_declared=False):
        '''returns total tips, includes ALL tips reguardless of job or employee
            pass include declared = TRUE to include declared tips in the total, by default does not
        '''
        df = self.df
        cc = np.round(np.sum(df['CCTIPS'].values), 6)
        if include_declared:
            decl = np.sum(df['DECTIPS'].values)
            return cc + decl
        return cc

    def get_clockin_time(self):
        df = self.df[['EMPLOYEE', 'JOBCODE', 'INHOUR',
                      'INMINUTE', 'OUTHOUR', 'OUTMINUTE']]
        for col in ['INHOUR', 'OUTHOUR']:
            df[col] = np.where(df[col].astype(int) < 12, df[col].astype(
                str) + 'am', df[col])  # any hours that are am, add am
            try:
                # convert 24hr time to a readable 12hr time, skip if an am time
                df[col] = np.where(df[col].astype(int) > 12,
                                   df[col].astype(int) - 12, df[col])
            except:
                pass  # skip that row, if an am is already added
            try:
                df[col] = np.where(df[col].astype(int) < 12, df[col].astype(
                    str) + 'pm', df[col])  # any hours that are left over, add PM
            except:
                pass  # skip that row if an am is already added
        df['DATE'] = self.get_day()
        return df

    def get_labor_rate(self, tracked_labor, return_nan=True):
        # if self.cached:
        # return self.cached[3]
        labor_cost = self.get_total_pay(tracked_labor)
        sales = self.get_total_sales()
        if sales == 0:
            return 0
        else:
            return np.multiply(np.divide(labor_cost, sales), 100)

    def calc_hourly_pay_rate(self):
        '''calculates the individual employee hourly rate, including any tips earned'''
        cur_df = self.df
        labor = self.calc_labor_cost(salary=False)[['TOTAL_PAY']],
        cur_df = cur_df.join(labor)
        cur_df.drop(columns=['INVALID', 'COUTBYEOD'], axis=1, inplace=True)
        cur_df['ACTUAL_HOURLY'] = np.divide(np.add(
            cur_df['TTL_TIPS'], cur_df['TOTAL_PAY']), np.add(cur_df['HOURS'], cur_df['OVERHRS']))

        if self.verbose_debug:
            cur_df.to_csv('debug/calc_hourly_rate' + self.day + '.csv')

        return cur_df

    def calc_labor_cost(self, tracked_labor=[]):
        '''returns a dataframe with pay based on pay rate and hours on tracked labor
           use salary=False to skip calculating salary'''
        if tracked_labor != []:
            cur_df = self.df.loc[self.df.loc[:, ('JOBCODE')].isin(
                tracked_labor)].copy()
        else:
            cur_df = self.df.copy()

        reg = np.multiply(cur_df.loc[:, ('HOURS')], cur_df.loc[:, ('RATE')])
        over = np.multiply(cur_df.loc[:, ('OVERHRS')], np.multiply(
            cur_df.loc[:, ('RATE')], 1.5))
        cur_df.loc[:, ('REGPAY')] = reg
        cur_df.loc[:, ('OVERPAY')] = over
        cur_df.loc[:, ('TOTAL_PAY')] = np.add(reg, over)

        if self.verbose_debug:
            cur_df.to_csv('debug/calc_labor_cost' + self.day + '.csv')
        return cur_df

    def calc_tiprate_df(self):
        '''returns a dataframe with a daily summary report'''
        names = [
            "Pool",
            "Date",
            "Hourly",
            "Cash",
            "Total_Pool",
            "Total_Hours"
        ]
        tip_rate = self.pooler.get_tip_rate()
        cash_tips = self.pooler.get_cash_contribution()
        total_tips = self.pooler.get_total_contribution()
        total_hours = self.pooler.get_total_hours()

        tip_rate_pools = self.pool_names
        for pool in self.dropped_pools_from_tiprate:
            try:
                del tip_rate_pools[pool]
            except:
                print('pool_name does not exist')
        df = pd.concat([pd.DataFrame(data={
            names[0]: [pool],
            names[1]: [self.get_day()],  # date
            names[2]: [tip_rate[pool]],  # Tip Hourly
            names[3]: [cash_tips[pool]],  # Cash Tips
            names[4]: [total_tips[pool]],  # Total Tip Pool
            names[5]: [total_hours[pool]]  # Total Tipped Hours
        }) for pool in tip_rate_pools])

        if self.totals_tiprate:
            _df = df.reset_index().pivot_table(index=['Date'], aggfunc=np.sum)
            _df = _df.sort_values(by='index').drop(columns='index')
            _df['Total_Hours'] = np.divide(_df['Total_Hours'],len(tip_rate_pools))
            _df['Date'] = self.get_day()
            _df['Pool'] = 'DAILY SUM'
            return _df
        return df

    def calc_laborrate_df(self, tracked_labor):
        '''returns a dataframe with the daily calculations for labor rate percentages'''

        jobcodes = QueryDB().return_jobname(tracked_labor)
        jobcodes = ', '.join(jobcodes)

        df = pd.DataFrame(data={
            "Jobs": [jobcodes],
            "Day": [self.get_day()],
            "Rate (%)": [self.get_labor_rate(tracked_labor)],
            "Total Pay": [self.get_total_pay(tracked_labor)],
            "Total Sales": [self.get_total_sales()],
            "Reg Hours": [self.get_total_hours(tracked_labor, reg=True)],
            "Over Hours": [self.get_total_hours(tracked_labor, over=True)],
            "Total Hours": [self.get_total_hours(tracked_labor, reg=True, over=True)]
        })
        return df

    def calc_emps_in_day(self):
        return self.df['EMPLOYEE']


if __name__ == '__main__':

    def main():
        # print("loading ProcessTips.py")
        # print(ProcessLabor("20220107").calc_emps_in_day())
        print(ProcessLabor("20230304").calc_tiprate_df())
    r = 1
    f = timeit.repeat("main()", "from __main__ import main",
                      number=1, repeat=r)
    print("completed with an average of " + str(np.round(np.mean(f), 2)) + " seconds over " +
          str(r) + " tries \n total time: " + str(np.round(np.sum(f), 2)) + "s")
