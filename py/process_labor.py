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
    #'SYSDATEIN','INVALID','JOBCODE','EMPLOYEE','HOURS','OVERHRS','CCTIPS','DECTIPS','COUTBYEOD','SALES','INHOUR','INMINUTE','OUTHOUR','OUTMINUTE','RATE', 'SALES'
    def __init__(self, day):
        #instantiate a single day to process data
        self.db = QueryDB(day)
        self.df = pools(self.day).pooler()['df'].copy()
        self.day = day

        #config options
        c = ChipConfig()
        self.tracked_labor = c.query('SETTINGS','tracked_labor', return_type='int_array')
        self.pay_period = c.query('SETTINGS','pay_period_days', return_type='int_array')[0] #used for calculating labor costs for salaried employees
        self.verbose_debug = c.query('SETTINGS','verbose_debug', return_type='bool')

        if self.verbose_debug:
            if not os.path.exists('debug'):
                os.mkdir('debug')
    
    def get_day(self, fmt="%a %b %e"):
        '''returns the current day for the process labor object'''
        day = datetime.datetime.strptime(self.day, "%Y%m%d") #20210101
        return day.strftime(fmt) #Mon Jan 1

    def get_total_pay(self):
        '''returns total cost of labor'''
        cur_df = self.calc_labor_cost()
        total = np.sum(cur_df.loc[:, ('TOTAL_PAY')])
        return total

    def get_total_hours(self, over=False, reg=False):
        '''returns total hours tracked on the labor tracker'''
        cur_df = self.df.loc[self.df.loc[:, ('JOBCODE')].isin(self.tracked_labor)]
        total = 0
        if reg:
            total += np.sum(cur_df.loc[:, ('HOURS')])
        if over:
            total += np.sum(cur_df.loc[:,('OVERHRS')])
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
        cc = np.round(np.sum(df['CCTIPS'].values),6)
        if include_declared:
            decl = np.sum(df['DECTIPS'].values)
            return cc + decl
        return cc

    def get_clockin_time(self):
        df = self.df[['EMPLOYEE','JOBCODE','INHOUR','INMINUTE','OUTHOUR','OUTMINUTE']]
        for col in ['INHOUR', 'OUTHOUR']:
            df[col] = np.where(df[col].astype(int) < 12, df[col].astype(str) + 'am', df[col]) #any hours that are am, add am
            try:
                df[col] = np.where(df[col].astype(int) > 12, df[col].astype(int) - 12, df[col]) #convert 24hr time to a readable 12hr time, skip if an am time
            except:
                pass #skip that row, if an am is already added
            try:
                df[col] = np.where(df[col].astype(int) < 12, df[col].astype(str) + 'pm', df[col]) #any hours that are left over, add PM
            except:
                pass #skip that row if an am is already added
        df['DATE'] = self.get_day()
        return df

    def get_labor_rate(self,return_nan=True):
        #if self.cached:
            #return self.cached[3]
        labor_cost = self.get_total_pay()
        sales = self.get_total_sales()
        if sales == 0:
            return 0
        else:
            return np.multiply(np.divide(labor_cost, sales), 100)

    def calc_hourly_pay_rate(self):
        '''calculates the individual employee hourly rate, including any tips earned'''
        cur_df = self.df
        labor = self.calc_labor_cost(total=True, salary=False)[['TOTAL_PAY']],
        cur_df = cur_df.join(labor)
        cur_df.drop(columns=['INVALID','COUTBYEOD'], axis=1, inplace=True)
        cur_df['ACTUAL_HOURLY'] = np.divide(np.add(cur_df['TTL_TIP'], cur_df['TOTAL_PAY']), np.add(cur_df['HOURS'], cur_df['OVERHRS']))

        if self.verbose_debug:
            cur_df.to_csv('debug/calc_hourly_rate' + self.day + '.csv')

        return cur_df

    def calc_salary(self):
        '''returns a dataframe of the salary employees'''
        salary_df = pd.DataFrame #blank dataframe
        salary_path = 'data/salary.csv' 
        #check if the salary csv already exists
        if not os.path.exists(salary_path):
            salary_df = pd.DataFrame(data={'FIRSTNAME':['NEW'], 'LASTNAME':['NEW'], 'RATE':[0], 'HOURS':[0], 'OVERHRS':[0], 'JOB_NAME':['Salary']})
            salary_df.to_csv(salary_path)
            print('new salary file generated, open salary.csv to add salaried employees')
        else:
            salary_df = pd.read_csv(salary_path)
        salary_df.loc[:,('HOURS')] = np.divide(salary_df.loc[:,('HOURS')], self.pay_period)
        salary_df.loc[:,('OVERHRS')] = np.divide(salary_df.loc[:,('OVERHRS')], self.pay_period)
        return salary_df

    def calc_labor_cost(self, total=False, salary=True):
        '''returns a dataframe with pay based on pay rate and hours on tracked labor
           use salary=False to skip calculating salary'''
        if not total:
            cur_df = self.df.loc[self.df.loc[:, ('JOBCODE')].isin(self.tracked_labor)].copy()
        else:
            cur_df = self.df.copy()
        if salary:
            cur_df = cur_df.append(self.calc_salary())
        reg = np.multiply(cur_df.loc[:,('HOURS')], cur_df.loc[:,('RATE')])
        over = np.multiply(cur_df.loc[:,('OVERHRS')], np.multiply(cur_df.loc[:,('RATE')],1.5))
        cur_df.loc[:,('REGPAY')] = reg
        cur_df.loc[:,('OVERPAY')] = over
        cur_df.loc[:,('TOTAL_PAY')] = np.add(reg,over)


        if self.verbose_debug:
            cur_df.to_csv('debug/calc_labor_cost' + self.day + '.csv')


        return cur_df

    def calc_hourly_labor(self, interval=60, jobcodes=[7,8]):
        _df = self.db.process_db('labor_hourly')
        cur_df = _df.loc[_df.loc[:, ('JOBID')].isin(jobcodes)].copy()
        cur_df.drop(columns=['JOBID','STOREID','REGIONID','OCCASIONID'], axis=1, inplace=True)
        cur_df = cur_df.pivot_table(index=['DOB','STARTHOUR','STARTMIN','STOPHOUR','STOPMIN'], aggfunc=np.sum)
        cur_df.reset_index(inplace=True)
        cur_df['AMOUNT'] = cur_df['AMOUNT'].divide(len(jobcodes)) #pivot table will multiply sales for each jobcode selected, so we undo that here
        cur_df['PERCENT'] = np.multiply(np.divide(cur_df.loc[:,('COST')],cur_df.loc[:,('AMOUNT')]),100) #COST div AMOUNT, multiply by 100 for percent
        cur_df['STARTHOUR'] = pd.to_datetime(cur_df['STARTHOUR'], format='%H')
        cur_df['STARTMIN'] = pd.to_datetime(cur_df['STARTMIN'], format='%M')
        cur_df['STARTHOUR'] = cur_df['STARTHOUR'].dt.strftime('%I%p')
        cur_df['STARTMIN'] = cur_df['STARTMIN'].dt.strftime('%M')

        if self.verbose_debug:
            cur_df.to_csv('debug/calc_hourly_labor' + self.day + '.csv')

        return cur_df

    def calc_laborrate_df(self):
        '''returns a dataframe with the daily calculations for labor rate percentages'''
        salary = ''
        if self.salary:
            salary = ', Salary'
        jobcodes = QueryDB().return_jobname(self.tracked_labor)
        jobcodes = ', '.join(jobcodes) + salary

        names = ChipConfig().query('RPT_LABOR_RATE', 'col_names')
        df = pd.DataFrame(data={
            names[0]: [jobcodes],
            names[1]: [self.get_day()],
            names[2]: [self.get_labor_rate()],
            names[3]: [self.get_total_pay()],
            names[4]: [self.get_total_sales()],
            names[5]: [self.get_total_hours(reg=True)],
            names[6]: [self.get_total_hours(over=True)],
            names[7]: [self.get_total_hours(reg=True, over=True)]
            })
        return df

    def calc_emps_in_day(self):
        return self.df['EMPLOYEE']

if __name__ == '__main__':

    def main():
        #print("loading ProcessTips.py")
        #print(ProcessLabor("20220107").calc_emps_in_day())
        print(ProcessLabor("20230303").calc_hourly_pay_rate())
    r=1
    f = timeit.repeat("main()", "from __main__ import main", number=1, repeat=r)
    print("completed with an average of " + str(np.round(np.mean(f),2)) + " seconds over " + str(r) + " tries \n total time: " + str(np.round(np.sum(f),2)) + "s")
