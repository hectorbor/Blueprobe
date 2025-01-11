#!/home/hector/Desktop/Bluetooth/Blueprobe/Programa/Blueprobe/bin/python3

# import sys

# modulename = 'PySimpleGUI'
# if modulename not in sys.modules:
#     print ('You have not imported the' +modulename+ 'module')

import PySimpleGUI as sg
import csv, os, json
import array
from datetime import datetime

#Constants

Classic_BLE_Common_Comm=[0x0009,0x0011, 0x0013, 0x0001, 0x0003, 0x0001, 0x001A, 0x0006, 0x002A, 0x0005, 0x0002, 0x0026, 0x0024, 0x0023, 0x0025, 0x000C, 0x0022, 0x0021, 0x0030, 0x0005, 0x0019, 0x000D, 0x0030, 0x0029, 0x0027, 0x0023, 0x0024, 0x0031, 0x0032, 0x0033, 0x0034, 0x0035]
Classic_BLE_Common_Ev=[0x0E, 0x0F, 0x1D, 0x05, 0x08, 0x30, 0x13, 0x1A, 0x03]
Supported_Protocols=["HCI_CMD", "HCI_EVT", "L2CAP", "RFCOMM", "AVCTP", "AVRCP","AVDTP","SBC", "ATT"]

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

def format_packets_Classic(values_timed,protocols_list):
    for i in values_timed:
        current_protocol=i[4]
        match current_protocol:
            case 'HCI_CMD':
                if not i[7]=="LE Controller Commands":
                    protocols_list[i[4]].append({"order":i[0],"time":i[1], "OGF":i[7],"OCF":i[8],"Bytes":i[9]})
            case 'HCI_EVT':
                if not "LE" in i[10]:
                    protocols_list[i[4]].append({"order":i[0],"time":i[1], "Code":i[10], "Command_Opcode":i[11]})
            case 'L2CAP':
                protocols_list[i[4]].append({"order":i[0],"time":i[1], "source":i[2],"destination":i[3], "CID":i[13], "Opcode":i[14]})
            case 'RFCOMM':
                protocols_list[i[4]].append({"order":i[0],"time":i[1], "source":i[2],"destination":i[3], "CID":i[13], "DLCI":i[15], "Frame_Type":i[16],"Opcode_MCC":i[17]})
            case 'AVCTP':
                protocols_list[i[4]].append({"order":i[0],"time":i[1], "source":i[2],"destination":i[3], "CID":i[13], "Transaction":i[18],"C/R":i[19]})
            case 'AVRCP':
                protocols_list[i[4]].append({"order":i[0],"time":i[1], "source":i[2],"destination":i[3], "info":i[6],"CID":i[13], "Transaction":i[18],"C/R":i[19], "CType":i[20], "Opcode":i[21], "PUD_ID":i[22], "OpID":i[23]})
            case 'AVDTP':
                protocols_list[i[4]].append({"order":i[0],"time":i[1], "source":i[2],"destination":i[3], "info":i[6],"CID":i[13], "Transaction":i[24], "MessageType":i[25], "Signal":i[26]})
            case 'SBC':
                protocols_list[i[4]].append({"order":i[0],"time":i[1], "source":i[2],"destination":i[3], "CID":i[13], "ACP_SEID":i[27],"INT_SEID":i[28], "DataSpeed":i[29]})

