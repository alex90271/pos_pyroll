from process_labor import ProcessLabor as labor
from query_db import QueryDB as query_db
from chip_config import ChipConfig
import numpy as np
import pandas as pd
import datetime
import os
import timeit

class ReportWriter():

    def __init__(self, first_day, last_day=None, increment=1):
        self.first_day = first_day
        self.last_day = last_day
        self.days = []

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
        self.first_full = datetime.datetime.strptime(self.first_day, "%Y%m%d").strftime("%a %b %d, %Y")
        self.last_full = datetime.datetime.strptime(self.last_day, "%Y%m%d").strftime("%a %b %d, %Y")
    
    def append_totals(
                    self,
                    df,
                    totaled_cols: list,
                    averaged_cols: list,                    
                    ):
        for col in totaled_cols:
            df.at['TTL', col] = np.sum(df[col])
        for col in averaged_cols:
            df.at['TTL', col] = np.mean(df[col])

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

    #concatenates all the data into a proper report ready for a spreadsheet
    def labor_main(
                    self,
                    drop_cols: list,
                    index_cols: list,
                    totaled_cols: list,
                    addl_cols: list,
                    selected_employees=None,
                    selected_jobs=None,
                    sum_only=False
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

        if sum_only: #setting sum_only to true gives a list of total hours, ignoring the job type
            try:
                index_cols.remove('JOB_NAME')
            except:
                print('JOB_NAME not specified')

        _df = query_db(self.days[len(self.days)-1]).process_names(df=df) #add employee names before generating report 
        _df = _df.drop(drop_cols, axis=1)
        _df = pd.pivot_table(_df,
                            index=index_cols,
                            aggfunc=np.sum, 
                            fill_value=np.NaN)
        try:
            _df = _df[totaled_cols]
            self.append_totals(_df, totaled_cols=totaled_cols, averaged_cols=[])
        except:
            _df[totaled_cols] = np.nan

        if addl_cols is not None:
            for col in addl_cols:
                 _df[col] = np.nan

        return _df.reset_index()

    def print_to_excel(
                self, 
                rpt, 
                opt_print=False, 
                sum_only=False, 
                selected_employees=None,
                selected_jobs=None
                ):
        '''
            currently supports 'tip_rate' 'labor_main' 'labor_rate' 'cout_eod' 'labor_total'
            returns true when the file is printed
        
        '''
        mod = ''
        rpt_modifier = '_'
        if sum_only or selected_employees or selected_jobs:
            mod = '_filtered'
        _error_print_flag = False
        worksheet_name = (rpt + '_' + self.first_day + '_' + self.last_day)
        try:
            os.mkdir('reports')
        except:
            pass
        df = pd.DataFrame({})
        writer = pd.ExcelWriter('reports/' + worksheet_name + mod + '.xlsx', engine='xlsxwriter') # pylint: disable=abstract-class-instantiated
        df.to_excel(writer, sheet_name=worksheet_name) #instantiate a blank excel file to write
        wrkbook = writer.book
        wrksheet = writer.sheets[worksheet_name]
        f1 = wrkbook.add_format({'border': 1, 'num_format' : '_(* #,##0.00_);_(* (#,##0.00);_(* "-"??_);_(@_)'}) #rounds all floats using excel
        f2 = wrkbook.add_format({'border': 1, 'num_format': '_($* #,##0.00_);_($* (#,##0.00);_($* "-"??_);_(@_)'}) #adds $
        f3 = wrkbook.add_format({'border': 1, 'num_format': '0'}) #no formatting
        
        if rpt == 'tip_rate':
            df = self.rate_rpt(
                rpt='Tip',
                totaled_cols=['Cash Tips', 'Takeout CC Tips', 'Server Tipshare', 'Total Tip Pool', 'Total Tip\'d Hours'], 
                averaged_cols=['Tip Hourly'])
            wrksheet.set_column('B:H', ChipConfig().query('RPT_TIP_RATE', 'col_width'), f1)
            wrksheet.set_landscape()

        elif rpt == 'labor_main':
            df = self.labor_main(
                drop_cols=['RATE', 'TIPSHCON', 'TIP_CONT', 'SALES', 'CCTIPS', 'INHOUR', 'INMINUTE', 'OUTHOUR', 'OUTMINUTE', 'JOBCODE', 'EMPLOYEE'],
                index_cols=['LASTNAME', 'FIRSTNAME', 'JOB_NAME'],
                totaled_cols=['HOURS', 'OVERHRS', 'SRVTIPS', 'TIPOUT', 'DECTIPS'],
                addl_cols=['MEALS'],
                sum_only=sum_only, 
                selected_employees=selected_employees,
                selected_jobs=selected_jobs)

            if sum_only:
                rpt_modifier += "TOTALS"
            if selected_employees:
                rpt_modifier += 'FILTERED ON EMPLOYEE'
            if selected_jobs:
                rpt_modifier += 'FILTERED ON JOBCODE'

            wrksheet.set_column('B:D', ChipConfig().query('RPT_LABOR_MAIN', 'col_width'), f1)
            wrksheet.set_column('E:F', 12, f1)
            wrksheet.set_column('G:J', 12, f2)

        elif rpt == 'labor_rate':
            df = self.rate_rpt(
                rpt='Labor',
                totaled_cols=['Total Pay', 'Total Sales', 'Reg Hours', 'Over Hours', 'Total Hours'], 
                averaged_cols=['Rate (%)'])
            wrksheet.set_column('B:B', 20, f3)
            wrksheet.set_column('C:I', 12, f1)
            wrksheet.set_landscape()

        elif rpt == 'cout_eod':
            df = self.cout_by_eod(
                cols=['SYSDATEIN', 'EMPLOYEE','FIRSTNAME','LASTNAME', 'JOB_NAME', 'HOURS', 'OVERHRS','INHOUR','INMINUTE', 'OUTHOUR', 'OUTMINUTE', 'COUTBYEOD'],
                cout_col='COUTBYEOD')
            wrksheet.set_column('B:M', 12, f3)
            wrksheet.set_column('G:H', 12, f1)

        else:
            _error_print_flag = True
            raise ValueError('' + rpt + ' is an invalid selection - valid options: tip_rate, labor_main, labor_rate, cout_eod')
            

        if opt_print == 'False':
            return df
        elif opt_print == False:
            return df 

        if _error_print_flag == False:
            df.to_excel(writer, sheet_name=worksheet_name, float_format="%.2f") #write with the updated data
        
        #boilerplate stuff to turn the spreadsheet more into a report
        wrksheet.set_column('A:A', 4, f3) #make index column small
        wrksheet.repeat_rows(0) #repeat first row
        wrksheet.set_margins(left=0.5, right=0.5, top=0.7, bottom=0.7)
        wrksheet.fit_to_pages(1,0) #fits all columns to one page
        wrksheet.set_default_row(20)

        #report header and footer
        wrksheet.set_header(
                f'''
                &LREPORT TYPE: {rpt} 
                &CREPORT DATES: {self.first_full} --- {self.last_full} 
                &RPAGE &P of &N
                &COPTIONS:{rpt_modifier}
                ''')
        wrksheet.set_footer(
                f'''
                DATE PRINTED: &D &T
                ''')

        if _error_print_flag == False:
            writer.save()
        else: 
            pass

        if os.path.isfile('reports/' + worksheet_name + '.xlsx'):
            print('PRINTED: ' + rpt + ' - ' + self.first_full + ' - ' + self.last_full + '')
            return True
        else:
            print('FAILED: ' + rpt + ' - ' + self.first_full + ' - ' + self.last_full + '')
            return False

if __name__ == '__main__':
    print("loading ReportWriter.py")
    def main():
        os.environ['json_name'] = 'chip.json'
        ReportWriter('20210416','20210430').print_to_excel('labor_rate')
    r = 1
    f = timeit.repeat("main()", "from __main__ import main", number=1, repeat=r)
    print("completed with an average of " + str(np.round(np.mean(f),2)) + " seconds over " + str(r) + " tries \n total time: " + str(np.round(np.sum(f),2)) + "s")