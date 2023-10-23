import matplotlib.pyplot as plt
from process_labor import ProcessLabor as labor
from process_transactions import ProcessTransactions as transactions
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
        self.c = ChipConfig()

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

    def job_emp_filter(self, selected_employees, selected_jobs, _df):
        '''takes an input dataframe, and returns a filtered dataframe, based on the input selected employees and jobcodes'''
        if selected_employees and selected_jobs:
            _df = _df.loc[_df['JOBCODE'].isin(
                selected_jobs) & _df['EMPLOYEE'].isin(selected_employees)]
        elif selected_employees:
            _df = _df.loc[_df['EMPLOYEE'].isin(selected_employees)]
        elif selected_jobs:
            _df = _df.loc[_df['JOBCODE'].isin(selected_jobs)]
        
        if _df.empty:  # if there is no data left after filtering, return 'empty'
            return 'empty'
        else:
            return _df

    def tip_in_period(self, unused=False
                      ):
        '''returns total amount of tips for the period
            if unused=true then it will return the un-allocated tips for the period
        '''
        return (labor(day).get_tips_totals(unused=unused) for day in self.days)

    def punctuality(self, selected_employees, selected_jobs):
        '''returns a clockin report with a date of the week'''
        a = (labor(day).get_clockin_time() for day in self.days)
        df = pd.concat(a)
        df = self.job_emp_filter(selected_employees, selected_jobs, df)
        _df = query_db(self.days[len(self.days)-1]
                       ).process_names(df=df, job_bool=False)
        _df.drop(columns=['EMPLOYEE', 'TERMINATED'], inplace=True)
        _df = _df[['FIRSTNAME', 'LASTNAME', 'DATE',
                   'INHOUR', 'INMINUTE', 'OUTHOUR', 'OUTMINUTE']]
        # for column in ['INHOUR','INMINUTE','OUTHOUR','OUTMINUTE']:
        # df[column].loc(lambda x: x > 12)
        # df['CLOCKIN'] = df['INHOUR'] + df['INMINUTE']
        # df['CLOCKOUT'] = df['OUTHOUR'] + df['OUTMINUTE']

        return _df

    def hourly_pay_rate(self, selected_employees=None, selected_jobs=None, report=False):
        '''returns the hourly pay rate through the period'''
        a = [labor(day).calc_hourly_pay_rate() for day in self.days]
        reg_df = pd.concat(a)
        if selected_jobs:
            reg_df = self.job_emp_filter(None,selected_jobs, reg_df)
        reg_df.drop(labels=['CCTIPS', 'DECTIPS', 'SALES', 'TIPSHCON', 'INHOUR',
                            'INMINUTE', 'OUTHOUR', 'OUTMINUTE', 'RATE', 'SYSDATEIN'], axis=1, inplace=True)

        _df = pd.pivot_table(reg_df[['EMPLOYEE', 'ACTUAL_HOURLY']],
                             index=['EMPLOYEE'],
                             aggfunc=np.mean,
                             fill_value=np.NaN)
        if report:
            # readds totals for report
            _df = reg_df[['TTL_TIPS','TOTAL_PAY','HOURS','OVERHRS','EMPLOYEE']].join(_df, ['EMPLOYEE'])
            _df = query_db(self.days[len(self.days)-1]
                           ).process_names(df=_df, job_bool=False)
        # the _df is the df being returned
        if selected_employees:
            return self.job_emp_filter(selected_employees,None, _df)
        else:
            return _df

    def append_totals(
        self,
        df,
        totaled_cols: list,
        averaged_cols: list,
        labor_main=False
    ):
        for col in totaled_cols:
            df.loc['TTL', col] = np.sum(df[col])
        for col in averaged_cols:
            df.loc['TTL', col] = np.mean(df[col])
        

        # the employee column will be turned into the INDEX later
        if labor_main:
            df.loc['TTL', 'EMPLOYEE'] = 'TTL'
            df.loc['TTL', 'LASTNAME'] = 'TOTAL'
            df.loc['TTL', 'FIRSTNAME'] = 'TOTAL'
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
            return pd.DataFrame({})  # returns a blank dataframe
        df = pd.concat(a).reset_index(drop=True)
        
        if ((totaled_cols!=[]) & (averaged_cols!=[])):
            self.append_totals(df,
                totaled_cols=totaled_cols,
                averaged_cols=averaged_cols
        )  

        return df
    
    def rate_rpt_plot(
            self,
            rpt: str,
    ):
        df = self.rate_rpt(rpt=rpt, totaled_cols=[],averaged_cols=[])
        #df['Date'] = df['Date'].str[4:]
        plt.figure(figsize=(12, 9))
        df.pivot(index='Date', columns='Pool', values='Hourly')
        _df = df[['Hourly','Date']].pivot_table(index=['Date'], aggfunc=np.sum).reset_index()
        _df['Pool'] = 'Sum'
        _df.sort_values(by=['Date'][4:],inplace=True)
        df.sort_values(by=['Date'][4:],inplace=True)
        df = pd.concat([df,_df]).reset_index(drop=True)[['Pool','Date','Hourly']]
        print(df)
        plt.plot(df.pivot(index='Date', columns='Pool', values='Hourly'))
        plt.hlines(y=7.25, xmin=0, xmax=15, linewidth=2, color='r',label='Min Wage Threshold')
        plt.xticks(df['Date'], rotation=45, ha="right")
        plt.tight_layout()  # Adjust layout for better label display
        plt.savefig('foo.png')

    def cout_by_eod(
        self,
        cols: list,

        cout_col: str
    ):
        '''returns a report listing all employees that have the 'CLOCKED OUT AT END OF DAY flag. (anyone who forgot to clock out)'''
        cout = [query_db(day).process_db('labor') for day in self.days]
        df = pd.concat(cout).reset_index(drop=True)
        df = df.loc[df[cout_col] == "Y"]
        _df = query_db(self.days[len(self.days)-1]).process_names(df=df)
        _df = _df[cols]

        return _df

    def labor_hourly_rate(self):
        '''returns the labor rate to sales'''
        return [labor(day).get_labor_rate(return_nan=False) for day in self.days]

    def get_total_sales(self):
        return [labor(day).get_total_sales() for day in self.days]

    # concatenates all the data into a proper report ready for a spreadsheet
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
        append_totals=True,
    ):
        '''this is the main labor report'''
        a = (labor(day).get_pool_data() for day in self.days)
        df = pd.concat(a)
        # if any filter options are provided, fliter the data now.
        # While it would be more efficent to filter the data BEFORE processing, it is neccisary as tips require each line data
        df = self.job_emp_filter(selected_employees, selected_jobs, df)
        if type(df) == str:  # if df is 'empty' theres not point in doing anything else to it
            return df
        df['SYSDATEIN'] = pd.to_datetime(df['SYSDATEIN']).dt.strftime("%a %b %e")
        # add employee names before generating report
        _df = query_db(self.days[len(self.days)-1]).process_names(df=df)
        
        # if there any any columns passed in to drop, drop them
        _df.drop(drop_cols, axis=1, inplace=True)
        _df = pd.pivot_table(_df,
                             index=index_cols,
                             aggfunc=np.sum,
                             fill_value=np.NaN)
        
        # this block of code sets the index to employee numbers, sorts by last name, and adds totals
        _df.reset_index(inplace=True)
        if nightly:
            _df.sort_values(by=['SYSDATEIN', 'LASTNAME'], inplace=True)
        else:
            _df.sort_values(by=['LASTNAME', 'FIRSTNAME'], inplace=True)

        if append_totals:
            _df = self.append_totals(
                _df, totaled_cols=totaled_cols, averaged_cols=[], labor_main=True)
        _df.set_index('EMPLOYEE', inplace=True)
        _df.index.rename('ID', inplace=True)

        # if any additonal columns are requested, add them
        if addl_cols is not None:
            for col in addl_cols:
                _df[col] = np.NaN
        return _df

    def employees_in_dates(self):
        a = [labor(day).calc_emps_in_day() for day in self.days]
        df = pd.DataFrame(pd.concat(a))
        df.drop_duplicates(inplace=True)
        _df = query_db(self.days[len(self.days)-1]
                       ).process_names(df=df, job_bool=False)
        return _df

    def house_accounts(self):
        a = [transactions(day).get_total_byhouseid() for day in self.days]
        df = pd.DataFrame(pd.concat(a))
        _df = df.pivot_table(index=['HOUSEID'], aggfunc=np.sum)
        return _df

    def print_to_json(
        self,
        rpt,
        json_fmt=False,
        selected_employees=None,
        selected_jobs=None,
    ):
        


        if rpt == 'tip_rate':
            df = self.rate_rpt(
                rpt='Tip',
                totaled_cols=[
                    "Cash",
                    "Total_Pool"
                ],
                averaged_cols=["Hourly"])

        elif rpt == 'punctuality':
            df = self.punctuality(
                selected_employees=selected_employees,
                selected_jobs=selected_jobs,)

        elif rpt == 'labor_main':
            df = self.labor_main(
                drop_cols=['RATE', 'TIPSHCON', 'SALES', 'CCTIPS',
                           'INHOUR', 'INMINUTE', 'OUTHOUR', 'OUTMINUTE', 'JOBCODE', 'EXP_ID'],
                index_cols=['EMPLOYEE', 'LASTNAME', 'FIRSTNAME', 'JOB_NAME'],
                totaled_cols=['HOURS', 'OVERHRS',
                              'TTL_CONTRIBUTION', 'TTL_TIPS', 'DECTIPS'],
                addl_cols=[],
                selected_employees=selected_employees,
                selected_jobs=selected_jobs,
                nightly=False)
            # sort the columns
            if type(df) == str:  # if df is 'empty' don't try to round it
                return df
            df = df[['LASTNAME', 'FIRSTNAME', 'JOB_NAME', 'HOURS',
                     'OVERHRS', 'DECTIPS', 'TTL_CONTRIBUTION', 'TTL_TIPS']]

        elif rpt == 'labor_nightly':
            df = self.labor_main(
                drop_cols=[],
                index_cols=['EMPLOYEE', 'LASTNAME',
                            'FIRSTNAME', 'JOB_NAME', 'SYSDATEIN'],
                totaled_cols=['HOURS', 'OVERHRS',
                              'TTL_CONTRIBUTION', 'TTL_TIPS', 'DECTIPS'],
                addl_cols=[],
                selected_employees=selected_employees,
                selected_jobs=selected_jobs,
                nightly=True)
            # sort the columns
            if type(df) == str:  # if df is 'empty' don't try to round it
                return df
            df = df[['SYSDATEIN', 'LASTNAME', 'FIRSTNAME', 'HOURS',
                     'OVERHRS', 'TTL_CONTRIBUTION', 'TTL_TIPS', 'DECTIPS']]

        elif rpt == 'labor_total':
            df = self.labor_main(
                drop_cols=[],
                index_cols=['EMPLOYEE', 'LASTNAME', 'FIRSTNAME'],
                totaled_cols=['HOURS', 'OVERHRS',
                              'TTL_CONTRIBUTION', 'TTL_TIPS', 'DECTIPS'],
                addl_cols=[],
                sum_only=True,
                selected_employees=selected_employees,
                selected_jobs=selected_jobs,
                nightly=False)
            if type(df) == str:  # if df is 'empty' don't try to round it
                return df
            # sort the columns
            df = df[['LASTNAME', 'FIRSTNAME', 'HOURS',
                     'OVERHRS', 'TTL_TIPS', 'DECTIPS']]

        elif rpt == 'tipshare_detail':
            ttlrs = ['HOURS', 'OVERHRS']
            for pool in ['luncheon_pool', 'server_pool', 'takeout_pool']:
                ttlrs.append('CCTIP_' + pool)
                ttlrs.append('c_' + pool)
                ttlrs.append(pool)

            df = self.labor_main(
                drop_cols=['RATE', 'TIPSHCON', 'COUTBYEOD', 'INVALID', 'JOB_NAME','TERMINATED','SYSDATEIN',
                           'INHOUR', 'INMINUTE', 'OUTHOUR', 'OUTMINUTE', 'JOBCODE', 'JOBCODE1', 'EXP_ID', 'TTL_CONTRIBUTION', 'TTL_TIPS'],
                index_cols=['EMPLOYEE', 'LASTNAME', 'FIRSTNAME'],
                totaled_cols=ttlrs,
                addl_cols=[],
                sum_only=True,
                selected_employees=selected_employees,
                selected_jobs=selected_jobs,
                nightly=False)

        elif rpt == 'labor_rate':
            df = self.rate_rpt(
                rpt='Labor',
                totaled_cols=['Total Pay', 'Total Sales',
                              'Reg Hours', 'Over Hours', 'Total Hours'],
                averaged_cols=['Rate (%)'])

        elif rpt == 'cout_eod':
            df = self.cout_by_eod(
                cols=['SYSDATEIN', 'EMPLOYEE', 'FIRSTNAME', 'LASTNAME', 'JOB_NAME',
                      'INHOUR', 'INMINUTE', 'OUTHOUR', 'OUTMINUTE', 'COUTBYEOD'],
                cout_col='COUTBYEOD')

        elif rpt == 'labor_weekly':
            df = WeeklyWriter(
                self.first_day,
                self.last_day).weekly_labor(
                    selected_jobs=selected_jobs,
                    selected_employees=selected_employees,
                    json_fmt=json_fmt)

        elif rpt == 'labor_avg_hours':
            df = WeeklyWriter(
                self.first_day,
                self.last_day).weekly_labor(
                    selected_jobs=selected_jobs,
                    selected_employees=selected_employees,
                    json_fmt=json_fmt,
                    avg_hrs=True)

        elif rpt == 'hourly':
            df = self.hourly_pay_rate(
                selected_employees=selected_employees,
                selected_jobs=selected_jobs,
                report=True
            )
            if type(df) == str:  # if df is 'empty' don't try to round it
                return df
            #df = df[['FIRSTNAME', 'LASTNAME', 'ACTUAL_HOURLY']]

        elif rpt == 'tip_rate_plot':
            df = self.rate_rpt_plot()
            raise ValueError("BETA REPORT\nReport was exported\nThere are no guarantees of accuracy of this report")

        elif rpt == 'house_acct':
            df = self.house_accounts()
            raise ValueError("BETA REPORT\nReport was exported\nThere are no guarantees of accuracy of this report")
        else:
            raise ValueError(
                '' + rpt + ' is an invalid selection - valid options: tip_rate, labor_rate, cout_eod, punctuality, labor_totals, labor_main, hourly')

        return df.round(2)


