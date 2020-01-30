'''
Main module.
'''
import sys

from fbs_runtime.application_context.PyQt5 import ApplicationContext
from app import MainWindow

if __name__ == '__main__':
    APPCTXT = ApplicationContext()       # 1. Instantiate ApplicationContext

    WINDOW = MainWindow()
    WINDOW.show()

    EXIT_CODE = APPCTXT.app.exec_()      # 2. Invoke APPCTXT.app.exec_()

    sys.exit(EXIT_CODE)
