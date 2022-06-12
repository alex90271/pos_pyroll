import datetime
import numpy as np
import pandas as pd
import timeit
import os
from chip_config import ChipConfig
from query_db import QueryDB
from database import DatabaseHandler

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
        self.nonsharedtip_code = c.query('SETTINGS','nonshared_tip_codes', return_type='int_array') 
        self.debug = c.query('SETTINGS','debug', return_type='bool')
    
    def get_day(self, fmt="%a %b %e"):
        '''returns the current day for the process labor object'''
        day = datetime.datetime.strptime(self.day, "%Y%m%d") #20210101
        return day.strftime(fmt) #Mon Jan 1

    def get_percent_sales(self):
        '''returns tip share  total from server jobcodes'''
        cur_df = self.calc_servtips()
        total = np.sum(cur_df.loc[:,('TIP_CONT')].values)
        
        if self.debug:
            print('tipshare ' + str(total))

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
            
        if self.debug:
            print('reg tips ' + str(total))

        return total

    def get_tipped_hours(self):
        '''returns total hours to be tipped'''
        cur_df = self.df.loc[self.df['JOBCODE'].isin(self.tipped_code)].copy()
        total = np.add(np.sum(cur_df['HOURS'].values), np.sum(cur_df['OVERHRS'].values))
            
        if self.debug:
            print('total hours ' + str(total))

        return total

    def get_tip_rate(self):
        '''returns hourly rate'''
        #if self.cached:
           # return self.cached[2]
        tipped_hours = self.get_tipped_hours()
        total_pool = np.add(self.get_percent_sales(), self.get_percent_tips(decl=True, cctip=True))
        with np.errstate(invalid='ignore'): #some days may return zero and thats okay (closed days)
            rt = np.divide(total_pool, tipped_hours)
            if self.debug:
                print(self.day, rt)
            return rt
            
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
        df = self.df[['EMPLOYEE','INHOUR','INMINUTE','OUTHOUR','OUTMINUTE']]
        #for col in ['INHOUR','OUTHOUR']:
            #df[col] = np.where(df[col].astype(int) > 12, df[col].astype(int) - 12, df[col].astype(int))
        df['DATE'] = self.get_day()
        return df
    
    def get_unallocated_tips(self):
        '''
        returns any tips not allocated in the tip pool, or paid out to a server
        '''
        total = self.get_total_tips(include_declared=False) + self.get_percent_tips(decl=True)
        used = np.sum([np.sum(self.calc_servtips()[["SRVTIPS"]].values),
                      np.sum(self.calc_tipout()[["TIPOUT"]].values),
                      np.sum(self.calc_tipout()[["DECTIPS"]].values),
                      np.sum(self.calc_nonsharedtips()[["OTHERTIPS"]].values)])
        #print(used,total)
         #save just the tipout from calc_tipout
        return np.round(np.subtract(total,used),4)

    def get_labor_rate(self,return_nan=True):
        #if self.cached:
            #return self.cached[3]
        labor_cost = self.get_total_pay()
        sales = self.get_total_sales()
        if sales == 0:
            return 0
        else:
            return np.multiply(np.divide(labor_cost, sales), 100)

    def calc_hourly_rate(self):
        '''calculates the individual employee hourly rate, including any tips earned'''
        cur_df = self.df
        labor = self.calc_labor_cost(total=True, salary=False)[['TOTAL_PAY']],
        tips = self.calc_payroll()[['TOTALTIPS']],
        cur_df = cur_df.join(labor)
        cur_df = cur_df.join(tips)
        cur_df['ACTUAL_HOURLY'] = np.divide((cur_df['TOTALTIPS'] + cur_df['TOTAL_PAY']), (cur_df['HOURS'] + cur_df['OVERHRS']))

        if self.debug:
            cur_df.to_csv('debug/calc_hourly_rate' + self.day + '.csv')

        return cur_df
        

    def calc_tipout(self):
        '''calculates tipouts and returns a dataframe with added tipout values'''
        cur_df = self.df.loc[self.df['JOBCODE'].isin(self.tipped_code)].copy()
        cur_df['TIPOUT'] = np.multiply(cur_df['HOURS'].values, self.get_tip_rate())

        if self.debug:
            cur_df.to_csv('debug/calc_tipout' + self.day + '.csv')

        return cur_df

    def calc_nonsharedtips(self):
        '''calculates any tips for jobcodes who keeps the entire tip'''
        cur_df = self.df.loc[self.df['JOBCODE'].isin(self.nonsharedtip_code)].copy()
        cur_df['OTHERTIPS'] = cur_df['CCTIPS']

        if self.debug:
            cur_df.to_csv('debug/calc_nonshared_tips' + self.day + '.csv')

        return cur_df

    def calc_servtips(self): 
        '''calculates server tips and returns a dataframe with added values'''
        cur_df = self.df.loc[self.df['JOBCODE'].isin(self.percent_sales_codes)].copy()

        if self.use_aloha_tipshare:
            cur_df['TIP_CONT'] = cur_df['TIPSHCON'].values
        else:
            cur_df['TIP_CONT'] = np.multiply(cur_df['SALES'].values, float(self.sales_percent))

        cur_df['SRVTIPS'] = np.subtract(cur_df['CCTIPS'].values, cur_df['TIP_CONT'].values)


        if self.debug:
            cur_df.to_csv('debug/calc_srv_tips' + self.day + '.csv')


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


        if self.debug:
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

        if self.debug:
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
    
    def calc_tiprate_df(self):
        '''returns a dataframe with a daily summary report'''
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
        '''appends serving tips and tipout to the main dataframe, and returns the resulting dataframe'''
        s = self.calc_servtips()[["TIP_CONT", "SRVTIPS"]] #save just those columns from calc_serve_tips
        t = self.calc_tipout()[["TIPOUT"]] #save just the tipout from calc_tipout
        n = self.calc_nonsharedtips()[["OTHERTIPS"]]
        df = self.df
        tdf = df.join([s,t,n])
        tdf['TOTALTIPS'] = tdf[["SRVTIPS","TIPOUT","OTHERTIPS"]].sum(axis=1)
        a = tdf.loc[tdf['JOBCODE'].isin(self.percent_tips_codes)]['DECTIPS'] #remove tips from jobcodes that contribute all their tips
        tdf.update(a.where(a<0, 0))

        if self.debug:
            tdf.to_csv('debug/calc_payroll' + self.day + '.csv')

        return tdf

    def calc_emps_in_day(self):
        return self.df['EMPLOYEE']

if __name__ == '__main__':

    def main():
        #print("loading ProcessTips.py")
        #print(ProcessLabor("20220107").calc_emps_in_day())
        print(ProcessLabor("20211214").calc_hourly_rate())
    r=1
    f = timeit.repeat("main()", "from __main__ import main", number=1, repeat=r)
    print("completed with an average of " + str(np.round(np.mean(f),2)) + " seconds over " + str(r) + " tries \n total time: " + str(np.round(np.sum(f),2)) + "s")
