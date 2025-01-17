from datetime import date, datetime, timedelta
import warnings
from tkinter import END, SUNKEN, W, S, Listbox, StringVar, Tk, Label, OptionMenu, Frame, Toplevel
from tkinter import ttk
from tkinter.messagebox import askokcancel, askyesno, showerror, showinfo
from tkinter.ttk import Button, Combobox, Frame, Separator, Style
import numpy as np
from google_sheets import GoogleSheetsUpload
from tkcalendar import DateEntry
import pandas as pd
from process_pools import ProcessPools
import jinja2
from query_db import QueryDB
from report_writer import Payroll, ReportWriter, ReportWriterReports
from gui_adjustments import AdjustmentsGui
from chip_config import ChipConfig
from pandastable import Table
import pdfkit
import os

class ChipGui():

    def __init__(self, icon="", title="Title"):
        #call database
        yesterday = (date.today()-timedelta(days=1)).strftime('%Y%m%d')
        self.employee_df = QueryDB(yesterday).process_db('employees').set_index('ID')
        self.jobcode_df = QueryDB(yesterday).process_db('jobcodes').set_index('ID')
        self.employee_df['NAME'] = self.employee_df['FIRSTNAME'] + ' ' + self.employee_df['LASTNAME']
        self.reports = ReportWriterReports().available_reports()
        self.verbose_debug = ChipConfig().query(
            'SETTINGS', 'verbose_debug', return_type='bool')
        if not self.verbose_debug:
            warnings.simplefilter(action='ignore', category=FutureWarning)
        #window setup
        self.root = Tk()
        self.title = title
        self.root.wm_title(title)
        self.root.geometry("460x700")

        if os.name == 'posix':
            style = ttk.Style(self.root)
            style.theme_use('clam')
        
        #tk font
        Style().configure('.', font=('Verdana', 12))
        self.root.option_add("*font", ("Verdana", 12))

        try:
            self.icon = icon
            self.root.iconbitmap(icon)
        except:
            print("error loading icon")

        #selections
        self.day_one = yesterday
        self.day_two = yesterday
        self.rpt_type = "labor_main"
        self.select_emps = []
        self.select_jobs = []
        
        self.main_window()

    def view_rpt(self):
        report_window = Toplevel()
        report_window.iconbitmap(self.icon)
        report_window.wm_title(self.title)
        report_frame = Frame(report_window)
        report_frame.grid()
        print('PROCESSING: ' + ' ' + self.day_one + ' ' + self.day_two + ' ' + self.rpt_type)
        if self.rpt_type == 'labor_avg_hours' or self.rpt_type =='labor_weekly':
            if (int(self.day_two) - int(self.day_one)) < 14:
                showerror('Error', "You must select a range greater than two weeks")
                return 0 #exit the program if no data to display
            
        df = ReportWriter(self.day_one, self.day_two).print_to_json(
            self.rpt_type, selected_employees=self.select_emps, selected_jobs=self.select_jobs, json_fmt=True)
        if type(df) == str:
            showinfo('Note', "There is no data to display for this selection\n(This is not an error)")
            pt.delete()
            return 0 #exit the program if no data to display
        
        df.reset_index(inplace=True)
        if self.verbose_debug:
            df.to_csv('debug/latest_viewed.csv')

        #df.to_dict(orient='index')
        pt = Table(report_frame, dataframe=df, width=1100, height=600,
                showstatusbar=True)
        pt.autoResizeColumns()
        pt.show()
        
    def export_rpt(self):
            print('PROCESSING: ' + ' ' + self.day_one + ' ' + self.day_two + ' ' + self.rpt_type)
            df = ReportWriter(self.day_one, self.day_two).print_to_json(
                self.rpt_type, selected_employees=self.select_emps, selected_jobs=self.select_jobs, json_fmt=True)
            if type(df) == 'empty':
                showinfo('Note', "There is no data to display for this selection\n(This is not an error)")
                return '' #exit the program if no data to display
            result = df.fillna('')
            env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(searchpath="templates/"))
            template = env.get_template('render.html').render(
                tables=[result.to_html(
                    table_id="table", classes="ui striped table")],
                titles=result.columns.values,
                timestamp=datetime.now().strftime('%b %d %Y (%I:%M:%S%p %Z)'),
                dates=[
                    datetime.strptime(self.day_one, "%Y%m%d").strftime(
                        '%a, %b %d, %Y'),
                    datetime.strptime(self.day_two, "%Y%m%d").strftime(
                        '%a, %b %d, %Y')
                ],
                rpttp=self.rpt_type,
                select_emps=self.select_emps, select_jobs=self.select_jobs)
            export_dir = "/exports/"
            name_string = self.rpt_type + '-' + self.day_one[-6:] + '-' + self.day_two[-6:]
            cur_directory = os.path.abspath(os.getcwd())
            extention = ".pdf"
            export_path = cur_directory + export_dir + name_string + extention
            pdfkit.from_string(input=template,
                            output_path=(export_path),
                            configuration=pdfkit.configuration(wkhtmltopdf=cur_directory+"/wkhtmltox/bin/wkhtmltopdf.exe"))
            try:
                printer_name = win32print.GetDefaultPrinter()
                print("trying: " + printer_name)
                win32api.ShellExecute (
                0,
                "print",
                export_path,
                #
                # If this is None, the default printer will
                # be used anyway.
                #
                '/d:"%s"' % printer_name,
                ".",
                0
                )
                showinfo('Note', "The report has been printed\nCheck Printer: " + printer_name)                          
            except:
                showerror('Error', "There was a printer error\nCheck the exports folder for a PDF\n\nNote: Adobe Acrobat Reader should be installed")

    def gusto_rpt(self):
            result = True
            if (pd.date_range(self.day_one, periods=1, freq='SM').strftime("%Y%m%d")[0] != self.day_two):
                #changes to false if the user clicks no
                result = askyesno("***CAUTION***", ("***CAUTION***\nYou have selected a NON STANDARD payroll interval for export\nPlease double check your days!\n\nFirst day: " + datetime.strptime(self.day_one, "%Y%m%d").strftime("%b %d, %y") + "\nLast day: " + datetime.strptime(self.day_two, "%Y%m%d").strftime("%b %d, %y") + "\n \nWould you like export the NON STANDARD payroll?"))
            if result:
                print('PROCESSING: ' + ' ' + self.day_one + ' ' + self.day_two + ' ' + self.rpt_type)
                '''exports payroll to gusto'''
                result = Payroll(self.day_one, self.day_two).process_payroll()
                
                if type(result) == 'empty':
                    showinfo('Note', "There is no data to export for this selection\n(This is not an error)")
                    return '' #exit the program if no data to export
                name_string = 'payroll_csv-' + self.day_one + '-through-' + self.day_two
                result.to_csv(
                    ("exports/" + name_string + '.csv'),
                    index=False)
                
                response = askyesno("Export to Google Sheets", "Do you want to upload this export to Google Sheets?")
                if response:
                    GoogleSheetsUpload().create_and_upload_spreadsheet(name_string= '' + name_string + '.csv')
                
                #generate report tooltip
                paycheck_tips = np.round(np.sum(result['paycheck_tips']),2)
                gratuties  = np.round(np.sum(result['custom_earning_gratuity']),2)
                tip_grat_sum = np.round((paycheck_tips + gratuties),2)
                total_exp_hours = np.round(np.sum(result['regular_hours']),2)
                total_exp_overtime = np.round(np.sum(result['overtime_hours']),2)
                total_hr_overtim_exp_sum = np.round((total_exp_hours + total_exp_overtime),2)
                showinfo('Note', ("Exported\nPlease verify the export dates below\n\nFirst day: " + datetime.strptime(self.day_one, "%Y%m%d").strftime("%b %d, %y") + "\nLast day: " + datetime.strptime(self.day_two, "%Y%m%d").strftime("%b %d, %y") + "\n\nTips Paid Out: $" + str(paycheck_tips) + "\nGratuities Paid Out: $" + str(gratuties) + "\nTotal: $" + str(tip_grat_sum) + "\n\nHours: " + str(total_exp_hours) + "\nOvertime: " + str(total_exp_overtime) + "\nTotal: " + str(total_hr_overtim_exp_sum) + "\n\nThe file has been uploaded to Google Drive *or* Check the exports folder for the CSV"))

    def export_csv(self):
            print('PROCESSING: ' + ' ' + self.day_one + ' ' + self.day_two + ' ' + self.rpt_type)
            result = ReportWriter(self.day_one, self.day_two).print_to_json(
                self.rpt_type, selected_employees=self.select_emps, selected_jobs=self.select_jobs, json_fmt=True)
            print(result)
            if type(result) == 'empty':
                showinfo('Note', "There is no data to display for this selection\n(This is not an error)")
                return '' #exit the program if no data to display
            name_string = self.rpt_type + '-' + self.day_one + '-through-' + self.day_two
            result.to_csv(("exports/" + name_string + '.csv'))
        
            showinfo('Note', ("Exported\n\n\nFirst day: " + datetime.strptime(self.day_one, "%Y%m%d").strftime("%b %d, %y") + "\nLast day: " + datetime.strptime(self.day_two, "%Y%m%d").strftime("%b %d, %y") + "\n\nCheck the exports folder for the CSV"))

    def tipshare_info_window(self):
        showinfo('Note', """
This data can be modified under <INSTALLDIR>/data/pools.json

This is a list of each tip pool
Which Jobs contribute, and which receive
Based on Jobcode numbers from Aloha

Type-Sales: is contribution on percentage of sales

Type-Tips: Contribution a percentage of tips
                 
Type-Equal: Splitting the tip equally

Percent: how much they contribute
                 """)

    def rpt_help_window(self):
        showinfo('Note', """
--labor_main--
Shows a breakdown of tips, and hours by Job
TTL_TIPS are tips paid out on check
TTL_CONT[RIBUTIONS] are what was paid to tip pool
DECTIPS are declared cash tips
                                  
--labor_total--
Same as "Labor_Main", but only employee totals
                 
--punctuality--
Shows when employees clocked in, and out                                
                 
--tip_rate--
Shows the daily tip payrate, and info
Broken down by tip pool (takeout, servers, etc)
Or as a total if set to True in settings
                 
--labor_rate--
Shows the daily labor paid out, against sales
Based on labor rates set in Aloha
                 
--cout_eod--
Shows each employee that Aloha automatically clocked out (displays in 24hr time)
Any 3am outhours should be fixed
Ex. If \"outhour\" was 3 and \"outmin\" 00, that is 3:00 clockout.
                 
--hourly--
Calculates the hourly rate earned during the selected period
Includes tips in the calculation
                 
--avg_hours_per_week--
Requires 2+ weeks
Shows the average hours an employee worked through the selection   

--adjustments--
Reports any adjustments that were input through the selection   
                 
--tip_rate_graph--
[experimental] Runs the tip_rate and exports it as a graph

--tipshare_detail--
A complex breakdown of tipshare
Columns prefixed with c_ are contribution  
        """)

    def startup_help_window(self):
        showinfo('Note', """
RUN A REPORT:
    1.Select the report dates in the dropdown
       1a.For a single day, enter it in both first and last dates
    2.Select a report type
       2a. Click "Report Help" for details on each report
    3.(Optional) Filter by employee or job
    4.Press "view", or send to printer with "print"
                 
EXPORT PAYROLL:
    Only relies on you setting the Dates
    Ignores any other selections

TO UPDATE HOURS/TIPS:
    For hours, update these in Aloha. Then run a new report
    To adjust tips, click the 'Adjustments' button

The data reported uses Aloha as the source of truth
If Aloha is incorrect, these reports will also be incorrect
(Incorrect clockin/clockout, declared tips, or CC tips, etc.)

        """)

    def main_window(self):
        self.startup_help_window()

        label = Label(self.root, text="\nReport Options")
        label.grid(row=0, column=2, columnspan=2)

        ##DATE PICKERS##

        label = Label(self.root, text="First day")
        label.grid(row=1, column=2)
        start_date_picker = DateEntry(self.root, width=12, background='darkblue', foreground='white', borderwidth=2,
                                    showweeknumbers=False, maxdate=(date.today()-timedelta(days=1)), mindate=(date.today()-timedelta(weeks=162)))
        start_date_picker.grid(row=2, column=2)
        print((date.today()-timedelta(days=365)))

        label = Label(self.root, text="Last day")
        label.grid(row=1, column=3)
        end_date_picker = DateEntry(self.root, width=12, background='darkblue', foreground='white', borderwidth=2,
                                    showweeknumbers=False, maxdate=(date.today()-timedelta(days=1)), mindate=(date.today()-timedelta(weeks=162)))
        end_date_picker.grid(row=2, column=3)
        self.root.grid_rowconfigure(3, weight=1)

        start_date_picker.set_date((date.today()-timedelta(days=7)))
        end_date_picker.set_date((date.today()-timedelta(days=1)))

        def on_date_changed(e):
            # Get the dates from both date pickers
            start_date = start_date_picker.get()
            end_date = end_date_picker.get()
            self.day_one = datetime.strptime(start_date, '%m/%d/%y').strftime('%Y%m%d')
            self.day_two = datetime.strptime(end_date, '%m/%d/%y').strftime('%Y%m%d')
            #print(self.day_one, self.day_two)


        start_date_picker.bind("<<DateEntrySelected>>", on_date_changed)
        end_date_picker.bind("<<DateEntrySelected>>", on_date_changed)

        ##REPORT DROPDOWN##

        dropdown_val = StringVar(self.root)
        dropdown_val.set("labor_main")
        label = Label(self.root, text="Select a report:")
        label2 = Label(self.root, text="**report, employee, and jobcode selections\n do not apply to payroll csv**")
        label2.config(font=("Courier", 10))
        label.grid(row=3, column=2, columnspan=2)
        label2.grid(row=4, column=2, columnspan=2)

        report_combo = Combobox(self.root, values=self.reports, width=16, exportselection=False)
        report_combo.grid(row=5, column=2, columnspan=2)
        report_combo.set("labor_main")

        def on_report_changed(e):
            self.rpt_type = report_combo.get()
            if self.rpt_type == "tip_rate":
                showinfo('Note', "This report ignores any employee & jobcode selections\n\nNumbers are based on tipshare settings")
            if self.rpt_type == "labor_rate":
                showinfo('Note', "Select the jobcodes you want for the calculation\n\nIgnores any employee selections\n\nLabor Cost is based on pay rate in Aloha")
            if self.rpt_type == "hourly":
                showinfo('Note', "If a job is selected, it will only show the hourly for that job\n\nIncludes Tips")
            if self.rpt_type == "avg_hours_per_week":
                showinfo('Note',"Requires 2+ weeks selection\n\nThis report ignores employee and jobcode selections")

        report_combo.bind("<<ComboboxSelected>>", on_report_changed)   

        ##EMPLOYEE LISTBOX##

        self.root.grid_rowconfigure(5, weight=1)
        label = Label(self.root, text="Select an employee:\n(to select all, leave blank)")
        label.grid(row=6, column=2)

        employee_listbox = Listbox(self.root, height=10, listvariable=StringVar(self.root, value=self.employee_df["NAME"].to_list()), selectmode='multiple', exportselection=False)
        employee_listbox.grid(row=7, column=2, padx=1, pady=2)

        # Set the callback function
        def on_employee_changed(e):
            self.select_emps = [self.employee_df.index[i]
                        for i in employee_listbox.curselection()]
            
        employee_listbox.bind("<<ListboxSelect>>", on_employee_changed)

        ##JOBCODE LISTBOX##

        label = Label(self.root, text="Select a job code:\n(to select all, leave blank)")
        label.grid(row=6, column=3)

        jobcode_listbox = Listbox(
            self.root, height=10, listvariable=StringVar(self.root, value=self.jobcode_df["SHORTNAME"].to_list()), selectmode='multiple', exportselection=False)
        jobcode_listbox.grid(row=7, column=3, padx=1, pady=2)

        # Set the callback function
        def on_jobcode_changed(e):
            self.select_jobs = [self.jobcode_df.index[i]
                        for i in jobcode_listbox.curselection()]
     
        jobcode_listbox.bind("<<ListboxSelect>>", on_jobcode_changed)

        ##PROCESS BUTTONS#

        label = Label(self.root, text="\nProcess Reports")
        label.grid(row=8, column=2, columnspan=2)
        

        view_button = Button(self.root, text="View", command=self.view_rpt)
        view_button.grid(row=9, column=2)

        export_button = Button(self.root, text="Print", command=self.export_rpt)
        export_button.grid(row=9, column=3)

        self.root.grid_rowconfigure(10, weight=1)

        report_help = Button(self.root, text="Report Help", command=self.rpt_help_window)
        report_help.grid(row=11, column=3)

        payroll_button = Button(self.root, text="Export Payroll", command=self.gusto_rpt)
        payroll_button.grid(row=11, column=2)

        self.root.grid_rowconfigure(13, weight=1)

        separator = Label(self.root, text="\nOther Options")
        separator.grid(column=1, row=14, columnspan=3, sticky='ns')

        export_csv_button = Button(self.root, text="Debug Export", command=self.export_csv)
        export_csv_button.grid(row=15, column=2)


        def init_adjustment_gui():
            AdjustmentsGui().mainloop()

        add_adjustment_button = Button(self.root, text="Adjustments", command=init_adjustment_gui)
        add_adjustment_button.grid(row=15, column=3, columnspan=2)

        self.root.grid_rowconfigure(16, weight=1)


    def mainloop(self):
        self.root.mainloop()

if __name__ == "__main__":
    ChipGui().mainloop()