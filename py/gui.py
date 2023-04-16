import dearpygui.dearpygui as dpg
from flask import jsonify
import pandas as pd
from query_db import QueryDB
from report_writer import Payroll, ReportWriter, ReportWriterReports
from chip_config import ChipConfig
import dearpygui.dearpygui as dpg
import dearpygui.demo as demo

dpg.create_context()
dpg.create_viewport(title='Custom Title', width=800, height=800)

def print_rpt(day_one, day_two, rpt_type, select_jobs, select_emps, opt_print='json'):
    result = ReportWriter(day_one, day_two).print_to_json(
        rpt_type, selected_employees=select_emps, selected_jobs=select_jobs, json_fmt=True)

    if opt_print == 'json':
        # turn any NaN data to Zero for json compatability
        result = result.fillna(0)
        result.reset_index(inplace=True)
        return result.to_dict(orient='index')

employee_list = QueryDB().process_db('employees').to_dict(orient='records')
jobcode_list = QueryDB().process_db('jobcodes').to_dict(orient='records')
items = ReportWriterReports().available_reports()
dataset = pd.DataFrame()


def button_callback(sender, data):
    start_date = dpg.get_value('date_range_picker')
    end_date = dpg.get_value('date_range_picker')
    report_name = dpg.get_value('report_dropdown')
    employee_selections = dpg.get_value('employee_listbox')
    jobcode_selections = dpg.get_value('jobcode_listbox')
    dataset = pd.DataFrame(print_rpt(day_one='20230401', day_two='20230401', rpt_type='labor_main',
                      select_emps=[], select_jobs=[], opt_print='json'))
    return dataset


with dpg.window():
    dpg.add_text("Select a date range:")
    dpg.add_date_picker(id='date_range_picker')
    dpg.add_combo(id='report_dropdown', items=items)
    dpg.add_listbox(id='employee_listbox', items=employee_list)
    dpg.add_listbox(id='jobcode_listbox', items=jobcode_list)
    dpg.add_button(id='submit_button', label='Submit',
                   callback=button_callback)
    with dpg.table(label='DatasetTable'):
        for i in range(dataset.shape[1]):
            dpg.add_table_column(label=dataset.columns[i])
        for i in range(9):
            with dpg.table_row():
                for j in range(dataset.shape[1]):
                    dpg.add_text(f"{dataset.iloc[i,j]}")


dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
