
#127.0.0.1:5000/

from query_db import QueryDB
import numpy as np
import os
import json
from flask import Flask, redirect, url_for, request, jsonify
from flask_cors import CORS
from report_writer import ReportWriter
from chip_config import ChipConfig

app = Flask(__name__)
CORS(app)

#available data: 
#['tip_rate', 'labor_main', 'labor_rate', 'cout_eod', 'labor_total']
#date format YYYYMMDD (ex. July 4th, 2021 would be represented as: 20210704)

#v01 Routes
@app.route('/v01/data/<day_one>/<day_two>/<rpt_type>/<opt_print>')
def print_rpt(day_one, day_two, rpt_type, opt_print):

    result = ReportWriter(day_one, day_two).print_to_excel(rpt_type, opt_print=opt_print)
    if opt_print == 'False':
        return result.to_json() #'False' assumes the return type DataFrame
    return jsonify(result)

@app.route('/v01/config/', methods=["GET"])
def full_config():
    return jsonify(ChipConfig().read_json())

@app.route('/v01/config/<query>', methods=["GET"])
def config_item(query):
    return jsonify(ChipConfig().query('SETTINGS',str(query)))

@app.route('/v01/employee')
def employee_list():
    return jsonify(QueryDB().process_db('employees').to_json())

@app.route('/v01/jobcodes')
def jobcode_list():
    return jsonify(QueryDB().process_db('jobcodes').to_json())

#Unfinished Requests
#@app.route('/v01/data/post/<employee_id>/<data>', methods=["POST"])
def update_data(employee_id,data):
    #TODO Finish this. Accepts a json object from frontend {employee_ID : data}
    #data would be adjustments on the worksheet
    pass


if __name__ == '__main__':
    app.run(debug=True)