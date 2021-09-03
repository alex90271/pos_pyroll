
#127.0.0.1:5000/
#available data: 
#['tip_rate', 'labor_main', 'labor_rate', 'cout_eod', 'labor_total']
#date format YYYYMMDD (ex. July 4th, 2021 would be represented as: 20210704)

#v01 Routes

from excel_writer import ExcelPrinter
from query_db import QueryDB
import numpy as np
import os
import json
from flask import Flask, redirect, url_for, request, jsonify
from flask_cors import CORS, cross_origin
from report_writer import ReportWriter
from chip_config import ChipConfig

app = Flask(__name__)
cors = CORS(app)
app.config['JSON_SORT_KEYS'] = False

@cross_origin
@app.route('/v01/data/<day_one>/<day_two>/<rpt_type>/<select_jobs>/<select_emps>/<opt_print>')
def print_rpt(day_one, day_two, rpt_type, select_jobs, select_emps, opt_print):
    if select_emps == '0':
         select_emps = None
    else:
        select_emps = [int(item) for item in select_emps.split(',')]
    if select_jobs == '0':
        select_jobs = None
    else:
        select_jobs = [int(item) for item in select_jobs.split(',')]
    opt_print = str(opt_print).lower()
    #print(select_jobs, select_emps)
    if opt_print == 'true':
        result = ExcelPrinter(day_one, day_two).print_to_excel(rpt_type, selected_employees=select_emps, selected_jobs=select_jobs)
        return jsonify(result)
    if opt_print == 'false':
        result = ReportWriter(day_one, day_two).print_to_json(rpt_type, selected_employees=select_emps, selected_jobs=select_jobs)
        result.reset_index(drop=True, inplace=True)
        def zero(x):
            return 0
        result['MEALS'] = result['MEALS'].apply((zero))
        return jsonify(result.to_dict(orient='index')) #'False' assumes the return type DataFrame
    else:
        raise ValueError('Print argument not passed a bool type')

@app.route('/v01/config/', methods=["GET"])
def full_config():
    return jsonify(ChipConfig()
    .read_json())

@app.route('/v01/config/<cfg>/<query>', methods=["GET"])
def config_item(cfg, query):
    return jsonify(ChipConfig()
    .query(cfg,str(query)))

@app.route('/v01/config/<cfg>/<query_item>/<updated_val>', methods=["GET"])
def config_item_update(cfg, query_item, updated_val):
    return jsonify(ChipConfig()
    .query(cfg,str(query_item),updated_result=updated_val))

@app.route('/v01/employees')
def employee_list():
    return jsonify(QueryDB()
    .process_db('employees')
    .to_dict(orient='records'))

@app.route('/v01/jobcodes')
def jobcode_list():
    return jsonify(QueryDB()
    .process_db('jobcodes')
    .to_dict(orient='records'))

@app.route('/v01/report_list')
def report_list():
    return 'report_list'

#Unfinished Requests
#@app.route('/v01/data/post/<employee_id>/<data>', methods=["POST"])
def update_data(employee_id,data):
    #TODO Finish this. Accepts a json object from frontend {employee_ID : data}
    #data would be adjustments on the worksheet
    pass


if __name__ == '__main__':
    app.run(debug=True)