import datetime
import numpy as np
import pandas as pd
import timeit
import os
from chip_config import ChipConfig
from query_db import QueryDB

class ProcessLabor():
    '''functions that start with 'get' return a number, functions that start with 'calc' return a dataframe'''
    #'SYSDATEIN','INVALID','JOBCODE','EMPLOYEE','HOURS','OVERHRS','CCTIPS','DECTIPS','COUTBYEOD','SALES','INHOUR','INMINUTE','OUTHOUR','OUTMINUTE','RATE', 'SALES'
    def __init__(self, day):
        #instantiate a single day to process data
        self.db = QueryDB(day)
        self.df = self.db.process_db('labor')
        self.day = day

        #config options
        c = ChipConfig()
        self.percent_tips_codes = c.query('SETTINGS','percent_tip_codes', return_type='int_array') #jobcodes that contribute based on a percentage of tips
        self.percent_sales_codes = c.query('SETTINGS','percent_sale_codes', return_type='int_array') #jobcodes that contribute based on a percentage of sales
        self.tipped_code = c.query('SETTINGS','tipped_codes', return_type='int_array') #jobcodes that receive
        self.sales_percent = c.query('SETTINGS','tip_sales_percent', return_type='float')
        self.use_aloha_tipshare = c.query('SETTINGS','use_aloha_tipshare', return_type='bool')
        self.tracked_labor = c.query('SETTINGS','tracked_labor', return_type='int_array')
        self.pay_period = c.query('SETTINGS','pay_period_days', return_type='int_array')[0] #used for calculating labor costs for salaried employees
        self.salary = c.query('SETTINGS','count_salary')
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
        '''returns hourly rate'''
        tipped_hours = self.get_tipped_hours()
        total_pool = np.add(self.get_percent_sales(), self.get_percent_tips(decl=True, cctip=True))
        with np.errstate(invalid='ignore'): #some days may return zero and thats okay (closed days)
            return np.divide(total_pool, tipped_hours)
            
    def get_total_pay(self):
        '''returns total cost of labor'''
        cur_df = self.calc_labor_cost()
        total = np.sum(cur_df.loc[:, ('TOTAL_PAY')])
        return total

    def get_total_hours(self, over=False, reg=False):
        '''returns total hours tracked on the labor tracker'''
        cur_df = self.df.loc[self.df.loc[:, ('JOBCODE')].isin(self.tracked_labor)].copy()
        total = 0
        if reg:
            total += np.sum(cur_df.loc[:, ('HOURS')])
        if over:
            total += np.sum(cur_df.loc[:,('OVERHRS')])
        return total

    def get_total_sales(self):
        df = self.df
        return np.round(np.sum(df['SALES'].values),2)
    
    def get_labor_rate(self):
        labor_cost = self.get_total_pay()
        sales = self.get_total_sales()
        if sales == 0:
            return np.nan
        else:
            return np.multiply(np.divide(labor_cost, sales), 100)

    def calc_tipout(self):
        '''calculates tipouts and returns a dataframe with added tipout values'''
        cur_df = self.df.loc[self.df['JOBCODE'].isin(self.tipped_code)].copy()
        cur_df['TIPOUT'] = np.multiply(cur_df['HOURS'].values, self.get_tip_rate())

        if self.debug:
            cur_df.to_csv('debug/calc_tipout' + self.day + '.csv')

        return cur_df

    def calc_servtips(self): 
        '''calculates server tips and returns a dataframe with added values'''
        cur_df = self.df.loc[self.df['JOBCODE'].isin(self.percent_sales_codes)].copy()

        if self.use_aloha_tipshare:
            cur_df['TIP_CONT'] = cur_df['TIPSHCON'].values
        else:
            cur_df['TIP_CONT'] = np.multiply(cur_df['SALES'].values, float(self.sales_percent))

        cur_df['SRVTIPS'] = np.subtract(cur_df['CCTIPS'].values, cur_df['TIP_CONT'].values)

        return cur_df

    def calc_salary(self):
        '''returns a dataframe of the salary employees'''
        salary_df = pd.DataFrame #blank dataframe
        salary_path = 'salary.csv' 
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

    def calc_labor_cost(self):
        '''returns a dataframe with pay based on pay rate and hours on tracked labor
           use salary=False to skip calculating salary'''
        cur_df = self.df.loc[self.df.loc[:, ('JOBCODE')].isin(self.tracked_labor)].copy()
        if self.salary:
            cur_df = cur_df.append(self.calc_salary())
        reg = np.multiply(cur_df.loc[:,('HOURS')], cur_df.loc[:,('RATE')])
        over = np.multiply(cur_df.loc[:,('OVERHRS')], np.multiply(cur_df.loc[:,('RATE')],1.5))
        cur_df.loc[:,('REGPAY')] = reg
        cur_df.loc[:,('OVERPAY')] = over
        cur_df.loc[:,('TOTAL_PAY')] = np.add(reg,over)
        return cur_df

    def calc_laborrate_df(self):
        salary = ''
        if self.salary:
            salary = ', Salary'
        jobcodes = QueryDB().return_jobname(self.tracked_labor)
        jobcodes = ', '.join(jobcodes) + salary
        df = pd.DataFrame(data={
                    'Tracked Codes': [jobcodes],
                    'Day': [self.get_day()],
                    'Rate (%)': [self.get_labor_rate()],
                    'Total Pay': [self.get_total_pay()],
                    'Total Sales': [self.get_total_sales()],
                    'Reg Hours': [self.get_total_hours(reg=True)],
                    'Over Hours': [self.get_total_hours(over=True)],
                    'Total Hours': [self.get_total_hours(reg=True, over=True)]
            })
        return df
    
    def calc_tiprate_df(self, r=3):
        '''returns a dataframe with a daily summary report, use r to change rounding'''
        names = ChipConfig().query('RPT_TIP_RATE', 'col_names')
        df = pd.DataFrame(data={
            names[0]: [self.get_day()], #date
            names[1]: [self.get_tip_rate()], #Tip Hourly
            names[2]: [self.get_percent_tips(decl=True)], #Cash Tips
            names[3]: [self.get_percent_tips(cctip=True)], #Takeout CC Tips
            names[4]: [self.get_percent_sales()], # Server Tipshare
            names[5]: [np.add(self.get_percent_sales(),self.get_percent_tips(decl=True,cctip=True))], #Total Tip Pool
            names[6]: [self.get_tipped_hours()] #Total Tipped Hours
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
        #print("loading ProcessTips.py")
        print(ProcessLabor("20210416").calc_laborrate_df())
    r = 5
    f = timeit.repeat("main()", "from __main__ import main", number=1, repeat=r)
    print("completed with an average of " + str(np.round(np.mean(f),2)) + " seconds over " + str(r) + " tries \n total time: " + str(np.round(np.sum(f),2)) + "s")