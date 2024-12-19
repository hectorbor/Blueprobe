#!/bin/python3

# import sys

# modulename = 'PySimpleGUI'
# if modulename not in sys.modules:
#     print ('You have not imported the' +modulename+ 'module')

import PySimpleGUI as sg
import csv

# Creating layouts for every possible window
layout1 = [ [sg.Text('Introduce the .csv file to be analyzed'), sg.FileBrowse(key='-FILE_PATH-')],
            [sg.CalendarButton("From", close_when_date_chosen=True,  target='-DEPARTURE-', location=(0,0), no_titlebar=False ), sg.Input(key='-DEPARTURE-', size=(20,1))],
            [sg.CalendarButton("To", close_when_date_chosen=True,  target='-ARRIVAL-', location=(0,0), no_titlebar=False ), sg.Input(key='-ARRIVAL-', size=(20,1))],
            [sg.Radio('Bluetooth Classic', group_id=1, default=True), sg.Radio('Bluetooth Low Energy', group_id=1)],            
            [sg.Button('Analyze'), sg.Button('Clear')] ]

layout2 = [ [sg.Text('Successful change')]]

# Organizing all the layouts
layout = [      [sg.Column(layout1, key='COL1'),
     sg.Column(layout2, key='COL2', visible=False)] ]

# Create the Window
window = sg.Window('Window Title', layout)

col1, col2 = window['COL1'], window['COL2']

# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED : # if user closes window or clicks cancel
        break
    elif event == 'Analyze' :
        col2.update(visible=True)
        col1.update(visible=False)

window.close()
