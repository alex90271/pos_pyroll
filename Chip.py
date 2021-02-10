# python -m pip install tkcalendar
# python -m pip install pandas
# python -m pip install dbfread
# python -m pip install xlsxwriter
# python -m pip install python-quickbooks

import timeit
from gen_rpt import gen_rpt

if __name__ == '__main__':
    print("loading chip.py")

    def main():
        rpt = gen_rpt('20210101', '20210115')
        print(rpt.labor_main())

    f = timeit.timeit("main()", "from __main__ import main", number=1)
    print("completed in " + str(round(f,2)) + " seconds")