def format_packets_LE(values_timed,protocols_list):
    for i in values_timed:
        current_protocol=i[4]
        match current_protocol:
            case 'HCI_CMD':
                #"Bytes":i[9]
                hexCodeCMD=int(i[9][3:] + i[9][:2],16)&1023
                if hexCodeCMD in Classic_BLE_Common_Comm or i[7]=="LE Controller Commands":
                    protocols_list[i[4]].append({"order":i[0],"time":i[1], "OGF":i[7],"OCF":i[8]})
            case 'HCI_EVT':
                hexCodeEVT=int(i[12],16)
                if hexCodeEVT in Classic_BLE_Common_Ev or ("LE" in i[10]):
                    protocols_list[i[4]].append({"order":i[0],"time":i[1], "Code":i[10], "Command_Opcode":i[11]})
            case 'L2CAP':
                protocols_list[i[4]].append({"order":i[0],"time":i[1], "source":i[2],"destination":i[3], "CID":i[13], "Opcode":i[14]})
            case 'ATT':
                protocols_list[i[4]].append({"order":i[0],"time":i[1], "source":i[2],"destination":i[3],"Operation":i[30],"Handle":i[31],"Value":i[32]})

def format_packets_Not_Implemented(values_timed, protocols_list):
    for i in values_timed:
        current_protocol=i[4]
        if current_protocol not in Supported_Protocols:
            protocols_list[i[4]].append({"order":i[0],"time":i[1], "source":i[2],"destination":i[3],"protocol":current_protocol,"info":i[6]})
        
def present_packets(protocol_list,protocol,column,LE):
    counter=0
    match protocol:
            case 'HCI_CMD':
                for i in protocol_list:
                    column.append([sg.Text("Command from group  "+ i['OGF']+ " doing "+i['OCF']+" at "+i['time']+"\n",key="box"+str(counter))])
                    counter+=1  
            case 'HCI_EVT':
                for i in protocol_list:
                    column.append([sg.Text("Event "+i['Code']+" performed at "+i['time'],key="box"+str(counter))])
                    counter+=1
            case 'L2CAP':
                for i in protocol_list:
                    if not LE:
                        if i['CID']=='01:00':
                            column.append([sg.Text("Signaling channel "+ i['CID']+ " used at "+i['time']+" to execute command "+i['Opcode'],key="box"+str(counter))])
                        else:
                            column.append([sg.Text("Channel "+ i['CID']+ " used at "+i['time'],key="box"+str(counter))])
                        counter+=1
                    else:
                        if i['CID']=='05:00':
                            column.append([sg.Text("Signaling channel "+ i['CID']+ " used at "+i['time']+" to execute command "+i['Opcode'],key="box"+str(counter))])
                        else:
                            column.append([sg.Text("Channel "+ i['CID']+ " used at "+i['time'],key="box"+str(counter))])
                        counter+=1
            case 'RFCOMM':
                for i in protocol_list:
                    column.append([sg.Text("Using L2CAP channel "+ i['CID']+ " and logical channel "+i['DLCI']+" with type frame "+i['Frame_Type']+" at "+i['time'],key="box"+str(counter))])
                    counter+=1
            case 'AVCTP':
                for i in protocol_list:
                    column.append([sg.Text("Using L2CAP channel "+ i['CID']+" in transaction "+i['Transaction']+" as "+i["C/R"]+" at "+i['time'],key="box"+str(counter))])
                    counter+=1
            case 'AVRCP':
                for i in protocol_list:
                    column.append([sg.Text("Using L2CAP channel "+ i['CID']+" in transaction "+i['Transaction']+" as "+i["C/R"]+" it happened "+i['info']+" at "+i['time'],key="box"+str(counter))])
                    counter+=1
            case 'AVDTP':
                for i in protocol_list:
                    column.append([sg.Text("Using L2CAP channel "+ i['CID']+" in transaction "+i['Transaction']+" as "+i["MessageType"]+" it happened "+i['info']+" at "+i['time'],key="box"+str(counter))])
                    counter+=1
            case 'SBC':
                for i in protocol_list:
                    column.append([sg.Text("Using L2CAP channel "+ i['CID']+" using ACP SEID "+i['ACP_SEID']+" and INT SEID "+i["INT_SEID"]+" at bit rate "+i['DataSpeed'],key="box"+str(counter))])
                    counter+=1
            case 'ATT':
                for i in protocol_list:
                    column.append([sg.Text("From "+ i['source']+ " to "+i['destination']+" at "+i['time']+" : doing "+i['Operation']+" with handle "+i['Handle'],key="box"+str(counter))])
                    counter+=1

    

