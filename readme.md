### --- REQUIREMENTS

Tauri requires rust, and rust requires the windows APIs to be used on windows

    rust-lang.org

    1. download: https://visualstudio.microsoft.com/visual-cpp-build-tools/

    2. download: https://rustup.rs/


### --- INSTALL INSTRUCTIONS

    1. First see requirements above

    2. Run `python -m pip install -r "requirements.txt"`

    3. Run `npm install`

    4. Compile backend
        a. `cd src-tauri\bin`
        b. `pyinstaller server.py --onefile --add-data "templates;templates" --add-data "static;static"`
        c. Move the .exe file from the bin\dist folder, one directory up to the bin folder. 
            i. Rename it server-x86_64-pc-windows-msvc.exe (for tauri to find)

    5. To launch, `npm run tauri dev`


### --- DIRECTORIES

    1. src-tauri : tauri directory
        a. src-tauri/bin : python source code
    2. src : react source code

### ---FRONTEND:

The frontend is written in react, and controlled with tauri

    dependency install: `npm install`

In the project directory, you can run:

     `npm start`

        Runs the app in the development mode.\
        Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

        The page will reload if you make edits.\
        You will also see any lint errors in the console.

    `npm run tauri dev`

        Launches tauri dev server

    `npm run tauri build`

        Build tauri output, see tauri documentation

### ---BACKEND:

Pyinstaller Compile Command: 
pyinstaller server.py --onefile --add-data "templates;templates" --add-data "static;static"  

    dependency install: `python -m pip install -r "requirements.txt"`

built on python 3.8.6 64Bit

run server.py to launch API

run test.py for viewing data in the console, or printing reports

date format YYYYMMDD (ex. July 4th, 2021 would be represented as: 20210704)

test.py uses command line args, edit the launch.json line: "args": ["20210416", "20210530", "True"], to change 

    (TRUE at the end will print the file to a printer, if on windows. )

API:

IF NO DATA IS AVAILABLE TO BE RETURNED, API WILL RETURN 'empty'

/v01/data/<str: day_one>/<str: day_two>/<str: rpt_type>/<int: jobcode_filter>/<int: employee_filter>/<str: opt_print>

    day_one = first day in the sequence (ex. 20210701)

    day_two = last day in the sequence (ex. 20210705) -- to submit for just ONE day, pass it for both args

    rpt_type = type of data to print or return (ex. labor_main) 
    options: 
        labor_main = Returns data containing detailed labor / payroll info (including tip information) 
        (use this for fetching any labor data such as hours, tips, etc.)
        tip_rate = Returns data containing tip hourly rates
        labor_rate = Contains labor percentages based on cost of labor to sales ratio
        cout_eod = Contains a list of shifts that were auto clocked out (and their clock-out time)
    
    jobcode_filter
        takes an integer to filter the report based on the jobcode number
        api /jobcodes (see below) can proivde a list
        for more than one, separate with a comma
        ex. 50,1,4 would filter on jobcode 50, 1, and 4

        pass 0 to not filter data

    employee_filter
        takes an integer to filter the report based on the employee number
        api /employees (see below) can proivde a list
        for more than one, separate with a comma
        ex. 4006,3089 would filter on employee 4006 and 3089
        
        pass 0 to not filter data

    pass opt_print = 'html' to output a printable html verison of the report
    pass opt_print = 'json' to output a json file for the frontent
        default is json if no option is provided

    example query, no filter: 
        http://localhost:5000/v01/data/20210416/20210430/labor_main/0/0/False

    example query, with filter (jobcode 50, employees 4006 and 3089): 
        http://localhost:5000/v01/data/20210416/20210430/labor_main/50/4006,3089/False

returns, for each shift:

    {
    "0":{
        "LASTNAME":"",
        "FIRSTNAME":"",
        "HOURS":203.83,
        "OVERHRS":0.0,
        "SRVTIPS":0.0,
        "TIPOUT":40.0002720771,
        "DECTIPS":0.0,
        "MEALS":0
    },
    "1":{
        "LASTNAME":"",
        "FIRSTNAME":"",
        "HOURS":184.27,
        "OVERHRS":0.0,
        "SRVTIPS":3213.4804,
        "TIPOUT":170.6219823755,
        "DECTIPS":0.0,
        "MEALS":0
    },
    "2":{
        "LASTNAME":"",
        "FIRSTNAME":"",
        "HOURS":108.25,
        "OVERHRS":0.0,
        "SRVTIPS":0.0,
        "TIPOUT":0.0,
        "DECTIPS":0.0,
        "MEALS":0
    },
    "3":{
        "LASTNAME":"",
        "FIRSTNAME":"",
        "HOURS":245.99,
        "OVERHRS":161.19,
        "SRVTIPS":0.0,
        "TIPOUT":0.0,
        "DECTIPS":0.0,
        "MEALS":0
    },
    "4":{
        "LASTNAME":"",
        "FIRSTNAME":"",
        "HOURS":43.59,
        "OVERHRS":0.0,
        "SRVTIPS":0.0,
        "TIPOUT":379.8103894286,
        "DECTIPS":0.0,
        "MEALS":0
    },
    "5":{
        "LASTNAME":"TTL",
        "FIRSTNAME":"",
        "HOURS":29.36,
        "OVERHRS":0.0,
        "SRVTIPS":0.0,
        "TIPOUT":245.0726951291,
        "DECTIPS":0.0,
        "MEALS":0
    }


/v01/data/change/<str: day>/{request_body}

    Expected Body-- These are net changes to the orignial data

    day is formatted YYYYMMDD (see date format above):

    {
        "LASTNAME":STRING, #not changeable, please change in POS
        "FIRSTNAME":STRING, #not changeable, please change in POS
        "DESC":STRING, #optional. breif description of change, 
        "HOURS":FLOAT, # (applies to all below)positve or negative. essentially 'add or subtract tips from original' 
        "OVERHRS":FLOAT,
        "SRVTIPS":FLOAT,
        "TIPOUT":FLOAT,
        "DECTIPS":FLOAT,
        "MEALS":FLOAT,
    }

/v01/config/<str: config>/<str: query>/{updated_query_result}

    config selects a settings section within chip.json

    returns a config item. see chip_config.py line 23, for more config sections

    pass with an {updated_query_result} to save it

    delete the .json file to generate a new one (necessary when config changes are made)

    If query is NONE, it will return the entire config section (i.e. /v01/config/FRONTEND_SETTINGS) will return just the frontend section

/v01/config/FRONTEND_SETTINGS

    returns frontend settings options

/v01/config/REPORT_OPTIONS

    returns a list of available report options

    line 0 will always be the descrition of the report

    following lines are the available columns

/v01/jobcodes

    returns a list of jobcodes, and their IDs (ex. Jobcode 50 is Manager)

/v01/employees

    returns a list of employees and their employee number
    employees with the TERMINATED: Y flag are, terminated. Their data is pulled for historical reporting

/v01/employees/in_period/<str: day_one>/<str: day_two>
    
    returns a dataframe of employees and their names that are available during the specified period