from datetime import date, datetime, timedelta
import time
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo
import jinja2
from tkcalendar import DateEntry
import pandas as pd
from query_db import QueryDB
from report_writer import Payroll, ReportWriter, ReportWriterReports
from chip_config import ChipConfig
from pandastable import Table
import pdfkit
import win32api
import win32print
import os

class MainGui():

    def __init__(self, icon="assets\pyroll_ico.ico", title="Payroll and Tipshare report tool"):

        #call database
        self.employee_df = QueryDB().process_db('employees').set_index('ID')
        self.jobcode_df = QueryDB().process_db('jobcodes').set_index('ID')
        self.employee_df['NAME'] = self.employee_df['FIRSTNAME'] + ' ' + self.employee_df['LASTNAME']
        self.reports = ReportWriterReports().available_reports()
        self.icon = icon
        self.title = title

        #window setup
        self.root = tk.Tk()
        self.icon = icon 
        self.title = title
        self.root.iconbitmap(icon)
        self.root.wm_title(title)
        self.root.geometry("800x500")

        #selections
        self.day_one = (date.today()-timedelta(days=7)).strftime('%Y%m%d')
        self.day_two = (date.today()-timedelta(days=1)).strftime('%Y%m%d')
        self.rpt_type = "labor_main"
        self.select_emps = []
        self.select_jobs = []

        self.info_label = tk.Label(self.root, text="""
                To Run a Report:
                Select the report dates in the dropdown
                (for a single day, enter it twice)
                                   
                Important Notes:
                It is important to verify totals against Aloha 
                    Total tips paid out should equal total tips reported on Aloha
                The data reported here is only as accurate as Aloha 
                    Ex. incorrect clockins
                                   
                Click "Report Help" for details on what each report does
        """, justify="left")
        self.info_label.grid(row=1,column=4, rowspan=8)

    def rpt_help_window(self):
        showinfo('Note', """
            1.Cout_eod:
            This report lists any clockins that were force closed by the end of day (3am)

            2.Labor Rate:
            Labor rate report pulls from pay rates set in Aloha
                 
            3.Hourly:
            Hourly shows the actual hourly rate someone made, tips and all (uses pay rates set in aloha)

            4.Labor Average Hours:
            Requires 2+ weeks; Labor Average shows the average hours and employee worked during the selected period
                 
            5.Labor Reports:
            Shows a breakdown of tips, and hours
            TTL_TIP are tips paid out on check
            TTL_CONT are tip contributions
            DECTIPS are declared cash tips
        """)

    def main_window(self):
        self.day_one = (date.today()-timedelta(days=7)).strftime('%Y%m%d')
        self.day_two = (date.today()-timedelta(days=1)).strftime('%Y%m%d')
        self.select_jobs = []
        self.select_emps = []

        label = tk.Label(self.root, text="")
        label.grid(row=0, column=1, padx=2, pady=2)

        label = tk.Label(self.root, text="\nReport Options")
        label.grid(row=0, column=2, padx=2, pady=2, columnspan=2)

        # Create two date pickers
        label = tk.Label(self.root, text="First day")
        label.grid(row=1, column=2, padx=2, pady=2)
        start_date_picker = DateEntry(self.root, width=12, background='darkblue', foreground='white', borderwidth=2,
                                    showweeknumbers=False, maxdate=(date.today()-timedelta(days=1)), mindate=(date.today()-timedelta(days=395)))
        start_date_picker.grid(row=2, column=2, padx=2, pady=2)
        label = tk.Label(self.root, text="Second day")
        label.grid(row=1, column=3)
        end_date_picker = DateEntry(self.root, width=12, background='darkblue', foreground='white', borderwidth=2,
                                    showweeknumbers=False, maxdate=(date.today()-timedelta(days=1)), mindate=(date.today()-timedelta(days=395)))
        end_date_picker.grid(row=2, column=3, padx=2, pady=2)

        def on_date_changed(e):
            # Get the dates from both date pickers
            start_date = start_date_picker.get()
            end_date = end_date_picker.get()
            self.day_one = datetime.strptime(start_date, '%m/%d/%y').strftime('%Y%m%d')
            self.day_two = datetime.strptime(end_date, '%m/%d/%y').strftime('%Y%m%d')
            print(self.day_one, self.day_two)

        start_date_picker.bind("<<DateEntrySelected>>", on_date_changed)
        end_date_picker.bind("<<DateEntrySelected>>", on_date_changed)

        label = tk.Label(self.root, text="Select an employee:\n(to select all, leave blank)")
        label.grid(row=5, column=2, padx=2, pady=2)

        dropdown_val = tk.StringVar(self.root)
        dropdown_val.set("labor_main")
        label = tk.Label(self.root, text="Select a report:")
        label.grid(row=3, column=2, padx=2, pady=2, columnspan=2)

        def on_report_changed(e):
            self.rpt_type = dropdown_val.get()
        report_dropdown = tk.OptionMenu(self.root, dropdown_val, *self.reports, command=on_report_changed)
        report_dropdown.grid(row=4, column=2, padx=2, pady=2)

        report_help = tk.Button(self.root, text="Report Help", command=self.rpt_help_window)
        report_help.grid(row=4, column=3, padx=2, pady=2)

        # Create a list box
        employee_listbox = tk.Listbox(
            self.root, listvariable=tk.StringVar(self.root, value=self.employee_df["NAME"].to_list()), selectmode='multiple', exportselection=False)
        employee_listbox.grid(row=6, column=2, padx=2, pady=2)

        # Set the callback function
        def on_employee_changed(e):
            self.select_emps = [self.employee_df.index[i]
                        for i in employee_listbox.curselection()]

        employee_listbox.bind("<<ListboxSelect>>", on_employee_changed)
        label = tk.Label(self.root, text="Select a job code:\n(to select all, leave blank)")
        label.grid(row=5, column=3, padx=2, pady=2)

        # Create a list box
        jobcode_listbox = tk.Listbox(
            self.root, listvariable=tk.StringVar(self.root, value=self.jobcode_df["SHORTNAME"].to_list()), selectmode='multiple', exportselection=False)
        jobcode_listbox.grid(row=6, column=3, padx=2, pady=2)
        # Set the callback function
        def on_jobcode_changed(e):
            self.select_jobs = [self.jobcode_df.index[i]
                        for i in jobcode_listbox.curselection()]

        jobcode_listbox.bind("<<ListboxSelect>>", on_jobcode_changed)

        label = tk.Label(self.root, text="\nProcess Reports")
        label.grid(row=7, column=2, padx=2, pady=2, columnspan=2)

        view_button = tk.Button(self.root, text="View", command=self.view_rpt, padx=15)
        view_button.grid(row=8, column=2, padx=2, pady=2)

        export_button = tk.Button(self.root, text="Print", command=self.export_rpt, padx=15)
        export_button.grid(row=8, column=3, padx=2, pady=2)

        label = tk.Label(self.root, text="")
        label.grid(row=9, column=2)

        payroll_button = tk.Button(
            self.root, text="Payroll CSV Export", command=self.gusto_rpt, padx=15)
        payroll_button.grid(row=10, column=2, padx=2, pady=2, columnspan=2)

        # Create a button that will open the popup box
        testing_adjust_button = False
        if testing_adjust_button:
            add_adjustment_button = tk.Button(self.root, text="Adjustments", command=self.adjustments_window, padx=15)
            add_adjustment_button.grid(row=11, column=3, padx=2, pady=2)

    def view_rpt(self):
        report_window = tk.Tk()
        #report_window.geometry("800x800")
        report_window.iconbitmap(self.icon)
        report_window.wm_title(self.title)
        report_frame = tk.Frame(report_window)
        report_frame.grid()
        print('PROCESSING: ' + ' ' + self.day_one + ' ' + self.day_two + ' ' + self.rpt_type)
        df = ReportWriter(self.day_one, self.day_two).print_to_json(
            self.rpt_type, selected_employees=self.select_emps, selected_jobs=self.select_jobs, json_fmt=True)
        if type(df) == 'empty':
            showinfo('Note', "There is no data to display for this selection\n(This is not an error)")
            return '' #exit the program if no data to display
        df.reset_index(inplace=True)
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
                showinfo('Note', "There was a printer error\nCheck the exports folder for a PDF\n\nNote: Adobe Acrobat Reader should be installed")

    def gusto_rpt(self):
            print('PROCESSING: ' + ' ' + self.day_one + ' ' + self.day_two + ' ' + self.rpt_type)
            '''exports payroll to gusto'''
            if (pd.date_range(self.day_one, periods=1, freq='SM').strftime("%Y%m%d")[0] == self.day_two):
                result = Payroll(self.day_one, self.day_two).process_payroll()
                if type(result) == 'empty':
                    showinfo('Note', "There is no data to export for this selection\n(This is not an error)")
                    return '' #exit the program if no data to export
                name_string = ChipConfig().query("SETTINGS", "company_name") + \
                    '-payroll_export-' + 'F' + self.day_one + '-' + 'L' + self.day_two
                result.to_csv(
                    ("exports/" + name_string + '.csv'),
                    index=False)
                showinfo('Note', ("Check the exports folder for the payroll CSV"))
            else:
                showinfo('Note', ("There was an error\nYou must select a payroll interval to export payroll\nEx. 1st-15th or 16th-31st"))


    def kill_launch_window(self, window):
        while self.root.state() != 'normal':
                time.sleep(1)
                print('loading')
        window.destroy()

    def adjustments_window(self):
        # Create the popup box
        adjust_window = tk.Tk()
        adjust_window.geometry("300x400")
        adjust_window.iconbitmap(self.icon)
        adjust_window.wm_title(self.title)
        adjust_frame = tk.Frame(adjust_window)
        adjust_frame.grid()
        today = datetime.today()

        primary_mods = []
        def on_primary_selection_changed(e):
            primary_mods = self.employee_df.index[dropdown_val.get()]
        # Do something when the primary selection is changed

        second_mods = []
        def on_multiple_selection_changed(e):
            second_mods = [self.employee_df.index[i] for i in multiple_selection_listbox.curselection()]

        dl = tk.Label(adjust_frame, text="Date")
        dl.grid()
        # Create a list of dates from the previous 15th or end of month date, to today
        date_list = [today - timedelta(days=x) for x in range(15)]
        date_dropdown = tk.OptionMenu(adjust_frame, "", *date_list)
        date_dropdown.grid(padx=2, pady=2)

        psl = tk.Label(adjust_frame, text="Primary Server")
        psl.grid()
        dropdown_val = tk.StringVar(adjust_frame)
        primary_selection_dropdown = tk.OptionMenu(adjust_frame, dropdown_val, *self.employee_df["NAME"].to_list(), command=on_primary_selection_changed)
        primary_selection_dropdown.grid(padx=2, pady=2)

        msl = tk.Label(adjust_frame, text="Secondary Servers")
        msl.grid()
        multiple_selection_listbox = tk.Listbox(adjust_frame,listvariable=tk.StringVar(value=self.employee_df["NAME"].to_list()), selectmode="multiple", exportselection=False)
        multiple_selection_listbox.grid(padx=2, pady=2)

        # Bind the <<ListboxSelect>> event to the second list box
        multiple_selection_listbox.bind("<<ListboxSelect>>", on_multiple_selection_changed)


if __name__ == "__main__":
    print("this is a helper file, run chip_payroll")
