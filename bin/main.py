import timeit
import numpy as np
import sys
import os
from report_writer import ReportWriter


if __name__ == '__main__':
    print("\nloading chip.py\n")

    print("cleaning reports folder")
    #remove all the old reports in the output folder
    [os.remove(os.path.join('reports', f))for f in os.listdir('reports')]

    def main():
        
        #you can clear the enviroment and set the json_name to read a different settings file, or simply generate a new one with a different name
        #if no variable is set here, it will use the default, set in cfg.py 'chip.json'
        #os.environ.clear()
        day_one = str(sys.argv[1])
        day_two = str(sys.argv[2])
        rpt_list = list(['tip_rate', 'labor_main', 'labor_rate', 'cout_eod', 'labor_total'])

        #full command: python chip.py json_name day_one day_two
        #testing: python chip.py chip.json 20210101 20210115
        print('\nday one: ' + day_one + '\nday two: ' + day_two + '\n')

        #to select same day, pass day_one and day_two as the same
        [ReportWriter(day_one,day_two).print_to_excel(rpt) for rpt in rpt_list]
        
    #setting reports only to True skips launching the flask server
    debug = True
    if debug:
        r = 1
        f = timeit.repeat("main()", "from __main__ import main", number=1, repeat=r)
        print("completed with an average of " + str(np.round(np.mean(f),2)) + " seconds over " + str(r) + " tries \ntotal time: " + str(np.round(np.sum(f),2)) + "s")
    else:
        main()

