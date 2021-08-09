import win32api
import win32print
import time

file = 'reports\\tip_rate_20210726_20210807.xlsx'
printer = win32print.GetDefaultPrinter() #win32print.EnumPrinters(2)

win32api.ShellExecute (
    0,
    "print",
    file,
    '/d:"%s"' % printer,
    ".",
    0
)

if printer == 'Microsoft Print to PDF':
    time.sleep(5)
else:
    time.sleep(3)
