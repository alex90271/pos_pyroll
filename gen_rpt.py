from process_labor import process_labor as labor
from process_tips import process_tips as tips
from query_db import query_db as query_db
from datetime import date
import xlsxwriter
import numpy as np
import pandas as pd
import datetime
import os

class gen_rpt():

    def __init__(self, first_day, last_day=None, increment=1):
        self.first_day = first_day
        self.last_day = last_day
        self.days = []

        if last_day == None:
            self.days.append(first_day)
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
                averaged_cols: list
                ):
        a = []
        if rpt == 'Tip':
            a = [tips(day).calc_tiprate_df() for day in self.days]
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
        cout = [query_db(day).process_db('labor') for day in self.days]
        df = pd.concat(cout).reset_index(drop=True)
        df = df.loc[df[cout_col]=="Y"]
        _df = query_db(self.days[len(self.days)-1]).process_names(df=df)
        _df = _df[cols]

        return _df

    #concatenates the data
    def labor_main(
                    self,
                    drop_cols: list,
                    index_cols: list,
                    totaled_cols: list,
                    addl_cols: list
                    ): 
        a = [tips(day).calc_payroll() for day in self.days]
        df = pd.concat(a)
        _df = query_db(self.days[len(self.days)-1]).process_names(df=df)
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

    def print_to_excel(self, rpt):
        '''
            currently supports 'tip_rate' 'labor_main' 'labor_rate' 'cout_eod' 
            returns true when the file is printed
        
        '''
        file_name = (rpt + '_' + self.first_day + '_' + self.last_day + '.xlsx')
        try:
            os.mkdir('reports')
        except:
            pass
        df = pd.DataFrame({})
        writer = pd.ExcelWriter('reports/' + file_name, engine='xlsxwriter') # pylint: disable=abstract-class-instantiated
        df.to_excel(writer, sheet_name=file_name[:-5]) #instantiate a blank excel file to write, -5 to remove the .xlsx
        wrkbook = writer.book
        wrksheet = writer.sheets[file_name[:-5]]
        f1 = wrkbook.add_format({'border': 1, 'num_format' : '_(* #,##0.00_);_(* (#,##0.00);_(* "-"??_);_(@_)'}) #rounds all floats
        f2 = wrkbook.add_format({'border': 1, 'num_format': '_($* #,##0.00_);_($* (#,##0.00);_($* "-"??_);_(@_)'}) #adds $
        f3 = wrkbook.add_format({'border': 1, 'num_format': '0'}) #no formatting
        
        if rpt == 'tip_rate':
            df = self.rate_rpt(
                rpt='Tip',
                totaled_cols=['Cash Tips', 'Takeout CC Tips', 'Server Tipshare', 'Total Tip Pool', 'Total Tip\'d Hours'], 
                averaged_cols=['Tip Hourly'])
            wrksheet.set_column('B:H', 15, f1)
            wrksheet.set_landscape()
        elif rpt == 'labor_main':
            df = self.labor_main(
                drop_cols=['RATE', 'TIPSHCON', 'TIP_CONT', 'SALES', 'CCTIPS', 'INHOUR', 'INMINUTE', 'OUTHOUR', 'OUTMINUTE', 'JOBCODE'],
                index_cols=['LASTNAME', 'FIRSTNAME', 'EMPLOYEE', 'JOB_NAME'],
                totaled_cols=['HOURS', 'OVERHRS', 'SRVTIPS', 'TIPOUT', 'DECTIPS'],
                addl_cols=['MEALS'])
            wrksheet.set_column('B:E', 10, f1)
            wrksheet.set_column('F:G', 8, f1)
            wrksheet.set_column('D:D', 6, f3) #employee numbers 
            wrksheet.set_column('H:K', 8, f2)
        elif rpt == 'labor_rate':
            df = self.rate_rpt(
                rpt='Labor',
                totaled_cols=['Total Pay', 'Total Sales', 'Reg Hours', 'Over Hours', 'Total Hours'], 
                averaged_cols=['Rate (%)'])
            wrksheet.set_column('B:H', 12, f1)
            wrksheet.set_landscape()
        elif rpt == 'cout_eod':
            df = self.cout_by_eod(
                cols=['SYSDATEIN', 'EMPLOYEE','FIRSTNAME','LASTNAME', 'JOB_NAME', 'HOURS', 'OVERHRS','INHOUR','INMINUTE', 'OUTHOUR', 'OUTMINUTE', 'COUTBYEOD'],
                cout_col='COUTBYEOD')
            wrksheet.set_column('B:M', 10, f3)
            wrksheet.set_column('G:H', 10, f1)
        else:
            print('' + rpt + ' is an invalid selection - valid options: tip_rate, labor_main, labor_rate, cout_eod')
            return False

        wrksheet.set_column('A:A', 4, f3) #make index column small
        df.to_excel(writer, sheet_name=file_name[:-5], header=df.keys(), float_format="%.2f") #write with the updated data
        wrksheet.set_header('REPORT DATES: ' + self.first_full + ' --- ' + self.last_full + '\nREPORT TYPE: ' + rpt)
        wrksheet.set_footer('DATE AND TIME PRINTED: ' + date.today().strftime("%a %b %d, %Y, %H:%M:%S"))
        writer.save()

        if os.path.isfile('reports/' + file_name):
            print('PRINTED: ' + rpt + ' - ' + self.first_full + ' - ' + self.last_full + '')
            return True
        else:
            print('FAILED: ' + rpt + ' - ' + self.first_full + ' - ' + self.last_full + '')
            return False

if __name__ == '__main__':
    print("loading gen_rpt.py")
    for rpt in ['tip_rate', 'labor_main', 'labor_rate', 'cout_eod']:
        gen_rpt('20210101','20210115').print_to_excel(rpt)
    