from datetime import date, datetime, timedelta
import tkinter as tk
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

employee_df = QueryDB().process_db('employees').set_index('ID')
jobcode_df = QueryDB().process_db('jobcodes').set_index('ID')
employee_df['NAME'] = employee_df['FIRSTNAME'] + ' ' + employee_df['LASTNAME']

print(jobcode_df['SHORTNAME'], employee_df['NAME'])
reports = ReportWriterReports().available_reports()

if __name__ == '__main__':
    # Create a window
    root = tk.Tk()
    root.geometry("800x800")
    root.iconbitmap("pyroll_ico.ico")
    root.wm_title("Payroll and Tipshare report tool")

    day_one = (date.today()-timedelta(days=1)).strftime('%Y%m%d')
    day_two = (date.today()-timedelta(days=1)).strftime('%Y%m%d')
    rpt_type = 'labor_main'
    select_jobs = []
    select_emps = []

    c_frame = tk.Frame(root)
    c_frame.pack(pady=5)

    l_frame = tk.Frame(c_frame, width=250)
    l_frame.pack(side='left', padx=10)

    t_frame = tk.Frame(l_frame)
    t_frame.pack(side='top', pady=10)

    r_frame = tk.Frame(c_frame, width=1200)
    r_frame.pack(side='right', padx=10)

    strt_label = tk.Label(r_frame, text="""
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
    strt_label.pack()

    b_frame = tk.Frame(t_frame)
    b_frame.pack(side='bottom', pady=10)

    b_l_frame = tk.Frame(b_frame)
    b_l_frame.pack(side='left', pady=10)

    b_r_frame = tk.Frame(b_frame)
    b_r_frame.pack(side='left', pady=10)

    # Create a label
    label = tk.Label(
        l_frame, text="Select report days\n(for one day, select it in both)")
    label.pack(padx=10, pady=5)

    info_label = tk.Label(t_frame, text="No Report Selected")
    info_label.pack()

    # Create two date pickers
    start_date_picker = DateEntry(l_frame, width=12, background='darkblue', foreground='white', borderwidth=2,
                                  showweeknumbers=False, maxdate=(date.today()-timedelta(days=1)), mindate=(date.today()-timedelta(days=395)))
    start_date_picker.pack(pady=5)

    end_date_picker = DateEntry(l_frame, width=12, background='darkblue', foreground='white', borderwidth=2,
                                showweeknumbers=False, maxdate=(date.today()-timedelta(days=1)), mindate=(date.today()-timedelta(days=395)))
    end_date_picker.pack(pady=5)

    # Bind a callback function to both date pickers

    def on_date_changed(date):
        # Get the dates from both date pickers
        start_date = start_date_picker.get()
        end_date = end_date_picker.get()
        global day_one, day_two
        day_one = datetime.strptime(start_date, '%m/%d/%y').strftime('%Y%m%d')
        day_two = datetime.strptime(end_date, '%m/%d/%y').strftime('%Y%m%d')

    start_date_picker.bind("<<DateEntrySelected>>", on_date_changed)
    end_date_picker.bind("<<DateEntrySelected>>", on_date_changed)

    dropdown_val = tk.StringVar(root)
    dropdown_val.set("labor_main")
    label = tk.Label(l_frame, text="Select a report:")
    label.pack(pady=5)

    def on_report_changed(report):
        global rpt_type
        rpt_type = dropdown_val.get()

    report_dropdown = tk.OptionMenu(
        l_frame, dropdown_val, *reports, command=on_report_changed)
    report_dropdown.pack(pady=5)

    # Create a label
    label = tk.Label(l_frame, text="OPTIONAL\nSelect an employee:")
    label.pack(pady=5)

    # Create a list box
    employee_listbox = tk.Listbox(
        l_frame, listvariable=tk.StringVar(l_frame, value=employee_df["NAME"].to_list()), selectmode='multiple')
    employee_listbox.pack()

    # Set the callback function
    def on_employee_changed(event):
        global select_emps
        select_emps = [employee_df.index[i]
                       for i in employee_listbox.curselection()]

    employee_listbox.bind("<<ListboxSelect>>", on_employee_changed)

    # Create a label
    label = tk.Label(l_frame, text="OPTIONAL\nSelect a job code:")
    label.pack(pady=5)

    # Create a list box
    jobcode_listbox = tk.Listbox(
        l_frame, listvariable=tk.StringVar(l_frame, value=jobcode_df["SHORTNAME"].to_list()), selectmode='multiple')
    jobcode_listbox.pack()

    # Set the callback function
    def on_jobcode_changed(event):
        global select_jobs
        select_jobs = [jobcode_df.index[i]
                       for i in jobcode_listbox.curselection()]

    jobcode_listbox.bind("<<ListboxSelect>>", on_jobcode_changed)

    def export_rpt():
        print('PROCESSING: ' + ' ' + day_one + ' ' + day_two + ' ' + rpt_type)
        if strt_label:
            strt_label.destroy()
        if r_frame.winfo_children():
            for widget in r_frame.winfo_children():
                widget.pack_forget()
        df = ReportWriter(day_one, day_two).print_to_json(
            rpt_type, selected_employees=select_emps, selected_jobs=select_jobs, json_fmt=True)
        if type(df) == 'empty':
            info_label.config(text="No rows to export")
        result = df.fillna('')
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(searchpath="templates/"))
        template = env.get_template('render.html').render(
            tables=[result.to_html(
                table_id="table", classes="ui striped table")],
            titles=result.columns.values,
            timestamp=datetime.now().strftime('%b %d %Y (%I:%M:%S%p %Z)'),
            dates=[
                datetime.strptime(day_one, "%Y%m%d").strftime(
                    '%a, %b %d, %Y'),
                datetime.strptime(day_two, "%Y%m%d").strftime(
                    '%a, %b %d, %Y')
            ],
            rpttp=rpt_type,
            select_emps=select_emps, select_jobs=select_jobs)
        export_dir = "/exports/"
        name_string = rpt_type + '-' + day_one[-6:] + '-' + day_two[-6:]
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
            info_label.config(text=(datetime.now().strftime(
                "%H:%M:%S") + "\nThe report has been printed\nCheck Printer: " + printer_name))
        except:
            print('there was a printer error; file was only exported')
            info_label.config(text=(datetime.now().strftime(
                "%H:%M:%S") + "\nThere was a printer error\nCheck the exports folder for the report"))
        for widget in r_frame.winfo_children():
            widget.destroy()

    def gusto_rpt():
        print('PROCESSING: ' + ' ' + day_one + ' ' + day_two + ' ' + rpt_type)
        strt_label.destroy()
        for widget in r_frame.winfo_children():
            widget.destroy()
        '''exports payroll to gusto'''
        if (pd.date_range(day_one, periods=1, freq='SM').strftime("%Y%m%d")[0] == day_two):
            result = Payroll(day_one, day_two).process_payroll()
            if type(result) == 'empty':
                info_label.config(text="No data to export")
            name_string = ChipConfig().query("SETTINGS", "company_name") + \
                '-payroll_export-' + 'F' + day_one + '-' + 'L' + day_two
            result.to_csv(
                ("exports/" + name_string + '.csv'),
                index=False)
            info_label.config(text=(datetime.now().strftime(
                "%H:%M:%S") + "\nCheck the exports folder for the payroll CSV"))
        else:
            info_label.config(
                text="There was an error\nYou must select a payroll interval to export payroll\nEx. 1st-15th or 16th-31st")

    def view_rpt():
        print('PROCESSING: ' + ' ' + day_one + ' ' + day_two + ' ' + rpt_type)
        strt_label.destroy()
        for widget in r_frame.winfo_children():
            widget.destroy()
        df = ReportWriter(day_one, day_two).print_to_json(
            rpt_type, selected_employees=select_emps, selected_jobs=select_jobs, json_fmt=True)
        if type(df) == 'empty':
            info_label.config(text="No data to display")
        df.reset_index(inplace=True)
        df.to_dict(orient='index')
        pt = Table(r_frame, dataframe=df, width=1000, height=600,
                   showstatusbar=True, editable=False)
        pt.show()
        info_label.config(
            text=(datetime.now().strftime("%H:%M:%S") + "\ndisplaying"))

    view_button = tk.Button(b_l_frame, text="View", command=view_rpt)
    view_button.pack(padx=5)

    export_button = tk.Button(b_l_frame, text="Print", command=export_rpt)
    export_button.pack(padx=5)

    payroll_button = tk.Button(
        b_r_frame, text="Process\nPayroll CSV", command=gusto_rpt)
    payroll_button.pack(padx=5)

    # Show the window
    root.mainloop()