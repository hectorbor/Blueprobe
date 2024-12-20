#!/bin/python3

# import sys

# modulename = 'PySimpleGUI'
# if modulename not in sys.modules:
#     print ('You have not imported the' +modulename+ 'module')

import PySimpleGUI as sg
import csv, os, json
from datetime import datetime

#Auxiliary functions

#To create a dictionary from a file address
def convert_csv_array(csv_address):
    file = open(csv_address)
    csv_reader = csv.reader(file)
    header = next(csv_reader)
    rows = []
    for row in csv_reader:
        rows.append(row)
    file.close()
    return rows

def filter_by_time(start_date,end_date, values):
    res=[]
    for i in values:
        elem_date=datetime.strptime(i["time"], '%Y-%m-%d %H:%M:%S')
        if(elem_date>=start_date and elem_date<=end_date):
            print('\n'+'correcto'+'fecha inicio: '+start_date.strftime("%m/%d/%Y, %H:%M:%S")+' fecha de final: '+end_date.strftime("%m/%d/%Y, %H:%M:%S")+' fecha de prueba: '+elem_date.strftime("%m/%d/%Y, %H:%M:%S"))
            res.append(i)
        else:
            print('\n'+'incorrecto'+'fecha inicio: '+start_date.strftime("%m/%d/%Y, %H:%M:%S")+' fecha de final: '+end_date.strftime("%m/%d/%Y, %H:%M:%S")+' fecha de prueba: '+elem_date.strftime("%m/%d/%Y, %H:%M:%S"))
    return res
    

# Creating layouts for every possible screen
layout1 = [ [sg.Text('Introduce the .csv file to be analyzed'), sg.FileBrowse(key='-FILE_PATH-')],
            [sg.CalendarButton("From", close_when_date_chosen=True,  target='-FROM-', location=(0,0), no_titlebar=False ), sg.Input(key='-FROM-', size=(20,1))],
            [sg.CalendarButton("To", close_when_date_chosen=True,  target='-TO-', location=(0,0), no_titlebar=False ), sg.Input(key='-TO-', size=(20,1))],
            [sg.Radio('Bluetooth Classic', group_id=1, default=True), sg.Radio('Bluetooth Low Energy', group_id=1)],            
            [sg.Button('Analyze'), sg.Button('Clear')] ]

layout2 = [ [sg.Text('Successful change')]]

# Organizing all the layouts
layout = [  [sg.Column(layout1, key='COL1'),
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
        csv_address = values["-FILE_PATH-"]
        csv_values=convert_csv_array(csv_address)
        print(csv_values[0])
        dict_values=[]
        for i in csv_values:
            dict_element={"order":i[0],"time":i[1].split('.')[0],"source":i[2],"destination":i[3], "type":i[4], "code":i[5], "description":i[6]}
            dict_values.append(dict_element)
        datetime_from = datetime.strptime(values["-FROM-"], '%Y-%m-%d %H:%M:%S')
        datetime_to = datetime.strptime(values["-TO-"], '%Y-%m-%d %H:%M:%S')
        datetime_test = datetime.strptime(dict_values[0]["time"], '%Y-%m-%d %H:%M:%S')
        dict_values_timed=filter_by_time(datetime_from,datetime_to,dict_values)

        print(dict_values)
        print(datetime_test)
        print("\n \n")
        print(dict_values_timed)

        col2.update(visible=True)
        col1.update(visible=False)

window.close()
