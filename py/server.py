
# 127.0.0.1:5000/
# available data:
# ['tip_rate', 'labor_main', 'labor_rate', 'cout_eod', 'labor_total']
# date format YYYYMMDD (ex. July 4th, 2021 would be represented as: 20210704)

# v01 Routes
from datetime import datetime
import os
import signal

import pandas as pd

from query_db import QueryDB
from flask import Flask, redirect, render_template, url_for, request, jsonify
from flask_cors import CORS, cross_origin
from report_writer import Payroll, ReportWriter, ReportWriterReports
from chip_config import ChipConfig


app = Flask(__name__, static_url_path='')
cors = CORS(app)
app.config['JSON_SORT_KEYS'] = False
debug = False  # set to false to turn off print statements


@cross_origin
@app.route('/')
def index():
    return render_template('index.html')


@cross_origin
@app.route('/v01/data/<day_one>/<day_two>/<rpt_type>/<select_jobs>/<select_emps>')
@app.route('/v01/data/<day_one>/<day_two>/<rpt_type>/<select_jobs>/<select_emps>/<opt_print>/')
def print_rpt(day_one, day_two, rpt_type, select_jobs, select_emps, opt_print='json'):
    if select_emps == '0':
        select_emps = None
    else:
        select_emps = [int(item) for item in select_emps.split(',')]
    if select_jobs == '0':
        select_jobs = None
    else:
        select_jobs = [int(item) for item in select_jobs.split(',')]
    opt_print = str(opt_print).lower()

    if debug:
        print(select_jobs, select_emps)

    json_fmt = False
    if opt_print == 'json':
        json_fmt = True

    result = ReportWriter(day_one, day_two).print_to_json(
        rpt_type, selected_employees=select_emps, selected_jobs=select_jobs, json_fmt=json_fmt)
    if type(result) == str:
        return jsonify('empty')
    # result.reset_index(drop=True, inplace=True)

    if opt_print == 'json':
        # turn any NaN data to Zero for json compatability
        result = result.fillna(0)
        result.reset_index(inplace=True)
        return result.to_dict(orient='index')
    elif opt_print == 'html':
        # turn any NaN data to blank for printability
        result = result.fillna('')
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
        name_string = rpt_type + '-report-' + \
            datetime.now().strftime('%Y-%m-%d')
        export = open("exports/" + name_string + ".html", "w")
        export.write(pdf)
        export.close()
        return jsonify('exported')
    else:
        raise ValueError(
            'Print argument not passed json or html -- leave blank for json')


@app.route('/v01/data/gusto/<day_one>/<day_two>')
def gusto(day_one, day_two):
    '''exports payroll to gusto'''
    if (pd.date_range(day_one, periods=1, freq='SM').strftime("%Y%m%d") != day_two):
            return jsonify('day_error')
    result = Payroll(day_one, day_two).process_payroll()
    if type(result) == 'empty':
        return jsonify('empty')
    else:
        name_string = ChipConfig().query("SETTINGS", "company_name") + '-timesheet-' + \
            datetime.now().strftime('%Y-%m-%d')
        result.to_csv(
            ("exports/" + name_string + '.csv'),
            index=False)
        return jsonify('exported')


@app.route('/v01/data/house_acct/<day_one>/<day_two>')
def house_acct(day_one, day_two):
    result = ReportWriter(day_one, day_two).house_accounts()
    print(result)
    return jsonify(result.to_dict(orient='index'))


@app.route('/v01/employees/in_period/<day_one>/<day_two>')
def employees_in_period(day_one, day_two):
    result = ReportWriter(day_one, day_two).employees_in_dates()
    print(result)
    return jsonify(result.to_dict(orient='index'))


@app.route('/v01/config/', methods=["GET"])
def full_config():
    return jsonify(ChipConfig()
                   .read_json())


@app.route('/v01/config/<cfg>', methods=["GET"])
def config_item(cfg):
    return jsonify(ChipConfig()
                   .query(cfg))


@app.route('/v01/config/<cfg>/<query>', methods=["GET"])
def config_list_item(cfg, query):
    return jsonify(ChipConfig()
                   .query(cfg, str(query)))


@app.route('/v01/config/<cfg>/<updated_cfg>')
def config_item_update(cfg, updated_cfg):
    print(updated_cfg)


@app.route('/v01/employees')
def employee_list():
    return jsonify(QueryDB()
                   .process_db('employees')
                   .to_dict(orient='records'))

@app.route('/v01/1365438ff5213531a63c246846814a')
def shutdown():
    os.kill(os.getpid(), signal.SIGINT)
    return('attempting to stop')


@app.route('/v01/jobcodes')
def jobcode_list():
    return jsonify(QueryDB()
                   .process_db('jobcodes')
                   .to_dict(orient='records'))


@app.route('/v01/reports')
def report_list():
    return jsonify(
        ReportWriterReports().available_reports()
    )
# Unfinished Requests
# @app.route('/v01/data/post/<employee_id>/<data>', methods=["POST"])


def update_data(employee_id, data):
    # TODO Finish this. Accepts a json object from frontend {employee_ID : data}
    # data would be adjustments on the worksheet
    pass


if __name__ == '__main__':
    from waitress import serve
    serve(app, host='localhost', port='5000')
