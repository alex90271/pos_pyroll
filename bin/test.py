import timeit
import numpy as np
import sys
import os
import json
from excel_writer import ExcelPrinter
from report_writer import ReportWriter


if __name__ == '__main__':
    print("\nloading chip.py\n")

    #print("cleaning reports folder")
    #remove all the old reports in the output folder
    #[os.remove(os.path.join('data/.xlsx', f))for f in os.listdir('data/.xlsx')]

    def main():
        
        #you can clear the enviroment and set the json_name to read a different settings file, or simply generate a new one with a different name
        #if no variable is set here, it will use the default, set in cfg.py 'chip.json'
        #os.environ.clear()
        day_one = str(sys.argv[1])
        day_two = str(sys.argv[2])
        try:
            selected_employees = [int(item) for item in sys.argv[3].split(',')]
            for i in range(0, len(selected_employees)):
                selected_employees[i] = int(selected_employees[i])
            print(selected_employees)
        except:
            selected_employees=[]
        try:
            selected_jobs=[int(item) for item in sys.argv[4].split(',')]
            for i in range(0, len(selected_jobs)):
                selected_jobs[i] = int(selected_jobs[i])
            print(selected_jobs)
        except:
            selected_jobs=[]


        #full command: python chip.py json_name day_one day_two
        #testing: python chip.py chip.json 20210101 20210115
        print('\nday one: ' + day_one + '\nday two: ' + day_two + '\n')

        #result = (ReportWriter(day_one,day_two).print_to_excel('labor_main', opt_print=False, sum_only=True).to_json(orient='index', indent=4))
        #parsed = json.loads(result)
        #print(json.dumps(parsed, indent=4))

        #ExcelPrinter(day_one,day_two).print_to_excel('labor_nightly') #PRINTS TO A FILE, pass Pys_print=True to print to a printer

        #print(ReportWriter(day_one,day_two).print_to_json('tip_rate'))
        #print(ReportWriter(day_one,day_two).print_to_json('labor_rate'))
        #print(ReportWriter(day_one,day_two).print_to_json('cout_eod'))
        day_list = [["20190701", "20190706"], 
                    ["20190708", "20190713"], 
                    ["20190715", "20190720"], 
                    ["20190722", "20190727"], 
                    ["20190701", "20190706"],
                    ["20190729", "20190803"],
                    ["20190805", "20190810"],
                    ["20190812", "20190817"],
                    ["20190819", "20190824"]]

        day_list = [["20210820", "20210829"]]

        for days in day_list:
            print((ExcelPrinter(days[0], days[1])
                .print_to_excel(
                    'labor_nightly',
                    selected_employees=None, 
                    selected_jobs=selected_jobs)))

        for days in day_list:
            print((ExcelPrinter(days[0], days[1])
                .print_to_excel('labor_rate')))
                
    
    debug = True
    if debug:
        r = 1
        f = timeit.repeat("main()", "from __main__ import main", number=1, repeat=r)
        print("completed with an average of " + str(np.round(np.mean(f),2)) + " seconds over " + str(r) + " tries \ntotal time: " + str(np.round(np.sum(f),2)) + "s")
    else:
        main()