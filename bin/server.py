
#127.0.0.1:5000/
#available data: 
#['tip_rate', 'labor_main', 'labor_rate', 'cout_eod', 'labor_total']
#date format YYYYMMDD (ex. July 4th, 2021 would be represented as: 20210704)

#v01 Routes

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

class UtilFunc():
    def get_zero(zero):
        '''this does exactly what you think it does. it gets zero. its kinda useful'''
        return 0

@app.route('/v01/data/<day_one>/<day_two>/<rpt_type>/<opt_print>')
def print_rpt(day_one, day_two, rpt_type, opt_print):
    print(str(opt_print))
    if str(opt_print).lower() == 'true':
        result = ReportWriter(day_one, day_two).print_to_excel(rpt_type)
        return jsonify(result)
    if str(opt_print).lower() == 'false':
        result = ReportWriter(day_one, day_two).print_to_json(rpt_type)
        result.reset_index(drop=True, inplace=True)
        result['MEALS'] = result['MEALS'].apply((UtilFunc.get_zero))
        print('block one')
        return jsonify(result.to_dict(orient='index')) #'False' assumes the return type DataFrame
    else:
        raise ValueError('Print argument not passed a bool type')

@app.route('/v01/config/', methods=["GET"])
def full_config():
    return jsonify(ChipConfig()
    .read_json())

@app.route('/v01/config/<query>/save', methods=["GET"])
def config_item(query):
    return jsonify(ChipConfig()
    .query('SETTINGS',str(query)))

@app.route('/v01/employee')
def employee_list():
    return jsonify(QueryDB()
    .process_db('employees')
    .to_dict(orient='records'))

@app.route('/v01/jobcodes')
def jobcode_list():
    return jsonify(QueryDB()
    .process_db('jobcodes')
    .to_dict(orient='records'))

#Unfinished Requests
#@app.route('/v01/data/post/<employee_id>/<data>', methods=["POST"])
def update_data(employee_id,data):
    #TODO Finish this. Accepts a json object from frontend {employee_ID : data}
    #data would be adjustments on the worksheet
    pass


if __name__ == '__main__':
    app.run(debug=True)