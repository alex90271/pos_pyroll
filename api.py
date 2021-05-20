
#127.0.0.1:5000/

#/api/config/<config_id>
#/api/employees/<employee_id>
#/api/jobcodes/<jobcode_id>
#/api/data/reports/<report_id>

import timeit
import numpy as np
import sys
import os
from gen_rpt import gen_rpt
from datetime import timedelta, date, datetime
from cfg import cfg
import json

from flask import (
    Flask,
    render_template
)

# Create the application instance
app = Flask(__name__, template_folder="templates")

# Create a URL route in our application for "/"
@app.route('/')
def home():
    """
    This function just responds to the browser ULR
    localhost:5000/

    :return:        the rendered template 'home.html'
    """
    return render_template('home.html')

# If we're running in stand alone mode, run the application
if __name__ == '__main__':
    app.run(debug=True)
