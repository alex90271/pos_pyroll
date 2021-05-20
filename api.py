
#127.0.0.1:5000/

import timeit
import numpy as np
import sys
import os
from gen_rpt import gen_rpt
from datetime import timedelta, date, datetime
from cfg import cfg
import json
import connexion

from flask import (
    Flask,
    render_template
)

# Create the application instance
#app = Flask(__name__, template_folder="frontend\public")

app = connexion.App(__name__, specification_dir='./')

# Read the swagger.yml file to configure the endpoints
app.add_api('swagger.yml')

# Create a URL route in our application for "/"
@app.route('/')
def index():
    return render_template('index.html')

# If we're running in stand alone mode, run the application
if __name__ == '__main__':
    app.run(debug=True)
