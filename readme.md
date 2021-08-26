python dependencies (updated 8-11-2021)

    pandas
    dbfread
    xlsxwriter
    flask
    flask_cors
    timeit - (used only for testing purposes)
    sqlite3

    WINDOWS ONLY:
     win32api
     win32print

built on python 3.8.6 64Bit

run server.py to launch API

run test.py for viewing data in the console, or printing reports

date format YYYYMMDD (ex. July 4th, 2021 would be represented as: 20210704)

test.py uses command line args, edit the launch.json line: "args": ["20210416", "20210530", "True"], to change 

    (TRUE at the end will print the file to a printer, if on windows. )

WORK IN PROGRESS:

    database has been built, just needs to be connected to process_labor class

    Employee Numbers included in data (Finished-- though sending the request response gives an error when using employee ID as Index, as the ID might not be unique (ex. multiple shifts))

API:

/v01/data/<str: day_one>/<str: day_two>/<str: rpt_type>/<int: jobcode_filter>/<int: employee_filter>/<bool: print>

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

    pass 'print = True' to print report
        changes to invoke the report printer function
        when print 'True' is passed, the result will either be 'True' or 'False' depending on if it printed or not

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

    config selects a settings section within chip.json (see chip_config.py OR chip.json for data)

    returns a config item. see cfg.py for more details

    pass with an {updated_query_result} to save it

    delete the .json file to generate a new one

/v01/jobcodes

    returns a list of jobcodes, and their IDs (ex. Jobcode 50 is Manager)

/v01/employees

    returns a list of employees and their employee number
    employees with the TERMINATED: Y flag are, terminated. Their data is pulled for historical reporting
