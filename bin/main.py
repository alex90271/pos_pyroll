import timeit
import numpy as np
import sys
import os
import json
from report_writer import ReportWriter


if __name__ == '__main__':
    print("\nloading chip.py\n")

    print("cleaning reports folder")
    #remove all the old reports in the output folder
    [os.remove(os.path.join('.\\reports', f))for f in os.listdir('reports')]

    def main():
        
        #you can clear the enviroment and set the json_name to read a different settings file, or simply generate a new one with a different name
        #if no variable is set here, it will use the default, set in cfg.py 'chip.json'
        #os.environ.clear()
        day_one = str(sys.argv[1])
        day_two = str(sys.argv[2])

        #full command: python chip.py json_name day_one day_two
        #testing: python chip.py chip.json 20210101 20210115
        print('\nday one: ' + day_one + '\nday two: ' + day_two + '\n')

        #to select same day, pass day_one and day_two as the same
        result = (ReportWriter(day_one,day_two)
        .print_to_excel('labor_main', opt_print=False, sum_only=True)
        .to_json(orient='index', indent=4)
        )
        parsed = json.loads(result)
        print(json.dumps(parsed, indent=4))
        #ReportWriter(day_one,day_two).print_to_excel('tip_rate', opt_print=True)
       # ReportWriter(day_one,day_two).print_to_excel('labor_rate', opt_print=True)
       # ReportWriter(day_one,day_two).print_to_excel('cout_eod', opt_print=True)
       # ReportWriter(day_one,day_two).print_to_excel('labor_main', opt_print=True, sum_only=True, selected_employees=[4006], selected_jobs=[50])
        
    #setting reports only to True skips launching the flask server
    debug = True
    if debug:
        r = 1
        f = timeit.repeat("main()", "from __main__ import main", number=1, repeat=r)
        print("completed with an average of " + str(np.round(np.mean(f),2)) + " seconds over " + str(r) + " tries \ntotal time: " + str(np.round(np.sum(f),2)) + "s")
    else:
        main()