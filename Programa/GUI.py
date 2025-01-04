#!/home/hector/Desktop/Bluetooth/Blueprobe/Programa/Blueprobe/bin/python3

# import sys

# modulename = 'PySimpleGUI'
# if modulename not in sys.modules:
#     print ('You have not imported the' +modulename+ 'module')

import PySimpleGUI as sg
import csv, os, json
import array
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
        elem_date=datetime.strptime(i[1], '%Y-%m-%d %H:%M:%S')
        if(elem_date>=start_date and elem_date<=end_date):
            #print('\n'+'correcto'+'fecha inicio: '+start_date.strftime("%m/%d/%Y, %H:%M:%S")+' fecha de final: '+end_date.strftime("%m/%d/%Y, %H:%M:%S")+' fecha de prueba: '+elem_date.strftime("%m/%d/%Y, %H:%M:%S"))
            res.append(i)
        elif(elem_date>end_date):
            break
        #else:
            #print('\n'+'incorrecto'+'fecha inicio: '+start_date.strftime("%m/%d/%Y, %H:%M:%S")+' fecha de final: '+end_date.strftime("%m/%d/%Y, %H:%M:%S")+' fecha de prueba: '+elem_date.strftime("%m/%d/%Y, %H:%M:%S"))
    return res

def find_protocols(values_timed):
    res={}
    for i in values_timed:
        if not  i[4] in res:
            res[i[4]]=[]
    return res

def format_packets(values_timed,protocols_list):
    for i in values_timed:
        current_protocol=i[4]
        match current_protocol:
            case 'HCI_CMD':
                protocols_list[i[4]].append({"order":i[0],"time":i[1], "OGF":i[7],"OCF":i[8],"Bytes":i[9]})
            case 'HCI_EVT':
                protocols_list[i[4]].append({"order":i[0],"time":i[1], "Code":i[10], "Command_Opcode":i[11]})
            case 'L2CAP':
                protocols_list[i[4]].append({"order":i[0],"time":i[1], "source":i[2],"destination":i[3], "CID":i[12], "Opcode":i[13]})
            case 'RFCOMM':
                protocols_list[i[4]].append({"order":i[0],"time":i[1], "source":i[2],"destination":i[3], "CID":i[12], "DLCI":i[14], "Frame_Type":i[15],"Opcode_MCC":i[16]})
            case 'AVCTP':
                protocols_list[i[4]].append({"order":i[0],"time":i[1], "source":i[2],"destination":i[3], "CID":i[12], "Transaction":i[17],"C/R":i[18]})
            case 'AVRCP':
                protocols_list[i[4]].append({"order":i[0],"time":i[1], "source":i[2],"destination":i[3], "CID":i[12], "Transaction":i[17],"C/R":i[18], "CType":i[19], "Opcode":i[20], "PUD_ID":i[21], "OpID":i[22]})
            case 'AVDTP':
                protocols_list[i[4]].append({"order":i[0],"time":i[1], "source":i[2],"destination":i[3], "CID":i[12], "Transaction":i[23], "MessageType":i[24], "Signal":i[25]})
            case 'SBC':
                protocols_list[i[4]].append({"order":i[0],"time":i[1], "source":i[2],"destination":i[3], "CID":i[12], "ACP_SEID":i[26],"INT_SEID":i[27], "DataSpeed":i[28]})
            case 'ATT':
                protocols_list[i[4]].append({"order":i[0],"time":i[1], "source":i[2],"destination":i[3],"Operation":i[29],"Handle":i[30],"Value":i[31]})
            case _:
                protocols_list[i[4]].append({"order":i[0],"time":i[1], "source":i[2],"destination":i[3],"protocol":i[4],"info":i[6]})



def find_filters(values_timed):
    res=[[],[], []]
    for i in values_timed:
        #print('importante '+i['source'])
        #print('importante '+i['destination'])
        if not i['source'] in res[0]:
            res[0].append(i['source'])
        if not  i['destination'] in res[1]:
            res[1].append(i['destination'])
        if not  i['protocol'] in res[2]:
            res[2].append(i['protocol'])
    return res

    

