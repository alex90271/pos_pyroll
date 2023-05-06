from datetime import date, timedelta
import tkinter as tk
from tkcalendar import DateEntry
from flask import jsonify
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
    root.geometry("1200x800")

    day_one=(date.today()-timedelta(days = 1)).strftime('%Y%m%d')
    day_two=(date.today()-timedelta(days = 1)).strftime('%Y%m%d')
    rpt_type='labor_main'
    select_jobs=''
    select_emps=''

    l_frame = tk.Frame(root, width=200, height=600)
    l_frame.pack(side='left')

    r_frame = tk.Frame(root)
    r_frame.pack(side='right')

    # Create a label
    label = tk.Label(l_frame, text="Select a date range:")
    label.pack()

    # Create two date pickers
    start_date_picker = DateEntry(l_frame, width=12, background='darkblue', foreground='white', borderwidth=2)
    start_date_picker.pack()

    end_date_picker = DateEntry(l_frame, width=12, background='darkblue', foreground='white', borderwidth=2)
    end_date_picker.pack()

    # Set the minimum and maximum dates for both date pickers
    start_date_picker.min_date = (date.today()-timedelta(days = 365))
    start_date_picker.max_date = (date.today()-timedelta(days = 1))

    end_date_picker.min_date = (date.today()-timedelta(days = 365))
    end_date_picker.max_date = (date.today()-timedelta(days = 1))

    # Bind a callback function to both date pickers
    def on_date_changed(date):
        # Get the dates from both date pickers
        start_date = start_date_picker.get()
        end_date = end_date_picker.get()
        day_one=start_date.strftime('%Y%m%d')
        day_two=end_date.strftime('%Y%m%d')

    start_date_picker.bind("<<DateEntryChanged>>", on_date_changed)
    end_date_picker.bind("<<DateEntryChanged>>", on_date_changed)


    value_inside = tk.StringVar(root)
    value_inside.set("Select an Option")
    label = tk.Label(l_frame, text="Select a report:")
    label.pack()

    report_dropdown = tk.OptionMenu(l_frame, value_inside, *reports)
    report_dropdown.pack()

    # Set the callback function
    def on_report_changed(report):
        rpt_type=report.value_inside.get()
        print(rpt_type)
        return None

    report_dropdown.bind("<<MenuSelect>>", on_report_changed)

    # Create a label
    label = tk.Label(l_frame, text="Select an employee:")
    label.pack()

    # Create a list box
    employee_listbox = tk.Listbox(l_frame, listvariable=tk.StringVar(l_frame, value=employee_list))
    employee_listbox.pack()

    # Set the callback function
    def on_employee_changed(event):
        select_emps=employee_listbox.get(employee_listbox.curselection())
        print(select_emps)

    employee_listbox.bind("<<ListboxSelect>>", on_employee_changed)

    # Create a label
    label = tk.Label(l_frame, text="Select a job code:")
    label.pack()

    # Create a list box
    jobcode_listbox = tk.Listbox(l_frame, listvariable=tk.StringVar(l_frame, value=jobcode_list))
    jobcode_listbox.pack()

    # Set the callback function
    def on_jobcode_changed(event):
        select_jobs=jobcode_listbox.get(jobcode_listbox.curselection())
        print(select_jobs)

    jobcode_listbox.bind("<<ListboxSelect>>", on_jobcode_changed)

    def print_rpt():
        df = ReportWriter(day_one, day_two).print_to_json(
        rpt_type, selected_employees=select_emps, selected_jobs=select_jobs, json_fmt=True)
        df.reset_index(inplace=True)
        df.to_dict(orient='index')
        pt = Table(r_frame,dataframe=df, width=1000, height=600, showstatusbar=True, editable=False)
        pt.show()

    submit_button = tk.Button(l_frame, text="Submit", command=print_rpt)
    submit_button.pack()

    # Show the window
    root.mainloop()

