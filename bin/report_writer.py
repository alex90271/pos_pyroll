import json
from re import A
from process_labor import ProcessLabor as labor
from query_db import QueryDB as query_db
from chip_config import ChipConfig
import numpy as np
import pandas as pd
import datetime
import timeit

class ReportWriter():

    def __init__(self, first_day, last_day=None, increment=1):
        self.first_day = first_day
        self.last_day = last_day
        self.days = []
        self.FILEPATH = 'data/'

        if self.last_day == None:
            self.last_day = self.first_day
        else: 
            if type(first_day) and type(last_day) == str:
                first_day = datetime.datetime.strptime(first_day, "%Y%m%d")
                last_day = datetime.datetime.strptime(last_day, "%Y%m%d")
            elif type(first_day) or type(last_day) != str or datetime.date:
                raise TypeError('must pass datetime or string')

            while first_day <= last_day:
                cur_day = first_day.strftime("%Y%m%d")
                self.days.append(cur_day)
                first_day += datetime.timedelta(days=increment)

    def unused_tip_in_period(self):
        '''returns total amount of unallocated tips for the period'''
        return (labor(day).get_unallocated_tips() for day in self.days)

    def punctuality(self, selected_employees=None):
        '''returns a clockin report with a date of the week'''
        a = (labor(day).get_clockin_time() for day in self.days)
        df = pd.concat(a)
        if selected_employees:
            df = df.loc[df['EMPLOYEE'].isin(selected_employees)]
        _df = query_db(self.days[len(self.days)-1]).process_names(df=df,job_bool=False)
        _df.drop(columns=['EMPLOYEE','TERMINATED'],inplace=True)
        _df = _df[['FIRSTNAME','LASTNAME','DATE','INHOUR','INMINUTE','OUTHOUR','OUTMINUTE']]
        #for column in ['INHOUR','INMINUTE','OUTHOUR','OUTMINUTE']:
            #df[column].loc(lambda x: x > 12)
        #df['CLOCKIN'] = df['INHOUR'] + df['INMINUTE']
        #df['CLOCKOUT'] = df['OUTHOUR'] + df['OUTMINUTE']
        
        return _df
    
    def hourly_pay_rate(self):
        a = [labor(day).calc_hourly_pay_rate() for day in self.days]
        df = pd.concat(a)
        df.drop(labels=['CCTIPS', 'DECTIPS', 'SALES', 'TIPSHCON', 'INHOUR', 'INMINUTE', 'JOBCODE', 'OUTHOUR', 'OUTMINUTE', 'RATE'], axis=1, inplace=True)
        _df = query_db(self.days[len(self.days)-1]).process_names(df=df, job_bool=False)
        return _df

    def append_totals(
                    self,
                    df,
                    totaled_cols: list,
                    averaged_cols: list,
                    labor_main=False                    
                    ):
        try:
            for col in totaled_cols:
                df.loc['TTL', col] = np.sum(df[col])
            for col in averaged_cols:
                df.loc['TTL', col] = np.mean(df[col])
        except:
            pass

        #the employee column will be turned into the INDEX later
        if labor_main:
            df.loc['TTL','EMPLOYEE'] = 'TTL'
            df.loc['TTL','LASTNAME'] = 'TOTAL'
            df.loc['TTL','FIRSTNAME'] = 'TOTAL'
        return df

    def rate_rpt(
                self,
                rpt: str,
                totaled_cols: list, 
                averaged_cols: list,
                ):
        a = []
        if rpt == 'Tip':
            a = (labor(day).calc_tiprate_df() for day in self.days)
        elif rpt == 'Labor':
            a = (labor(day).calc_laborrate_df() for day in self.days)
        else:
            print('no proper data provided the following report is blank:')
            return pd.DataFrame({}) #returns a blank dataframe


        df = pd.concat(a).reset_index(drop=True)

        self.append_totals(df, 
            totaled_cols=totaled_cols, 
            averaged_cols=averaged_cols
            )

        return df
        

    def cout_by_eod(
                    self, 
                    cols: list,
                    cout_col: str
                    ):    
        '''returns a report listing all employees that have the 'CLOCKED OUT AT END OF DAY flag. (anyone who forgot to clock out)'''
        cout = [query_db(day).process_db('labor') for day in self.days]
        df = pd.concat(cout).reset_index(drop=True)
        df = df.loc[df[cout_col]=="Y"]
        _df = query_db(self.days[len(self.days)-1]).process_names(df=df)
        _df = _df[cols]

        return _df

    def labor_hourly_rate(self):
        return [labor(day).get_labor_rate(return_nan=False) for day in self.days]

    def get_total_sales(self):
        return [labor(day).get_total_sales() for day in self.days]

    #concatenates all the data into a proper report ready for a spreadsheet
    def labor_main(
                    self,
                    drop_cols: list,
                    index_cols: list,
                    totaled_cols: list,
                    addl_cols: list,
                    selected_employees=None,
                    selected_jobs=None,
                    sum_only=False, 
                    nightly=False,
                    append_totals=True
                    ): 
        '''this is the main labor report'''
        a = (labor(day).calc_payroll() for day in self.days)
        df = pd.concat(a)
        sorter = []
        #if any filter options are provided, fliter the data now. 
        #While it would be more efficent to filter the data BEFORE processing, it is neccisary as tips require each line data 
        if selected_employees and selected_jobs:
            df = df.loc[df['JOBCODE'].isin(selected_jobs) & df['EMPLOYEE'].isin(selected_employees)]
        elif selected_employees:
            df = df.loc[df['EMPLOYEE'].isin(selected_employees)]
        elif selected_jobs:
            df = df.loc[df['JOBCODE'].isin(selected_jobs)]

        if df.empty: #if there is no data left after filtering, return 'empty'
            return 'empty'

        if sum_only: #setting sum_only to true gives a list of total hours, ignoring the job type
            sorter = ['LASTNAME','FIRSTNAME','HOURS','OVERHRS','DECTIPS','SRVTIPS','TIPOUT','DECTIPS','UNALLOCTIPS']
            try:
                index_cols.remove('JOB_NAME')
            except:
                print('JOB_NAME not specified')
        else:
            sorter = ['LASTNAME','FIRSTNAME','JOB_NAME','HOURS','OVERHRS','SRVTIPS','TIPOUT','DECTIPS','UNALLOCTIPS']
        df['SYSDATEIN'] = pd.to_datetime(df['SYSDATEIN'], infer_datetime_format=True).dt.strftime("%a %b %e")        
        _df = query_db(self.days[len(self.days)-1]).process_names(df=df) #add employee names before generating report 
        _df.drop(drop_cols, axis=1, inplace=True) #if there any any columns passed in to drop, drop them
        _df = pd.pivot_table(_df,
                            index=index_cols,
                            aggfunc=np.sum, 
                            fill_value=np.NaN)
        #this block of code sets the index to employee numbers, sorts by last name, and adds totals
        _df.reset_index(inplace=True)
        if nightly == True:
            sorter = ['SYSDATEIN','LASTNAME','FIRSTNAME','HOURS','OVERHRS','SRVTIPS','TIPOUT','DECTIPS','UNALLOCTIPS']
            _df.sort_values(by=['SYSDATEIN', 'LASTNAME'], inplace=True)
        else:
            _df.sort_values(by=['LASTNAME', 'FIRSTNAME'], inplace=True)
        if append_totals:
            _df = self.append_totals(_df, totaled_cols=totaled_cols, averaged_cols=[], labor_main=True)
        _df.set_index('EMPLOYEE', inplace=True)
        _df.index.rename('ID', inplace=True)
        _df = _df[sorter]
    
        #if any additonal columns are requested, add them        
        if addl_cols is not None:
            for col in addl_cols:
                 _df[col] = np.NaN

        return _df

    def employees_in_dates(self):
        a = [labor(day).calc_emps_in_day() for day in self.days]
        df = pd.DataFrame(pd.concat(a))
        df.drop_duplicates(inplace=True)
        _df = query_db(self.days[len(self.days)-1]).process_names(df=df,job_bool=False)
        return _df

    def print_to_json(
                self, 
                rpt, 
                json_fmt,
                sum_only=False,
                selected_employees=None,
                selected_jobs=None, 
                ):
        #TODO include something so the frontend can know if the report is filtered or not ()
        if rpt == 'tip_rate':
            df = self.rate_rpt(
                rpt='Tip',
                totaled_cols=['Cash Tips', 'Takeout CC Tips', 'Server Tipshare', 'Total Tip Pool', 'Total Tip\'d Hours'], 
                averaged_cols=['Tip Hourly'])

        elif rpt == 'punctuality':
            df = self.punctuality(
                selected_employees=selected_employees)

        elif rpt == 'labor_main':
            df = self.labor_main(
                drop_cols=['RATE', 'TIPSHCON', 'TIP_CONT', 'SALES', 'CCTIPS', 'INHOUR', 'INMINUTE', 'OUTHOUR', 'OUTMINUTE', 'JOBCODE'],
                index_cols=['EMPLOYEE', 'LASTNAME', 'FIRSTNAME', 'JOB_NAME'],
                totaled_cols=['HOURS', 'OVERHRS', 'SRVTIPS', 'TIPOUT', 'DECTIPS', 'UNALLOCTIPS', 'TOTALTIPS'],
                addl_cols=['MEALS'],
                sum_only=sum_only, 
                selected_employees=selected_employees,
                selected_jobs=selected_jobs,
                nightly=False)

        elif rpt == 'labor_nightly':
            df = self.labor_main(
                drop_cols=['RATE', 'TIPSHCON', 'TIP_CONT', 'SALES', 'CCTIPS', 'INHOUR', 'INMINUTE', 'OUTHOUR', 'OUTMINUTE', 'JOBCODE', 'TERMINATED', 'INVALID', 'COUTBYEOD'],
                index_cols=['EMPLOYEE','LASTNAME', 'FIRSTNAME', 'JOB_NAME', 'SYSDATEIN'],
                totaled_cols=['HOURS', 'OVERHRS', 'SRVTIPS', 'TIPOUT', 'DECTIPS','UNALLOCTIPS', 'TOTALTIPS'],
                addl_cols=[],
                sum_only=sum_only, 
                selected_employees=selected_employees,
                selected_jobs=selected_jobs, 
                nightly=True)

        elif rpt == 'labor_totals':
            df = self.labor_main(
                drop_cols=['RATE', 'TIPSHCON', 'TIP_CONT', 'SALES', 'CCTIPS', 'INHOUR', 'INMINUTE', 'OUTHOUR', 'OUTMINUTE', 'JOBCODE', 'JOB_NAME'],
                index_cols=['EMPLOYEE', 'LASTNAME', 'FIRSTNAME'],
                totaled_cols=['HOURS', 'OVERHRS', 'SRVTIPS', 'TIPOUT', 'DECTIPS', 'UNALLOCTIPS', 'TOTALTIPS'],
                addl_cols=['MEALS'],
                sum_only=True, 
                selected_employees=selected_employees,
                selected_jobs=selected_jobs,
                nightly=False)

        elif rpt == 'labor_rate':
            df = self.rate_rpt(
                rpt='Labor',
                totaled_cols=['Total Pay', 'Total Sales', 'Reg Hours', 'Over Hours', 'Total Hours'], 
                averaged_cols=['Rate (%)'])

        elif rpt == 'cout_eod':
            df = self.cout_by_eod(
                cols=['SYSDATEIN', 'EMPLOYEE','FIRSTNAME','LASTNAME', 'JOB_NAME', 'INHOUR','INMINUTE', 'OUTHOUR', 'OUTMINUTE', 'COUTBYEOD'],
                cout_col='COUTBYEOD')

        elif rpt == 'labor_weekly':
            df = WeeklyWriter(
                self.first_day, 
                self.last_day).weekly_labor(
                    selected_jobs=selected_jobs, 
                    selected_employees=selected_employees, 
                    json_fmt=json_fmt)

        elif rpt == 'hourly':
            df = self.hourly_pay_rate()
            df = df[['SYSDATEIN','FIRSTNAME','LASTNAME','HOURS','OVERHRS','TOTAL_PAY','TOTALTIPS','ACTUAL_HOURLY']]
        else:
            raise ValueError('' + rpt + ' is an invalid selection - valid options: tip_rate, labor_rate, cout_eod, punctuality, labor_totals, labor_main, hourly')

        if type(df) == str: #if df is 'empty' don't try to round it
            return df
        else:
            return df.round(2)