# Creating layouts for every possible screen
layout1 = [ [sg.Text('Introduce the .csv file to be analyzed', background_color='#0082FC'), sg.FileBrowse(key='-FILE_PATH-',button_color=('#FFFFFF','#0A3C91'))],
            [sg.CalendarButton("From", close_when_date_chosen=True,  target='-FROM-', location=(0,0), no_titlebar=False ), sg.Input(key='-FROM-', size=(20,1))],
            [sg.CalendarButton("To", close_when_date_chosen=True,  target='-TO-', location=(0,0), no_titlebar=False ), sg.Input(key='-TO-', size=(20,1))],
            [sg.Radio('Bluetooth Classic', group_id=1, default=True), sg.Radio('Bluetooth Low Energy', group_id=1)],            
            [sg.Button('Analyze'), sg.Button('Clear')] ]

layout2 = [ [sg.Text('Successful analysis.')],
            [sg.Text('Sources', background_color='#0082FC'),sg.Combo([''], key='-SOURCES-',size=((20,3)))],
            [sg.Text('Destinations', background_color='#0082FC'),sg.Combo([''], key='-DESTINATIONS-',size=((20,3)))],
            [sg.Text('Protocols', background_color='#0082FC'),sg.Combo([''], key='-PROTOCOLS-',size=((20,3)))],
            [sg.Button('Filter')]]

#layout3 = []



# Organizing all the layouts
layout = [  [sg.Column(layout1, key='COL1', background_color='#0082FC'),
            sg.Column(layout2, key='COL2', background_color='#0082FC',visible=False),sg.Sizegrip(background_color='#0082FC')]
        ]

# Create the Window
window = sg.Window('Window Title', layout, resizable=True, background_color='#0082FC')

col1, col2= window['COL1'], window['COL2']
#col1, col2, col3 = window['COL1'], window['COL2'], window['COL3']

# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED : # if user closes window or clicks cancel
        break
    elif event == 'Analyze' :
        csv_address = values["-FILE_PATH-"]
        csv_values=convert_csv_array(csv_address)
        print(csv_values[0])
        for i in range(len(csv_values)):
            csv_values[i][1]=csv_values[i][1].split('.')[0]
        datetime_from = datetime.strptime(values["-FROM-"], '%Y-%m-%d %H:%M:%S')
        datetime_to = datetime.strptime(values["-TO-"], '%Y-%m-%d %H:%M:%S')
        values_timed=filter_by_time(datetime_from,datetime_to,csv_values)
        protocols_list=find_protocols(values_timed)
        format_packets(values_timed,protocols_list)
        print(protocols_list)
        protocols = list(protocols_list.keys())
        # sources_element = window.find_element('-SOURCES-', silent_on_error=True)
        # destinations_element = window.find_element('-DESTINATIONS-', silent_on_error=True)
        # protocols_element = window.find_element('-PROTOCOLS-', silent_on_error=True)
        # sources_element.update(values=filters[0])
        # destinations_element.update(values=filters[1])
        # protocols_element.update(values=filters[2])

        #print(dict_values)
        #print(datetime_test)
        # print("\n \n")
        # print(dict_values_timed)

        # print('qpasó 0'+str(filters))
        # print('qpasó 1'+str(filters[0]))
        # print('qpasó 2'+str(filters[1]))
        # print('qpasó 3'+str(filters[2]))


        col2.update(visible=True)
        col1.update(visible=False)

    elif event == 'Filter' :
        print("que buena crack")
        # #col3.update(visible=True)
        # print("esta entrando")
        # col3_layout = []
        # for i in dict_values_timed:
        #     if i['protocol']==protocols_element.get():
        #         col3_layout.append([sg.Text("From "+ i['source']+ " to "+i['destination']+" at "+i['time']+" : "+i['description'])])
        # print(str(col3_layout))
        # col3 = sg.Column(col3_layout, key='COL3', scrollable=True, size=(1200, 800),background_color='#FFFFFF')
        # window.extend_layout(window, [[col3]])  # Add the new column
        # col3.update(visible=False)
        # col3.layout([[sg.Text("holabuenas")]])
        # col3.update(size=(20,3))
        # col3.update(visible=True)
        #window.refresh()
window.close()
