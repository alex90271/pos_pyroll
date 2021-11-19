#excel_writer.py
import pandas as pd
import os
import time
import timeit
import datetime
import numpy as np
from chip_config import ChipConfig
from report_writer import ReportWriter, WeeklyWriter

class ExcelPrinter():

    def __init__(self, first, last) -> None:
        self.FILEPATH = 'data/reports/'
        self.first = first
        self.last = last
    
    def get_full_date(self, date):
        '''pass date as YYYYMMDD and get it turned into: Mon Jan 1st, 2021'''
        return datetime.datetime.strptime(date, "%Y%m%d").strftime("%a %b %d, %Y")
        
    def print_to_excel(
                self, 
                rpt, 
                sum_only=False,
                pys_print=False, 
                selected_employees=None,
                selected_jobs=None,
                weekly_fmt=False
                ):
        '''
            currently supports 'tip_rate' 'labor_main' 'labor_rate' 'cout_eod' 'labor_total'
            returns true when the file is printed
        
        '''
        mod = ''
        rpt_modifier = '_'
        if sum_only or selected_employees or selected_jobs:
            mod = '_filtered'
        worksheet_name = (rpt + '_' + self.first + '_' + self.last)
        print(worksheet_name)
        try:
            os.mkdir(self.FILEPATH)
        except:
            pass

        writer = pd.ExcelWriter(self.FILEPATH + worksheet_name + mod + '.xlsx', engine='xlsxwriter') # pylint: disable=abstract-class-instantiated
        wrkbook = writer.book
        f1 = wrkbook.add_format({'border': 1, 'num_format' : '_(* #,##0.00_);_(* (#,##0.00);_(* "-"??_);_(@_)'}) #rounds all floats using excel
        f2 = wrkbook.add_format({'border': 1, 'num_format': '_($* #,##0.00_);_($* (#,##0.00);_($* "-"??_);_(@_)'}) #adds $
        f3 = wrkbook.add_format({'border': 1, 'num_format': '0'}) #no formatting

        if weekly_fmt:
            df = WeeklyWriter(self.first, self.last).weekly_labor(selected_jobs=selected_jobs)
        else:
            df = ReportWriter(self.first, self.last).print_to_json(
                    rpt=rpt, 
                    sum_only=sum_only, 
                    selected_employees=selected_employees, 
                    selected_jobs=selected_jobs)

        df.to_excel(writer, sheet_name=worksheet_name) #instantiate a blank excel file to write
        wrksheet = writer.sheets[worksheet_name] 
        
        if rpt == 'tip_rate':
            wrksheet.set_column('B:H', ChipConfig().query('RPT_TIP_RATE', 'col_width'), f1)
            #wrksheet.set_landscape()

        elif rpt == 'labor_main':
            if sum_only:
                rpt_modifier += "TOTALS_"
            if selected_employees:
                rpt_modifier += 'FILTERED ON EMPLOYEE_'
            if selected_jobs:
                rpt_modifier += 'FILTERED ON JOBCODE_'

            wrksheet.set_column('B:D', ChipConfig().query('RPT_LABOR_MAIN', 'col_width'), f1)
            wrksheet.set_column('E:G', 12, f1)
            wrksheet.set_column('H:J', 12, f2)

        elif rpt == 'labor_nightly':
            if sum_only:
                rpt_modifier += "TOTALS_"
            if selected_employees:
                rpt_modifier += 'FILTERED ON EMPLOYEE_'
            if selected_jobs:
                rpt_modifier += 'FILTERED ON JOBCODE_'

            wrksheet.set_column('B:E', ChipConfig().query('RPT_LABOR_MAIN', 'col_width'), f1)
            wrksheet.set_column('F:H', 12, f1)
            wrksheet.set_column('I:K', 12, f2)

        elif rpt == 'labor_rate':
            wrksheet.set_column('B:B', 20, f3)
            wrksheet.set_column('C:I', 12, f1)
            #wrksheet.set_landscape()

        elif rpt == 'cout_eod':
            wrksheet.set_column('B:M', 12, f3)
            wrksheet.set_column('G:H', 12, f1)

        else:
            raise ValueError('' + rpt + ' is an invalid selection - valid options: tip_rate, labor_main, labor_rate, cout_eod')

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
                &CREPORT DATES: {self.get_full_date(self.first)} --- {self.get_full_date(self.last)} 
                &RPAGE &P of &N
                &COPTIONS:{rpt_modifier}
                ''')
        wrksheet.set_footer(
                f'''
                DATE PRINTED: &D &T
                ''')

        writer.save()

        file = self.FILEPATH + worksheet_name + mod + '.xlsx'
        if os.path.isfile(file):
            print('EXPORT SUCCESS: ' + rpt + ' - ' + self.get_full_date(self.first) + ' - ' + self.get_full_date(self.last) + '')
            if pys_print: 
               self.pys_print(file)
            return True
        else:
            print('FAILED EXPORT: ' + rpt + ' - ' + self.get_full_date(self.first) + ' - ' + self.get_full_date(self.last) + '')
            return False

    def pys_print(self, file):
        '''invokes the windows print API to get the default printer and print the data'''
        print('PRINTING FILE .. PLEASE WAIT')
        if os.name != 'nt':
            print('\nPrint dialog support not available for non-windows OS ...skipping... \n')
            return False
        import win32api
        import win32print
        printer = win32print.GetDefaultPrinter() #win32print.EnumPrinters(2)
        sleep_time = 3
        win32api.ShellExecute(0, "print", 'data\\reports\\'+file[13:], '/d:"%s"' % printer, ".", 0)
        if printer == 'Microsoft Print to PDF':
            sleep_time = sleep_time + 10
        time.sleep(sleep_time)
        print(f'FINISHED PRINT JOB IN {sleep_time} SECONDS')

if __name__ == '__main__':
    print("loading ExcelPrinter.py")
    def main():
        os.environ['json_name'] = 'chip.json'
        a = ExcelPrinter('20211004','20211115').print_to_excel('labor_main', weekly_fmt=True)
        #a = a.loc[a['LASTNAME'] == 'Alder']
        print(a)
    r = 1
    f = timeit.repeat("main()", "from __main__ import main", number=1, repeat=r)
    print("completed with an average of " + str(np.round(np.mean(f),2)) + " seconds over " + str(r) + " tries \n total time: " + str(np.round(np.sum(f),2)) + "s")