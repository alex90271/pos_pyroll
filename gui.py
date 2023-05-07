from datetime import date, datetime, timedelta
import tkinter as tk
from tkcalendar import DateEntry
from flask import app, jsonify, render_template
import pandas as pd
from query_db import QueryDB
from report_writer import Payroll, ReportWriter, ReportWriterReports
from chip_config import ChipConfig
from pandastable import Table

employee_df = QueryDB().process_db('employees')
jobcode_df = QueryDB().process_db('jobcodes')
employee_df['NAME'] = employee_df['FIRSTNAME'] + ' ' + employee_df['LASTNAME']

jobcode_list = jobcode_df['SHORTNAME'].to_list()
employee_list = employee_df['NAME'].to_list()
reports = ReportWriterReports().available_reports()

if __name__ == '__main__':
    # Create a window
    root = tk.Tk()
    root.geometry("1600x800")

    day_one = (date.today()-timedelta(days=1)).strftime('%Y%m%d')
    day_two = (date.today()-timedelta(days=1)).strftime('%Y%m%d')
    rpt_type = 'labor_main'
    select_jobs = []
    select_emps = []

    l_frame = tk.Frame(root, width=250, height=800)
    l_frame.pack(side='left', padx=50, pady=5)

    r_frame = tk.Frame(root, width=1200, height=800)
    r_frame.pack(side='right', padx=50, pady=5)

    b_frame = tk.Frame(l_frame, width=250, height=800)
    b_frame.pack(side='bottom', pady=20)

    # Create a label
    label = tk.Label(l_frame, text="Select report days\n(for one day, enter in both)")
    label.pack(padx=10, pady=5)

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
    dropdown_val.set("Select an Option")
    label = tk.Label(l_frame, text="Select a report:")
    label.pack(pady=5)

    def on_report_changed(report):
        global rpt_type
        rpt_type = dropdown_val.get()

    report_dropdown = tk.OptionMenu(
        l_frame, dropdown_val, *reports, command=on_report_changed)
    report_dropdown.pack(pady=5)

    # Create a label
    label = tk.Label(l_frame, text="Select an employee:")
    label.pack(pady=5)

    # Create a list box
    employee_listbox = tk.Listbox(
        l_frame, listvariable=tk.StringVar(l_frame, value=employee_list), selectmode='multiple')
    employee_listbox.pack()

    # Set the callback function
    def on_employee_changed(event):
        global select_emps
        select_emps = [employee_listbox.get(i) for i in employee_listbox.curselection()]
        print(select_emps)

    employee_listbox.bind("<<ListboxSelect>>", on_employee_changed)

    # Create a label
    label = tk.Label(l_frame, text="Select a job code:")
    label.pack(pady=5)

    # Create a list box
    jobcode_listbox = tk.Listbox(
        l_frame, listvariable=tk.StringVar(l_frame, value=jobcode_list), selectmode='multiple')
    jobcode_listbox.pack()

    # Set the callback function
    def on_jobcode_changed(event):
        global select_jobs
        select_jobs = [jobcode_listbox.get(i) for i in jobcode_listbox.curselection()]
        print(select_jobs)

    jobcode_listbox.bind("<<ListboxSelect>>", on_jobcode_changed)

    def view_rpt():
        df = ReportWriter(day_one, day_two).print_to_json(
            rpt_type, selected_employees=select_emps, selected_jobs=select_jobs, json_fmt=True)
        df.reset_index(inplace=True)
        df.to_dict(orient='index')
        pt = Table(r_frame, dataframe=df, width=1000, height=600,
                   showstatusbar=True, editable=False)
        pt.show()

    def export_rpt():
        df = ReportWriter(day_one, day_two).print_to_json(
            rpt_type, selected_employees=select_emps, selected_jobs=select_jobs, json_fmt=True)
        result = df.fillna('')
        with app:
            pdf = render_template('render.html',
                            tables=[result.to_html(
                                table_id="table", classes="ui striped table")],
                            titles=result.columns.values,
                            timestamp=datetime.now().strftime('%b %d %Y (%I:%M:%S%p)'),
                            dates=[
                                datetime.strptime(day_one, "%Y%m%d").strftime(
                                    '%a, %b %d, %Y'),
                                datetime.strptime(day_two, "%Y%m%d").strftime(
                                    '%a, %b %d, %Y')
                            ],
                            rpttp=rpt_type,
                            select_emps=select_emps, select_jobs=select_jobs)
        name_string = rpt_type + '-' + day_one[-6:]  + '-' + day_two[-6:]
        export = open("exports/" + name_string + ".html", "w")
        export.write(pdf)
        export.close()

    def gusto_rpt():
        '''exports payroll to gusto'''
        if (pd.date_range(day_one, periods=1, freq='SM').strftime("%Y%m%d") != day_two):
                return jsonify('day_error')
        result = Payroll(day_one, day_two).process_payroll()
        if type(result) == 'empty':
            return result
        else:
            name_string = ChipConfig().query("SETTINGS", "company_name") + '-timesheet-' + \
                datetime.now().strftime('%Y-%m-%d')
            result.to_csv(
                ("exports/" + name_string + '.csv'),
                index=False)
            return 'exported'



    view_button = tk.Button(b_frame, text="View", command=view_rpt)
    view_button.pack()

    export_button = tk.Button(b_frame, text="Export", command=export_rpt)
    export_button.pack()

    payroll_button = tk.Button(b_frame, text="Payroll Export", command=gusto_rpt)
    payroll_button.pack()

    # Show the window
    root.mainloop()