# Creating layouts for every possible screen
layout1 = [ [sg.Text('Introduce the .csv file to be analyzed', background_color='#0082FC'), sg.FileBrowse(key='-FILE_PATH-',button_color=('#FFFFFF','#0A3C91'))],
            [sg.CalendarButton("From", close_when_date_chosen=True,  target='-FROM-', location=(0,0), no_titlebar=False ), sg.Input(key='-FROM-', size=(20,1))],
            [sg.CalendarButton("To", close_when_date_chosen=True,  target='-TO-', location=(0,0), no_titlebar=False ), sg.Input(key='-TO-', size=(20,1))],
            [sg.Radio('Bluetooth Classic', group_id=1, default=True, key="Classic"), sg.Radio('Bluetooth Low Energy', group_id=1,key="BLE"),sg.Radio('Not implemented', group_id=1, key="NotImp")],            
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
        print("aqui entra la primera vez: "+str(protocols_list))
        if values["Classic"]:
            format_packets_Classic(values_timed,protocols_list)
        elif values["BLE"]:
            format_packets_LE(values_timed,protocols_list)
        else:
            format_packets_Not_Implemented(values_timed,protocols_list)
        for key in protocols_list.copy():
            print(key)
            if not protocols_list[key]:
                del protocols_list[key]
        protocols = list(protocols_list.keys())
        print(protocols)
        protocols_element = window.find_element('-PROTOCOLS-', silent_on_error=True)
        protocols_element.update(values=protocols)
        col2.update(visible=True)
        col1.update(visible=False)
        filterIter=0

    elif event == 'Filter' :
        #col3.update(visible=True)
        if(filterIter!=0):
            if filterIter==1:
                protocols_elementAux = window.find_element('-PROTOCOLS-')
                selected_protocol=protocols_element.get()
                selected_protocol_list=protocols_list[selected_protocol]
            else:
                protocols_elementAux = window.find_element('-PROTOCOLS-'+str(filterIter-1)+'-')
                selected_protocol=protocols_element.get()
                selected_protocol_list=protocols_list[selected_protocol]
            window.close()
            layoutAux = [   [sg.Text('Sources', background_color='#0082FC'),sg.Combo([''], key='-SOURCES'+str(filterIter)+'-',size=((20,3)))],
                            [sg.Text('Destinations', background_color='#0082FC'),sg.Combo([''], key='-DESTINATIONS'+str(filterIter)+'-',size=((20,3)))],
                            [sg.Text('Protocols', background_color='#0082FC'),sg.Combo([''], key='-PROTOCOLS-'+str(filterIter)+'-',size=((20,3)))],
                            [sg.Button('Filter')]]
            window = sg.Window('Window Title', layoutAux, resizable=True, background_color='#0082FC')
            event, values =window.read()
            protocols_elementAux = window.find_element('-PROTOCOLS-'+str(filterIter)+'-')
            protocols_elementAux.update(values=protocols)
            window.refresh()
        else:
            selected_protocol=protocols_element.get()
            selected_protocol_list=protocols_list[selected_protocol]
        col3_layout = []
        #selected_protocol_list=protocols_list[selected_protocol]
        if values['BLE']:
            present_packets(selected_protocol_list,selected_protocol,col3_layout,True)
        else:
            present_packets(selected_protocol_list,selected_protocol,col3_layout,False)
        
        #print(str(col3_layout))
        col3 = sg.Column(col3_layout, key='COL3'+str(filterIter)+'-', scrollable=True, size=(1200, 800),background_color='#FFFFFF')
        window.extend_layout(window, [[col3]])  # Add the new column
        col3.update(visible=False)
        col3.update(visible=True)
        window.refresh()
        filterIter+=1
window.close()