class ReportWriterReports():

    def available_reports(self):
        return ['labor_main',
            'labor_total',
            'labor_weekly',
            'tipshare_detail',
            'punctuality',
            'hourly',
            'tip_rate',
            'labor_rate',
            'cout_eod',
            'labor_avg_hours']


class Payroll(ReportWriter):
    def __init__(self, first_day, last_day):
        self.first_day = first_day
        self.last_day = last_day

        self.c = ChipConfig()
        self.primary = query_db(last_day).primary_jobcodes().set_index('ID')

    def process_payroll(self):
        '''PROCESSES PAYROLL EXPORT FOR GUSTO INTEGRATION'''
        super().__init__(first_day=self.first_day, last_day=self.last_day)
        df = self.labor_main(
            drop_cols=[],
            index_cols=['EMPLOYEE', 'LASTNAME',
                        'FIRSTNAME', 'JOB_NAME', 'JOBCODE', 'EXP_ID'],
            totaled_cols=[],
            addl_cols=[],
            append_totals=False)
        
        df['TTL_TIPS'] = df['TTL_TIPS'] - df['AUTGRTTOT']

        # need hours by jobcode, but total tips
        df_hours = df[['LASTNAME', 'FIRSTNAME',
                       'JOB_NAME', 'JOBCODE', 'HOURS', 'OVERHRS', 'EXP_ID']]

        df_tips = df[['LASTNAME', 'FIRSTNAME',
                      'DECTIPS', 'TTL_TIPS',
                      'AUTGRTTOT', 'EXP_ID']]
        
        df_tips = pd.pivot_table(df_tips,
                                 index=['ID', 'LASTNAME', 'FIRSTNAME', 'EXP_ID'],
                                 aggfunc=np.sum,
                                 fill_value=np.NaN).reset_index().set_index('ID')

        #hr_df = self.hourly_pay_rate()
        #hr_df.index.rename('ID', inplace=True)
        #self.primary = self.primary.join(hr_df, ['ID'])
        self.primary['ACTUAL_HOURLY'] = ''
        #self.primary['ACTUAL_HOURLY'] = '**see paystub for actual pay info** Average Hourly (with Tips): ' + \
            #self.primary['ACTUAL_HOURLY'].astype(str)
        
        # some magic merging to get the format needed for gusto (first jobcode must be primary and all tips have to be under primary-- but we still need hours broken down by jobcode)
        df = self.primary.merge(df_tips, how='inner', on='ID')
        df = df_hours.merge(df, how='outer', on=[
                            'ID', 'JOBCODE', 'FIRSTNAME', 'LASTNAME', 'EXP_ID'])
        df['JOB_NAME_y'] = np.where(df['JOB_NAME_y'].astype(
            str) == 'nan', df['JOB_NAME_x'].astype(str), df['JOB_NAME_y'].astype(str))

        # drop interface employees
        for x in self.c.query("SETTINGS", "interface_employees", return_type='int_array'):
            try:
                df.drop([float(x)], inplace=True, errors=False)
            except:
                pass
        # match gusto columns
        # ['last_name','first_name','title','gusto_employee_id','regular_hours','overtime_hours','paycheck_tips','cash_tips','personal_note']
        df.rename(columns={'LASTNAME': 'last_name', 'FIRSTNAME': 'first_name', 'JOB_NAME_y': 'title', 'EXP_ID': 'gusto_employee_id',
                           'HOURS': 'regular_hours', 'OVERHRS': 'overtime_hours', 'TTL_TIPS': 'paycheck_tips', 'DECTIPS': 'cash_tips', 'ACTUAL_HOURLY':'personal_note','AUTGRTTOT':'custom_earning_gratuity'}, inplace=True)
        df = df.sort_values(by='ID')
        df = df[['last_name', 'first_name', 'title', 'gusto_employee_id', 'regular_hours',
                 'overtime_hours', 'paycheck_tips', 'cash_tips', 'custom_earning_gratuity', 'personal_note']]

        return df


