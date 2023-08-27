from datetime import date, datetime, timedelta
import time
import tkinter as tk
from tkinter import ttk
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
        self.info_label = tk.Label(self.root, text="No Report Selected")
        self.info_label.pack()
        self.icon = icon 
        self.title = title
        self.root.iconbitmap(icon)
        self.root.wm_title(title)
        self.root.geometry("800x800")

        #selections
        self.day_one = (date.today()-timedelta(days=7)).strftime('%Y%m%d')
        self.day_two = (date.today()-timedelta(days=1)).strftime('%Y%m%d')
        self.rpt_type = "labor_main"
        self.select_emps = []
        self.select_jobs = []

        #frames
        #left
        self.l_frame = tk.Frame(self.root, width=250)
        self.l_frame.pack(side='left', padx=5, pady=2.5) 
        #right
        self.r_frame = tk.Frame(self.root)
        self.r_frame.pack(side='right', padx=5)
        #top
        self.t_frame = tk.Frame(self.l_frame)
        self.t_frame.pack(side='top', pady=2.5)
        #bottom
        self.b_frame = tk.Frame(self.l_frame)
        self.b_frame.pack(side='bottom', pady=2.5)

        self.strt_label = tk.Label(self.r_frame, text="""
                To get Started:
                Select the report dates in the dropdown
                (for a single day, enter it twice)
                
                Then select the desired report from the dropdown (default: labor_main)

                General Notes:
                            It is important to verify totals against Aloha (total tips paid out should equal total tips on aloha)
                            The data reported here is only as accurate as Aloha (ex. incorrect clockins)
                            Some reports can be filtered by Jobcode or Employee (payroll export file is never filtered)

                Report Info:
                    Cout_eod
                            This report lists any clockins that were force closed by the end of day (3am)
                    Labor Rate
                            Labor rate report pulls from pay rates set in Aloha
                    Hourly
                            Hourly shows the actual hourly rate someone made, tips and all (uses pay rates set in aloha)
                    Labor Average Hours
                            requires 2+ weeks; Labor Average shows the average hours and employee worked during the selected period
                    Labor Reports:
                            Shows a breakdown of tips, and hours
                            TTL_TIP are tips paid out on check
                            TTL_CONT are tip contributions (4% of sales for servers)
                            DECTIPS are declared cash tips
        """, justify="left")

    def kill_launch_window(self, window):
        while self.root.state() != 'normal':
                time.sleep(1)
                print('loading')
        window.destroy()

    def adjustments_window(self):
        # Create the popup box
        popup_window = tk.Toplevel()
        popup_window.geometry("300x400")
        popup_window.iconbitmap(self.icon)
        popup_window.wm_title(self.title)
        today = datetime.today()

        dl = tk.Label(popup_window, text="Date")
        dl.pack(pady=3.5)

        # Create a list of dates from the previous 15th or end of month date, to today
        date_list = [today - timedelta(days=x) for x in range(15)]


        date_dropdown = tk.OptionMenu(popup_window, "", *date_list)
        date_dropdown.pack()

        psl = tk.Label(popup_window, text="Primary Server")
        psl.pack(pady=3.5)
        primary_selection_listbox = tk.Listbox(popup_window,listvariable=tk.StringVar(value=self.employee_df["NAME"].to_list()), selectmode="single", exportselection=False)
        primary_selection_listbox.pack()

        msl = tk.Label(popup_window, text="Secondary Servers")
        msl.pack(pady=3.5)
        multiple_selection_listbox = tk.Listbox(popup_window,listvariable=tk.StringVar(value=self.employee_df["NAME"].to_list()), selectmode="multiple", exportselection=False)
        multiple_selection_listbox.pack()

        primary_mods = []
        def on_primary_selection_changed(e):
            primary_mods = self.employee_df.index[primary_selection_listbox.curselection()[0]]
        # Do something when the primary selection is changed

        second_mods = []
        def on_multiple_selection_changed(e):
            second_mods = [self.employee_df.index[i] for i in multiple_selection_listbox.curselection()]
        
        # Bind the <<ListboxSelect>> event to the first list box
        primary_selection_listbox.bind("<<ListboxSelect>>", on_primary_selection_changed)

        # Bind the <<ListboxSelect>> event to the second list box
        multiple_selection_listbox.bind("<<ListboxSelect>>", on_multiple_selection_changed)

    def view_rpt(self):
        popup_window = tk.Toplevel()
        popup_window.geometry("800x800")
        popup_window.iconbitmap(self.icon)
        popup_window.wm_title(self.title)
        print('PROCESSING: ' + ' ' + self.day_one + ' ' + self.day_two + ' ' + self.rpt_type)
        df = ReportWriter(self.day_one, self.day_two).print_to_json(
            self.rpt_type, selected_employees=self.select_emps, selected_jobs=self.select_jobs, json_fmt=True)
        if type(df) == 'empty':
            self.info_label.config(text="No data to display")
            return '' #exit the program if no data to display
        df.reset_index(inplace=True)
        #df.to_dict(orient='index')
        pt = Table(self.r_frame, dataframe=df, width=1000, height=600,
                showstatusbar=True, editable=True)
        pt.show()
        self.info_label.config(
            text=(datetime.now().strftime("%H:%M:%S") + "\ndisplaying"))
        
    def export_rpt(self):
            print('PROCESSING: ' + ' ' + self.day_one + ' ' + self.day_two + ' ' + self.rpt_type)
            df = ReportWriter(self.day_one, self.day_two).print_to_json(
                self.rpt_type, selected_employees=self.select_emps, selected_jobs=self.select_jobs, json_fmt=True)
            if type(df) == 'empty':
                self.info_label.config(text="No rows to export")
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
                self.info_label.config(text=(datetime.now().strftime(
                    "%H:%M:%S") + "\nThe report has been printed\nCheck Printer: " + printer_name))
            except:
                print('there was a printer error; file was only exported')
                self.info_label.config(text=(datetime.now().strftime(
                    "%H:%M:%S") + "\nThere was a printer error\nCheck the exports folder for the report"))
            for widget in self.r_frame.winfo_children():
                widget.destroy()

    def gusto_rpt(self):
            print('PROCESSING: ' + ' ' + self.day_one + ' ' + self.day_two + ' ' + self.rpt_type)
            '''exports payroll to gusto'''
            if (pd.date_range(self.day_one, periods=1, freq='SM').strftime("%Y%m%d")[0] == self.day_two):
                result = Payroll(self.day_one, self.day_two).process_payroll()
                if type(result) == 'empty':
                    self.info_label.config(text="No data to export")
                name_string = ChipConfig().query("SETTINGS", "company_name") + \
                    '-payroll_export-' + 'F' + self.day_one + '-' + 'L' + self.day_two
                result.to_csv(
                    ("exports/" + name_string + '.csv'),
                    index=False)
                self.info_label.config(text=(datetime.now().strftime(
                    "%H:%M:%S") + "\nCheck the exports folder for the payroll CSV"))
            else:
                self.info_label.config(
                    text="There was an error\nYou must select a payroll interval to export payroll\nEx. 1st-15th or 16th-31st")


    def main_window(self):
        self.day_one = (date.today()-timedelta(days=7)).strftime('%Y%m%d')
        self.day_two = (date.today()-timedelta(days=1)).strftime('%Y%m%d')
        rpt_type = 'labor_main'
        self.select_jobs = []
        self.select_emps = []

        self.strt_label.pack()

        # Create a label
        label = tk.Label(
            self.l_frame, text="Select a date range\n(for one day, select twice)")
        label.pack(padx=10, pady=3.5) 
        # Create two date pickers
        start_date_picker = DateEntry(self.l_frame, width=12, background='darkblue', foreground='white', borderwidth=2,
                                    showweeknumbers=False, maxdate=(date.today()-timedelta(days=1)), mindate=(date.today()-timedelta(days=395)))
        start_date_picker.pack(pady=3.5)

        end_date_picker = DateEntry(self.l_frame, width=12, background='darkblue', foreground='white', borderwidth=2,
                                    showweeknumbers=False, maxdate=(date.today()-timedelta(days=1)), mindate=(date.today()-timedelta(days=395)))
        end_date_picker.pack(pady=3.5)

        def on_date_changed(e):
            # Get the dates from both date pickers
            start_date = start_date_picker.get()
            end_date = end_date_picker.get()
            self.day_one = datetime.strptime(start_date, '%m/%d/%y').strftime('%Y%m%d')
            self.day_two = datetime.strptime(end_date, '%m/%d/%y').strftime('%Y%m%d')
            print(self.day_one, self.day_two)

        start_date_picker.bind("<<DateEntrySelected>>", on_date_changed)
        end_date_picker.bind("<<DateEntrySelected>>", on_date_changed)

        dropdown_val = tk.StringVar(self.root)
        dropdown_val.set("labor_main")
        label = tk.Label(self.l_frame, text="Select a report:")
        label.pack(pady=3.5)

        def on_report_changed(e):
            self.rpt_type = dropdown_val.get()
        report_dropdown = tk.OptionMenu(
        self.l_frame, dropdown_val, *self.reports, command=on_report_changed)
        report_dropdown.pack(pady=3.5)

        label = tk.Label(self.l_frame, text="Select an employee:\n(to select all, leave blank)")
        label.pack(pady=3.5)

        # Create a list box
        employee_listbox = tk.Listbox(
            self.l_frame, listvariable=tk.StringVar(self.l_frame, value=self.employee_df["NAME"].to_list()), selectmode='multiple', exportselection=False)
        employee_listbox.pack()

        # Set the callback function
        def on_employee_changed(e):
            self.select_emps = [self.employee_df.index[i]
                        for i in employee_listbox.curselection()]

        employee_listbox.bind("<<ListboxSelect>>", on_employee_changed)

        label = tk.Label(self.l_frame, text="Select a job code:\n(to select all, leave blank)")
        label.pack(pady=3.5)

        # Create a list box
        jobcode_listbox = tk.Listbox(
            self.l_frame, listvariable=tk.StringVar(self.l_frame, value=self.jobcode_df["SHORTNAME"].to_list()), selectmode='multiple', exportselection=False)
        jobcode_listbox.pack()

        # Set the callback function
        def on_jobcode_changed(e):
            self.select_jobs = [self.jobcode_df.index[i]
                        for i in jobcode_listbox.curselection()]

        jobcode_listbox.bind("<<ListboxSelect>>", on_jobcode_changed)

        view_button = tk.Button(self.b_frame, text="View", command=self.view_rpt, padx=15)
        view_button.pack(padx=1,pady=2)

        export_button = tk.Button(self.b_frame, text="Print", command=self.export_rpt, padx=15)
        export_button.pack(padx=1,pady=2)

        label = tk.Label(self.l_frame, text="")
        label.pack()

        payroll_button = tk.Button(
            self.b_frame, text="Payroll CSV Export", command=self.gusto_rpt, padx=15)
        payroll_button.pack(padx=1,pady=2)

        # Create a button that will open the popup box
        add_adjustment_button = tk.Button(self.b_frame, text="Adjustments", command=self.adjustments_window, padx=15)
        add_adjustment_button.pack(padx=1,pady=2)


if __name__ == "__main__":
    print("this is a helper file, run chip_payroll")
