from process_labor import ProcessLabor as labor
from query_db import QueryDB as query_db
from chip_config import ChipConfig
import numpy as np
import pandas as pd
import datetime
import os
import timeit
import time

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
            df.loc['TTL','JOB_NAME'] = 'TOTAL'
        return df

    def rate_rpt(
                self,
                rpt: str,
                totaled_cols: list, 
                averaged_cols: list,
                ):
        a = []
        if rpt == 'Tip':
            a = [labor(day).calc_tiprate_df() for day in self.days]
        elif rpt == 'Labor':
            a = [labor(day).calc_laborrate_df() for day in self.days]
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

    def labor_hourly(self):
        #hrly = [ for day in self.days]
        #df = pd.concat(hrly).reset_index(drop=True)
        return None

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
                    ): 
        '''this is the main labor report'''
        a = [labor(day).calc_payroll() for day in self.days]
        df = pd.concat(a)
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
            try:
                index_cols.remove('JOB_NAME')
            except:
                print('JOB_NAME not specified')
        df['SYSDATEIN'] = pd.to_datetime(df['SYSDATEIN'], infer_datetime_format=True).dt.strftime("%a %b %e")        
        _df = query_db(self.days[len(self.days)-1]).process_names(df=df) #add employee names before generating report 
        _df.drop(drop_cols, axis=1, inplace=True) #if there any any columns passed in to drop, drop them
        _df = pd.pivot_table(_df,
                            index=index_cols,
                            aggfunc=np.sum, 
                            fill_value=np.NaN)
        #if any additonal columns are requested, add them        
        if addl_cols is not None:
            for col in addl_cols:
                 _df[col] = np.nan
        #this block of code sets the index to employee numbers, sorts by last name, and adds totals
        _df.reset_index(inplace=True)
        if nightly == True:
            _df.sort_values(by=['SYSDATEIN', 'LASTNAME'], inplace=True)
        else:
            _df.sort_values(by=['LASTNAME'], inplace=True)
        _df = self.append_totals(_df, totaled_cols=totaled_cols, averaged_cols=[], labor_main=True)
        _df.set_index('EMPLOYEE', inplace=True)
        _df.index.rename('ID', inplace=True)
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
                sum_only=False,
                selected_employees=None,
                selected_jobs=None
                ):
        #TODO include something so the frontend can know if the report is filtered or not ()
        if rpt == 'tip_rate':
            df = self.rate_rpt(
                rpt='Tip',
                totaled_cols=['Cash Tips', 'Takeout CC Tips', 'Server Tipshare', 'Total Tip Pool', 'Total Tip\'d Hours'], 
                averaged_cols=['Tip Hourly']) 

        elif rpt == 'labor_main':
            df = self.labor_main(
                drop_cols=['RATE', 'TIPSHCON', 'TIP_CONT', 'SALES', 'CCTIPS', 'INHOUR', 'INMINUTE', 'OUTHOUR', 'OUTMINUTE', 'JOBCODE'],
                index_cols=['EMPLOYEE', 'LASTNAME', 'FIRSTNAME', 'JOB_NAME'],
                totaled_cols=['HOURS', 'OVERHRS', 'SRVTIPS', 'TIPOUT', 'DECTIPS'],
                addl_cols=['MEALS'],
                sum_only=sum_only, 
                selected_employees=selected_employees,
                selected_jobs=selected_jobs,
                nightly=False)

        elif rpt == 'labor_nightly':
            df = self.labor_main(
                drop_cols=['RATE', 'TIPSHCON', 'TIP_CONT', 'SALES', 'CCTIPS', 'INHOUR', 'INMINUTE', 'OUTHOUR', 'OUTMINUTE', 'JOBCODE', 'TERMINATED', 'INVALID', 'COUTBYEOD'],
                index_cols=['EMPLOYEE','LASTNAME', 'FIRSTNAME', 'JOB_NAME', 'SYSDATEIN'],
                totaled_cols=['HOURS', 'OVERHRS', 'SRVTIPS', 'TIPOUT', 'DECTIPS'],
                addl_cols=[],
                sum_only=sum_only, 
                selected_employees=selected_employees,
                selected_jobs=selected_jobs, 
                nightly=True)

        elif rpt == 'labor_rate':
            df = self.rate_rpt(
                rpt='Labor',
                totaled_cols=['Total Pay', 'Total Sales', 'Reg Hours', 'Over Hours', 'Total Hours'], 
                averaged_cols=['Rate (%)'])

        elif rpt == 'cout_eod':
            df = self.cout_by_eod(
                cols=['SYSDATEIN', 'EMPLOYEE','FIRSTNAME','LASTNAME', 'JOB_NAME', 'HOURS', 'OVERHRS','INHOUR','INMINUTE', 'OUTHOUR', 'OUTMINUTE', 'COUTBYEOD'],
                cout_col='COUTBYEOD')
        else:
            raise ValueError('' + rpt + ' is an invalid selection - valid options: tip_rate, labor_main, labor_rate, cout_eod')
            
        return df.round(2)

class WeeklyWriter(ReportWriter):

    def __init__(self, first_day, last_day):
        self.first_day = first_day
        self.last_day = last_day

    def getDateRangeFromWeek(self,p_year,p_week):
        #returns a date range from a week number, useful for weekly_labor function
        firstdayofweek = datetime.datetime.strptime(f'{p_year}-W{int(p_week )- 1}-1', "%Y-W%W-%w").date()
        lastdayofweek = firstdayofweek + datetime.timedelta(days=6.9)
        return firstdayofweek, lastdayofweek
    
    def weekly_labor(self):
        #0 = year, 1 = week, 2 = day
        week_start = datetime.datetime.strptime(self.first_day, "%Y%m%d").isocalendar()
        week_end = datetime.datetime.strptime(self.last_day, "%Y%m%d").isocalendar() 
        week_nums = []
        date_ranges = []

        for week_num in range(week_start[1],week_end[1]+1):
            week_nums.append(week_num)
            date_ranges.append((self.getDateRangeFromWeek(week_start[0],week_num)))

        for x in date_ranges:
            super().__init__(first_day=datetime.datetime.strftime(x[0], "%Y%m%d"), last_day=datetime.datetime.strftime(x[1], "%Y%m%d"), increment=1)
            print(self.labor_main(drop_cols=['RATE', 'TIPSHCON', 'TIP_CONT', 'SALES', 'CCTIPS', 'INHOUR', 'INMINUTE', 'OUTHOUR', 'OUTMINUTE', 'JOBCODE'],
                index_cols=['EMPLOYEE', 'LASTNAME', 'FIRSTNAME', 'JOB_NAME'],
                totaled_cols=['HOURS', 'OVERHRS', 'SRVTIPS', 'TIPOUT', 'DECTIPS'],
                addl_cols=['MEALS'],))

        print(date_ranges)

if __name__ == '__main__':
    print("loading ReportWriter.py")
    def main():
        os.environ['json_name'] = 'chip.json'
        print(WeeklyWriter('20211001','20211115').weekly_labor())
    r = 1
    f = timeit.repeat("main()", "from __main__ import main", number=1, repeat=r)
    print("completed with an average of " + str(np.round(np.mean(f),2)) + " seconds over " + str(r) + " tries \n total time: " + str(np.round(np.sum(f),2)) + "s")