class WeeklyWriter(ReportWriter):

    def __init__(self, first_day, last_day):
        self.first_day = first_day
        self.last_day = last_day

    def weekly_labor(self, selected_jobs, selected_employees, json_fmt, avg_hrs=False):

        date_ranges = pd.date_range(
            start=self.first_day, end=self.last_day, freq='w-mon')
        # print(date_ranges)
        data = []
        if avg_hrs:
            for date in date_ranges:
                super().__init__(first_day=datetime.datetime.strftime(date, "%Y%m%d"),
                                last_day=datetime.datetime.strftime((date+datetime.timedelta(days=6.9)), "%Y%m%d"), increment=1)
                t = self.labor_main(drop_cols=['RATE', 'TIPSHCON', 'TTL_CONTRIBUTION', 'SALES', 'CCTIPS', 'INHOUR', 'INMINUTE', 'OUTHOUR', 'OUTMINUTE', 'JOBCODE', 'CCTIP_luncheon_pool', 'CCTIP_server_pool', 'CCTIP_takeout_pool', 'c_luncheon_pool', 'c_server_pool', 'c_takeout_pool'],
                                    index_cols=['EMPLOYEE', 'LASTNAME',
                                                'FIRSTNAME'],
                                    totaled_cols=[],
                                    addl_cols=[],
                                    sum_only=True,
                                    append_totals=False).reset_index()
                if type(t) != str:
                    data.append(t)
            df = pd.concat(data)
            print(df)
            rtn_df = df.pivot_table(index=['FIRSTNAME'], values=['HOURS', 'OVERHRS'], aggfunc=np.average)

            return rtn_df
        else:
            for date in date_ranges:
                super().__init__(first_day=datetime.datetime.strftime(date, "%Y%m%d"),
                                last_day=datetime.datetime.strftime((date+datetime.timedelta(days=6.9)), "%Y%m%d"), increment=1)
                t = self.labor_main(drop_cols=['RATE', 'TIPSHCON', 'TTL_CONTRIBUTION', 'SALES', 'CCTIPS', 'INHOUR', 'INMINUTE', 'OUTHOUR', 'OUTMINUTE', 'JOBCODE', 'CCTIP_luncheon_pool', 'CCTIP_server_pool', 'CCTIP_takeout_pool', 'c_luncheon_pool', 'c_server_pool', 'c_takeout_pool'],
                                    index_cols=['EMPLOYEE', 'LASTNAME',
                                                'FIRSTNAME','JOB_NAME'],
                                    totaled_cols=['HOURS', 'OVERHRS',
                                                'SRVTIPS', 'TIPOUT', 'DECTIPS'],
                                    addl_cols=['DATE', 'SALES', 'RATE'],
                                    sum_only=True,
                                    append_totals=False,
                                    selected_jobs=selected_jobs,
                                    selected_employees=selected_employees)
                if type(t) != str:
                    data.append(t)
                    t['WEEK'] = date  # .strftime('%b, %d, %a, %Y')
                    t['SALES'] = np.sum(self.get_total_sales())
                    t['RATE'] = (np.sum(self.labor_hourly_rate())/6)

            df = pd.concat(data)

        if json_fmt:
            rtn_df = df.pivot_table(
                index=['WEEK', 'FIRSTNAME', 'SALES', 'RATE'], values=['HOURS'])
        else:
            rtn_df = df.pivot_table(index=['WEEK', 'SALES', 'RATE'], columns=[
                                    'FIRSTNAME'], values=['HOURS'])
            
        rtn_df.sort_values(by=['WEEK'], inplace=True)
        return rtn_df


if __name__ == '__main__':
    print("loading ReportWriter.py")

    def main():
        # print(WeeklyWriter('20211101','20220128').weekly_labor(selected_jobs=[7,8]))
        # print(ReportWriter('20230301', '20230315').print_to_json('house_acct'))
         print(ReportWriter('20230912','20230919').hourly_pay_rate(report=True, selected_jobs=[1]))
        # print(Payroll('20230401', '20230401').process_payroll())
    r = 1
    f = timeit.repeat("main()", "from __main__ import main",
                      number=1, repeat=r)
    print("completed with an average of " + str(np.round(np.mean(f), 2)) + " seconds over " +
          str(r) + " tries \n total time: " + str(np.round(np.sum(f), 2)) + "s")
