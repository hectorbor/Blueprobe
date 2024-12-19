#!/bin/python3

# import sys

# modulename = 'PySimpleGUI'
# if modulename not in sys.modules:
#     print ('You have not imported the' +modulename+ 'module')

import PySimpleGUI as sg
import csv

# All the stuff inside your window.
layout = [  [sg.Text('Some text on Row 1')],
            [sg.Text('Enter something on Row 2'), sg.InputText()],
            [sg.FileBrowse(key='-FILE_PATH-')],            
            [sg.Button('Ok'), sg.Button('Cancel')] ]

# Create the Window
window = sg.Window('Window Title', layout)

# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
        break
    print('You entered ', values[0])

window.close()
