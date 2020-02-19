"""
Description:
Author: Alvin yx
Action      Date        Content
------------------------------------
Create      2019-
"""
from pywinauto import application

app = application.Application().start("C:\Program Files (x86)\Google\Chrome\Application\chrome.exe")
dlg = app.window(class_name=r"Chrome_WidgetWin_1")
print(dlg.print_control_identifiers())
print(dlg.print_ctrl_ids())