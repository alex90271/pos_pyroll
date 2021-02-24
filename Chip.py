# python -m pip install tkcalendar
# python -m pip install pandas
# python -m pip install dbfread
# python -m pip install xlsxwriter
# python -m pip install python-quickbooks

import timeit
import numpy as np
from gen_rpt import gen_rpt

class rpt_out(gen_rpt):
    def __init__(self):
        pass

if __name__ == '__main__':
    print("\nloading chip.py\n")

    def main():
        for rpt in ['tip_rate', 'labor_main', 'labor_rate', 'cout_eod']:
            gen_rpt('20210101','20210115').print_to_excel(rpt)

        
    r = 1
    f = timeit.repeat("main()", "from __main__ import main", number=1, repeat=r)
    print("completed with an average of " + str(np.round(np.mean(f),2)) + " seconds over " + str(r) + " tries \ntotal time: " + str(np.round(np.sum(f),2)) + "s")