class WeeklyWriter(ReportWriter):

    def __init__(self, first_day, last_day):
        self.first_day = first_day
        self.last_day = last_day
    
    def weekly_labor(self, selected_jobs, selected_employees, json_fmt):

        date_ranges = pd.date_range(start=self.first_day,end=self.last_day,freq='w-mon')
        #print(date_ranges)
        data = []
        for date in date_ranges:
            super().__init__(first_day=datetime.datetime.strftime(date, "%Y%m%d"), last_day=datetime.datetime.strftime((date+datetime.timedelta(days=6.9)), "%Y%m%d"), increment=1)
            t = self.labor_main(drop_cols=['RATE', 'TIPSHCON', 'TIP_CONT', 'SALES', 'CCTIPS', 'INHOUR', 'INMINUTE', 'OUTHOUR', 'OUTMINUTE', 'JOBCODE'],
                    index_cols=['EMPLOYEE', 'LASTNAME', 'FIRSTNAME', 'JOB_NAME'],
                    totaled_cols=['HOURS', 'OVERHRS', 'SRVTIPS', 'TIPOUT', 'DECTIPS'],
                    addl_cols=['DATE','SALES','RATE'],
                    sum_only=True,
                    append_totals=False,
                    selected_jobs=selected_jobs,
                    selected_employees=selected_employees)
            if type(t) != str:
                data.append(t)
                t['WEEK'] = date#.strftime('%b, %d, %a, %Y')
                t['SALES'] = np.sum(self.get_total_sales())
                t['RATE'] = (np.sum(self.labor_hourly_rate())/6)
        tmp_df = pd.concat(data)
        df = pd.DataFrame(tmp_df)
        if json_fmt:
            rtn_df = df.pivot_table(index=['WEEK','FIRSTNAME', 'SALES', 'RATE'], values=['OVERHRS'])
        else:
            rtn_df = df.pivot_table(index=['WEEK', 'SALES', 'RATE'],columns=['FIRSTNAME'], values=['OVERHRS'])
        rtn_df.sort_values(by=['WEEK'], inplace=True)
        return rtn_df

if __name__ == '__main__':
    print("loading ReportWriter.py")
    def main():
        #print(WeeklyWriter('20211101','20220128').weekly_labor(selected_jobs=[7,8]))
        #print(ReportWriter('20220107','20220107').print_to_json('labor_main'))
        print(ReportWriter('20220216','20220228').print_to_json(rpt='punctuality'))
    r = 1
    f = timeit.repeat("main()", "from __main__ import main", number=1, repeat=r)
    print("completed with an average of " + str(np.round(np.mean(f),2)) + " seconds over " + str(r) + " tries \n total time: " + str(np.round(np.sum(f),2)) + "s")