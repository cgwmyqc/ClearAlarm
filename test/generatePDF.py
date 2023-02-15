import os
from win32com.client import DispatchEx


xlapp = DispatchEx("Excel.Application")
xlapp.Visible = False
xlapp.DisplayAlerts = 0
books = xlapp.Workbooks.Open(os.path.join(os.path.abspath(".."), "../excel", "template", "a.xlsx"), False)
books.ExportAsFixedFormat(0, os.path.join(os.path.abspath(".."), "../pdf", "a.pdf"))
books.Close(False)
xlapp.Quit()



