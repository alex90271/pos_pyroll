from datetime import date, datetime, timedelta
from tkinter import END, SUNKEN, W, S, Listbox, StringVar, Tk, Label, OptionMenu, Frame, Toplevel
from tkinter.messagebox import askokcancel, askyesno, showerror, showinfo
from tkinter.ttk import Button, Combobox, Frame, Style
import jinja2
import numpy as np
from tkcalendar import DateEntry
import pandas as pd
from process_pools import ProcessPools
from query_db import QueryDB
from report_writer import Payroll, ReportWriter, ReportWriterReports
from chip_config import ChipConfig
from pandastable import Table
import pdfkit
import win32api
import win32print
import os

class ChipGui():

    def __init__(self, icon="", title="Title"):
        #call database
        self.employee_df = QueryDB().process_db('employees').set_index('ID')
        self.jobcode_df = QueryDB().process_db('jobcodes').set_index('ID')
        self.employee_df['NAME'] = self.employee_df['FIRSTNAME'] + ' ' + self.employee_df['LASTNAME']
        self.reports = ReportWriterReports().available_reports()
        self.verbose_debug = ChipConfig().query(
            'SETTINGS', 'verbose_debug', return_type='bool')
        #window setup
        self.root = Tk()
        self.title = title
        self.root.wm_title(title)
        self.root.geometry("460x650")

        #add ttk font
        Style().configure('.', font=('Verdana', 12))
        #tk font
        self.root.option_add("*font", ("Verdana", 12))

        try:
            self.icon = icon
            self.root.iconbitmap(icon)
        except:
            print("error loading icon")

        #selections
        self.day_one = (date.today()-timedelta(days=7)).strftime('%Y%m%d')
        self.day_two = (date.today()-timedelta(days=1)).strftime('%Y%m%d')
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
            return 0 #exit the program if no data to display
        
        df.reset_index(inplace=True)
        if self.verbose_debug:
            df.to_csv('debug/latest_viewed.csv')
        #df.to_dict(orient='index')
        pt = Table(report_frame, dataframe=df, width=1000, height=600,
                showstatusbar=True)
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
                
                #generate report tooltip
                paycheck_tips = np.round(np.sum(result['paycheck_tips']),2)
                gratuties  = np.round(np.sum(result['custom_earning_gratuity']),2)
                tip_grat_sum = np.round((paycheck_tips + gratuties),2)
                total_exp_hours = np.round(np.sum(result['regular_hours']),2)
                total_exp_overtime = np.round(np.sum(result['overtime_hours']),2)
                total_hr_overtim_exp_sum = np.round((total_exp_hours + total_exp_overtime),2)
                showinfo('Note', ("Exported\nPlease verify the export dates below\n\nFirst day: " + datetime.strptime(self.day_one, "%Y%m%d").strftime("%b %d, %y") + "\nLast day: " + datetime.strptime(self.day_two, "%Y%m%d").strftime("%b %d, %y") + "\n\nTips Paid Out: " + str(paycheck_tips) + "\nGratuities Paid Out: " + str(gratuties) + "\nTotal: " + str(tip_grat_sum) + "\n\nHours: " + str(total_exp_hours) + "\nOvertime: " + str(total_exp_overtime) + "\nTotal: " + str(total_hr_overtim_exp_sum) + "\n\nCheck the exports folder for the CSV"))
                
    def mainloop(self):
        self.root.mainloop()

    def tipshare_info_window(self):
        showinfo('Note', """
This data can be modified under /data/pools.json

This is a list of each tip pool
Which Jobs contribute, and which receive
Based on Jobcode numbers from Aloha

Type-Sales: is contribution on percentage of sales

Type-Tips: Contribution a percentage of tips

Percent: how much they contribute
                 
A more helpful window is in the works
                 """)
        pooler = ProcessPools((date.today()-timedelta(days=1)).strftime('%Y%m%d'))
        df = pd.DataFrame(pooler.get_pool_info())

        report_window = Toplevel()
        report_window.iconbitmap(self.icon)
        report_window.wm_title(self.title)
        report_frame = Frame(report_window)
        report_frame.grid()


        df.reset_index(inplace=True)
        #df.to_dict(orient='index')
        pt = Table(report_frame, dataframe=df, width=1000, height=300,
                showstatusbar=False, editable=False)
        pt.show()

    def rpt_help_window(self):
        showinfo('Note', """
1.labor_main
By Jobcode, Shows a breakdown of tips, and hours
TTL_TIP are tips paid out on check
TTL_CONT are tip contributions
DECTIPS are declared cash tips
                                  
2.labor_total,
Same as "Labor_Main", but only employee totals
                                                           
3.labor_weekly,
Requires 2+ weeks
Shows a sum of labor for each week
                 
4.tipshare_detail,
A complex breakdown of tipshare
                 
5.punctuality,
Shows when employees clocked in, and out                 
                 
6.hourly,
Shows employee hourly, including their tips
Includes pay from payrates set in Aloha
                 
7.tip_rate,
Shows the daily tip payrate, and info
Broken down by tip pool (takeout, servers, etc)
                 
8.labor_rate,
Shows the daily labor paid out, against sales
Based on labor rates set in Aloha
                 
9.cout_eod,
Shows each employee that Aloha force clocked out
Any 3am outhours should be fixed                 
outhour, outmin, shows the latest outhour, and min from Aloha
                 
10.labor_avg_hours
Requires 2+ weeks
Shows the average hours an employee worked through the period                
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
                 
CSV EXPORT:
    Only relies on you setting the Dates
    Ignores the report, and employee/job selections

The data reported is only as accurate as data in Aloha 
(For example, incorrect clockins)

If changes are made in Aloha, a new report will show it
        """)

    def main_window(self):
        self.startup_help_window()

        label = Label(self.root, text="\nReport Options")
        label.grid(row=0, column=2, columnspan=2)

        ##DATE PICKERS##

        label = Label(self.root, text="First day")
        label.grid(row=1, column=2)
        start_date_picker = DateEntry(self.root, width=12, background='darkblue', foreground='white', borderwidth=2,
                                    showweeknumbers=False, maxdate=(date.today()-timedelta(days=1)), mindate=(date.today()-timedelta(days=365)))
        start_date_picker.grid(row=2, column=2)

        label = Label(self.root, text="Last day")
        label.grid(row=1, column=3)
        end_date_picker = DateEntry(self.root, width=12, background='darkblue', foreground='white', borderwidth=2,
                                    showweeknumbers=False, maxdate=(date.today()-timedelta(days=1)), mindate=(date.today()-timedelta(days=395)))
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
        label.grid(row=4, column=2, columnspan=2)

        report_combo = Combobox(self.root, values=self.reports, width=16, exportselection=False)
        report_combo.grid(row=5, column=2, columnspan=2)
        report_combo.set("labor_main")

        def on_report_changed(e):
            self.rpt_type = report_combo.get()

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

        payroll_button = Button(self.root, text="Export to CSV", command=self.gusto_rpt)
        payroll_button.grid(row=11, column=2)

        ##HELP BUTTONS##
        self.root.grid_rowconfigure(12, weight=1)
        tipshare_info = Button(self.root, text="Tipshare Config", command=self.tipshare_info_window)
        tipshare_info.grid(row=13, column=2)
        report_help = Button(self.root, text="Report Help", command=self.rpt_help_window)
        report_help.grid(row=13, column=3)

        testing_adjust_button = False
        #set to true to test the "adjustments" feature. Its not working at all
        if testing_adjust_button:
            add_adjustment_button = Button(self.root, text="Adjustments", command=self.adjustments_window)
            add_adjustment_button.grid(row=14, column=3)

        self.root.grid_rowconfigure(15, weight=1)

    def adjustments_window(self):
        # Create the popup box
        adjust_window = Tk()
        adjust_window.geometry("300x400")
        adjust_window.iconbitmap(self.icon)
        adjust_window.wm_title(self.title)
        adjust_frame = Frame(adjust_window)
        adjust_frame.grid()
        today = datetime.today()

        primary_mods = []
        def on_primary_selection_changed(e):
            primary_mods = self.employee_df.index[dropdown_val.get()]
        # Do something when the primary selection is changed

        second_mods = []
        def on_multiple_selection_changed(e):
            second_mods = [self.employee_df.index[i] for i in multiple_selection_listbox.curselection()]

        dl = Label(adjust_frame, text="Date")
        dl.grid()
        # Create a list of dates from the previous 15th or end of month date, to today
        date_list = [today - timedelta(days=x) for x in range(15)]
        date_dropdown = OptionMenu(adjust_frame, "", *date_list)
        date_dropdown.grid()

        psl = Label(adjust_frame, text="Primary Server")
        psl.grid()
        dropdown_val = StringVar(adjust_frame)
        primary_selection_dropdown = OptionMenu(adjust_frame, dropdown_val, *self.employee_df["NAME"].to_list(), command=on_primary_selection_changed)
        primary_selection_dropdown.grid()

        msl = Label(adjust_frame, text="Secondary Servers")
        msl.grid()
        multiple_selection_listbox = Listbox(adjust_frame,listvariable=StringVar(value=self.employee_df["NAME"].to_list()), selectmode="multiple", exportselection=False)
        multiple_selection_listbox.grid()

        # Bind the <<ListboxSelect>> event to the second list box
        multiple_selection_listbox.bind("<<ListboxSelect>>", on_multiple_selection_changed)


if __name__ == "__main__":
    ChipGui().mainloop()

