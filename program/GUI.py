#!/home/hector/Desktop/Bluetooth/Blueprobe/program/Blueprobe/bin/python3

import PySimpleGUI as sg
import csv
from datetime import datetime
import webbrowser

#Constants

#Common commands between Classic and LE
Classic_BLE_Common_Comm=[0x0009,0x0011, 0x0013, 0x0001, 0x0003, 0x0001, 0x001A, 0x0006, 0x002A, 0x0005, 0x0002, 0x0026, 0x0024, 0x0023, 0x0025, 0x000C, 0x0022, 0x0021, 0x0030, 0x0005, 0x0019, 0x000D, 0x0030, 0x0029, 0x0027, 0x0023, 0x0024, 0x0031, 0x0032, 0x0033, 0x0034, 0x0035]
#Common events between Classic and LE
Classic_BLE_Common_Ev=[0x0E, 0x0F, 0x1D, 0x05, 0x08, 0x30, 0x13, 0x1A, 0x03]
#Implemented protocols
Supported_Protocols=["HCI_CMD", "HCI_EVT", "L2CAP", "RFCOMM", "AVCTP", "AVRCP","AVDTP","SBC", "ATT", "SMP"]

#Auxiliary functions

#To create a dictionary from a file address.
def convert_csv_array(csv_address):
    file = open(csv_address,encoding='unicode_escape')
    csv_reader = csv.reader(file)
    header = next(csv_reader)
    rows = []
    for row in csv_reader:
        rows.append(row)
    file.close()
    return rows

#To filter the information about the data frames by time.
def filter_by_time(start_date,end_date, values):
    res=[]
    for i in values:
        elem_date=datetime.strptime(i[1], '%Y-%m-%d %H:%M:%S')
        if(elem_date>=start_date and elem_date<=end_date):
            res.append(i)
        elif(elem_date>end_date):
            break
    return res

#To create a dictionary with every protocol and an empty list associated to each of them.
def find_protocols(values_timed):
    res={}
    for i in values_timed:
        if not  i[4] in res:
            res[i[4]]=[]
    return res

#To select and storage the data fiels of interest for each data frame depending on the protocol. Only performs the formatting for Classic protocols.
def format_packets_Classic(values_timed,protocols_list):
    for i in values_timed:
        current_protocol=i[4]
        match current_protocol:
            case 'HCI_CMD':
                if not i[7]=="LE Controller Commands":
                    protocols_list[i[4]].append({"order":i[0],"time":i[1], "OGF":i[7],"OCF":i[8],"Bytes":i[9]})
            case 'HCI_EVT':
                if not "LE" in i[10]:
                    protocols_list[i[4]].append({"order":i[0],"time":i[1], "Code":i[10], "Sub Event":i[11],"Command_Opcode":i[12]})
            case 'L2CAP':
                protocols_list[i[4]].append({"order":i[0],"time":i[1], "source":i[2],"destination":i[3], "CID":i[14], "Opcode":i[15]})
            case 'RFCOMM':
                protocols_list[i[4]].append({"order":i[0],"time":i[1], "source":i[2],"destination":i[3], "CID":i[14], "DLCI":i[16], "Frame_Type":i[17],"Opcode_MCC":i[18]})
            case 'AVCTP':
                protocols_list[i[4]].append({"order":i[0],"time":i[1], "source":i[2],"destination":i[3], "CID":i[14], "Transaction":i[19],"C/R":i[20]})
            case 'AVRCP':
                protocols_list[i[4]].append({"order":i[0],"time":i[1], "source":i[2],"destination":i[3], "info":i[6],"CID":i[14], "Transaction":i[19],"C/R":i[20], "CType":i[21], "Opcode":i[22], "PUD_ID":i[23], "OpID":i[24]})
            case 'AVDTP':
                protocols_list[i[4]].append({"order":i[0],"time":i[1], "source":i[2],"destination":i[3], "info":i[6],"CID":i[14], "Transaction":i[25], "MessageType":i[26], "Signal":i[27]})
            case 'SBC':
                protocols_list[i[4]].append({"order":i[0],"time":i[1], "source":i[2],"destination":i[3], "CID":i[14], "ACP_SEID":i[28],"INT_SEID":i[29], "DataSpeed":i[30]})

#To select and storage the data fiels of interest for each data frame depending on the protocol. Only performs the formatting for Low Energy protocols.
def format_packets_LE(values_timed,protocols_list):
    for i in values_timed:
        current_protocol=i[4]
        match current_protocol:
            case 'HCI_CMD':
                hexCodeCMD=int(i[9][3:] + i[9][:2],16)&1023
                if hexCodeCMD in Classic_BLE_Common_Comm or i[7]=="LE Controller Commands":
                    protocols_list[i[4]].append({"order":i[0],"time":i[1], "OGF":i[7],"OCF":i[8]})
            case 'HCI_EVT':
                hexCodeEVT=int(i[13],16)
                if hexCodeEVT in Classic_BLE_Common_Ev or ("LE" in i[10]):
                    protocols_list[i[4]].append({"order":i[0],"time":i[1], "Code":i[10], "Sub Event":i[11],"Command_Opcode":i[12]})
            case 'L2CAP':
                protocols_list[i[4]].append({"order":i[0],"time":i[1], "source":i[2],"destination":i[3], "CID":i[14], "Opcode":i[15]})
            case 'ATT':
                protocols_list[i[4]].append({"order":i[0],"time":i[1], "source":i[2],"destination":i[3],"Operation":i[31],"Handle":i[32],"Value":i[33]})
            case 'SMP':
                protocols_list[i[4]].append({"order":i[0],"time":i[1], "source":i[2],"destination":i[3], "info":i[6], "Opcode":i[34]})

#To select and storage the data fiels of interest for each data frame depending on the protocol. Only performs the formatting for protocols that have not been implemented neither on the Classic nor in the LE mode.
def format_packets_Not_Implemented(values_timed, protocols_list):
    for i in values_timed:
        current_protocol=i[4]
        if current_protocol not in Supported_Protocols:
            protocols_list[i[4]].append({"order":i[0],"time":i[1], "source":i[2],"destination":i[3],"protocol":current_protocol,"info":i[6]})
        
#Establishes how the packets are presented depending on the protocol selected and adds the elements to the layout.
def present_packets(protocol_list,protocol,column,LE):
    counter=0
    match protocol:
            case 'HCI_CMD':
                for i in protocol_list:
                    column.append([sg.Text("Command from group  "+ i['OGF']+ " doing "+i['OCF']+" at "+i['time'],text_color="#000000",background_color='#FFFFFF',key="box"+str(counter))])
                    counter+=1  
            case 'HCI_EVT':
                for i in protocol_list:
                    if i['Sub Event']:
                        if "Connection Complete" in i['Sub Event']:
                            column.append([sg.Text("Event "+i['Code']+" with sub event "+i['Sub Event']+" took place at "+i['time'],text_color='#000000',background_color='#00FF00',key="box"+str(counter))])
                        if "Advertising Report" in i['Sub Event']:
                            column.append([sg.Text("Event "+i['Code']+" with sub event "+i['Sub Event']+" took place at "+i['time'],text_color='#000000',background_color='#FFDE21',key="box"+str(counter))])
                        else:
                            column.append([sg.Text("Event "+i['Code']+" with sub event "+i['Sub Event']+" took place at "+i['time'],text_color="#000000",background_color='#FFFFFF',key="box"+str(counter))])
                    else:
                        if "Connect Complete" in i['Code']:
                            column.append([sg.Text("Event "+i['Code']+" took place at "+i['time'],text_color='#000000',background_color='#00FF00',key="box"+str(counter))])
                        elif "Disconnect Complete" in i['Code']:
                            column.append([sg.Text("Event "+i['Code']+" took place at "+i['time'],text_color='#000000',background_color='#FF0000',key="box"+str(counter))])
                        elif "Inquiry Result" in i['Code']:
                            column.append([sg.Text("Event "+i['Code']+" took place at "+i['time'],text_color='#000000',background_color='#FFDE21',key="box"+str(counter))])
                        else:
                            column.append([sg.Text("Event "+i['Code']+" took place at "+i['time'],text_color="#000000",background_color='#FFFFFF',key="box"+str(counter))])
                    counter+=1
            case 'L2CAP':
                for i in protocol_list:
                    if not LE:
                        if i['CID']=='01:00':
                            column.append([sg.Text("Signaling channel "+ i['CID']+ " used at "+i['time']+" to execute command "+i['Opcode'],text_color="#00F900",background_color='#000000',key="box"+str(counter))])
                        else:
                            column.append([sg.Text("Channel "+ i['CID']+ " used at "+i['time'],text_color="#000000",background_color='#FFFFFF',key="box"+str(counter))])
                        counter+=1
                    else:
                        if i['CID']=='05:00':
                            column.append([sg.Text("Signaling channel "+ i['CID']+ " used at "+i['time']+" to execute command "+i['Opcode'],text_color="#00F900",background_color='#000000',key="box"+str(counter))])
                        else:
                            column.append([sg.Text("Channel "+ i['CID']+ " used at "+i['time'],text_color="#000000",background_color='#FFFFFF',key="box"+str(counter))])
                        counter+=1
            case 'RFCOMM':
                for i in protocol_list:
                    if i['DLCI']=='0x00' and i['Opcode_MCC']:
                        column.append([sg.Text("Using L2CAP channel "+ i['CID']+ " and control channel "+i['DLCI']+" with type frame "+i['Frame_Type']+" at "+i['time']+" to execute command "+i['Opcode_MCC'],text_color="#00F900",background_color='#000000',key="box"+str(counter))])
                    elif i['DLCI']=='0x00':
                        column.append([sg.Text("Using L2CAP channel "+ i['CID']+ " and control channel "+i['DLCI']+" with type frame "+i['Frame_Type']+" at "+i['time'],background_color='#000000',key="box"+str(counter))])
                    else:
                        column.append([sg.Text("Using L2CAP channel "+ i['CID']+ " and logical channel "+i['DLCI']+" with type frame "+i['Frame_Type']+" at "+i['time'],text_color="#000000",background_color='#FFFFFF',key="box"+str(counter))])
                    counter+=1
            case 'AVCTP':
                for i in protocol_list:
                    column.append([sg.Text("Using L2CAP channel "+ i['CID']+" in transaction "+i['Transaction']+" as "+i["C/R"]+" at "+i['time'],text_color="#000000",background_color='#FFFFFF',key="box"+str(counter))])
                    counter+=1
            case 'AVRCP':
                for i in protocol_list:
                    column.append([sg.Text("Using L2CAP channel "+ i['CID']+" in transaction "+i['Transaction']+" as "+i["C/R"]+" it happened "+i['info']+" at "+i['time'],text_color="#000000",background_color='#FFFFFF',key="box"+str(counter))])
                    counter+=1
            case 'AVDTP':
                for i in protocol_list:
                    column.append([sg.Text("Using L2CAP channel "+ i['CID']+" in transaction "+i['Transaction']+" as "+i["MessageType"]+" it happened "+i['info']+" at "+i['time'],text_color="#000000",background_color='#FFFFFF',key="box"+str(counter))])
                    counter+=1
            case 'SBC':
                for i in protocol_list:
                    column.append([sg.Text("Using L2CAP channel "+ i['CID']+" , ACP SEID "+i['ACP_SEID']+" and INT SEID "+i["INT_SEID"]+" at bit rate "+i['DataSpeed']+" at time "+i['time'],text_color="#000000",background_color='#FFFFFF',key="box"+str(counter))])
                    counter+=1
            case 'ATT':
                for i in protocol_list:
                    if "Write Command" in i['Operation']:
                        column.append([sg.Text("From "+ i['source']+ " to "+i['destination']+" at "+i['time']+" : doing "+i['Operation']+" with handle "+i['Handle']+" and value "+ i['Value'],text_color="#0018F9",background_color='#FFFFFF',key="box"+str(counter))])
                    elif "Value Notification" in i['Operation']:
                        column.append([sg.Text("From "+ i['source']+ " to "+i['destination']+" at "+i['time']+" : doing "+i['Operation']+" with handle "+i['Handle']+" and value "+ i['Value'],text_color="#B200ED",background_color='#FFFFFF',key="box"+str(counter))])
                    else:
                        column.append([sg.Text("From "+ i['source']+ " to "+i['destination']+" at "+i['time']+" : doing "+i['Operation']+" with handle "+i['Handle']+" and value "+ i['Value'],text_color="#000000",background_color='#FFFFFF',key="box"+str(counter))])
                    counter+=1
            case 'SMP':
                for i in protocol_list:
                    if i['Opcode']=="Pairing Request" or i['Opcode']=="Pairing Response":
                        column.append([sg.Text("From "+ i['source']+ " to "+i['destination']+" at "+i['time']+" : doing "+i['info'],text_color="#000000",background_color='#00FF00',key="box"+str(counter))])
                    else:
                        column.append([sg.Text("From "+ i['source']+ " to "+i['destination']+" at "+i['time']+" : doing "+i['Opcode'],text_color="#000000",background_color='#FFFFFF',key="box"+str(counter))])
                    counter+=1
            case _:
                for i in protocol_list:
                    column.append([sg.Text("From "+ i['source']+ " to "+i['destination']+" at "+i['time']+" : doing "+i['info'],text_color="#000000",background_color='#FFFFFF',key="box"+str(counter))])
                    counter+=1

    

# Creating layouts for every possible screen

# Main Screen 1
layout1 = [ [sg.Text('Introduce the .csv file to be analyzed', background_color='#0082FC'), sg.FileBrowse(key='-FILE_PATH-',button_color=('#FFFFFF','#0A3C91'))],
            [sg.CalendarButton("From", close_when_date_chosen=True,  target='-FROM-', location=(0,0), no_titlebar=False ), sg.Input(key='-FROM-', size=(20,1))],
            [sg.CalendarButton("To", close_when_date_chosen=True,  target='-TO-', location=(0,0), no_titlebar=False ), sg.Input(key='-TO-', size=(20,1))],
            [sg.Radio('Bluetooth Classic', background_color='#0082FC',group_id=1, default=True, key="Classic"), sg.Radio('Bluetooth Low Energy', background_color='#0082FC',group_id=1,key="BLE"),sg.Radio('Not implemented', background_color='#0082FC',group_id=1, key="NotImp")],            
            [sg.Button('Analyze')] ]

# Main Screen 2
layout2 = [ [sg.Text('Successful analysis.', background_color='#0082FC',key='AnalysisSuccess')],
            [sg.Text('Protocols', background_color='#0082FC'),sg.Combo([''], key='-PROTOCOLS-',size=((20,3)))],
            [sg.Button('Filter'),sg.Button('?',key='Help')]]

# Tabs layout for the main screen 2
tab1_layout = [[sg.Text("Contenido de la Pestaña 1")]]
tabs= [sg.Tab("Pestaña 1", tab1_layout, key="Tab1")]

# Layout for the LE Help secondary window
sec_layout_BLE=[[sg.Text('References to understand actions that have taken place for every protocol involved with BLE: ',background_color='#0082FC')],
                [sg.Button('HCI_CMD & HCI_EVT')],
                [sg.Button('L2CAP')],
                [sg.Button('ATT')],
                [sg.Button('SMP')]]

# Layout for the Classic Help secondary window
sec_layout_Classic=[[sg.Text('References to understand actions that have taken place for every protocol involved with Bluetooth Classic: ',background_color='#0082FC')],
                [sg.Button('HCI_CMD & HCI_EVT')],
                [sg.Button('L2CAP')],
                [sg.Button('RFCOMM'),sg.Text('Check section 4',font=('Helvetica', 12, 'bold italic'),background_color='#0082FC')],
                [sg.Button('AVCTP'), sg.Text('Check section 6',font=('Helvetica', 12, 'bold italic'),background_color='#0082FC')],
                [sg.Button('AVRCP'),sg.Text('PDF with specifications can be downloaded. Check section 6.',font=('Helvetica', 12, 'bold italic'),background_color='#0082FC')],
                [sg.Button('AVDTP'), sg.Text('PDF with specifications can be downloaded. Check section 6.',font=('Helvetica', 12, 'bold italic'),background_color='#0082FC')],
                [sg.Button('A2DP'), sg.Text('PDF with specifications can be downloaded. Check section 2.',font=('Helvetica', 12, 'bold italic'),background_color='#0082FC')]
            ]

# Organizing all the elements of the layout
layout = [  [sg.Column(layout1, key='COL1', background_color='#0082FC'),
            sg.Column(layout2, key='COL2', background_color='#0082FC',visible=False),sg.Sizegrip(background_color='#0082FC')],
            [sg.TabGroup([], key="TabGroup", title_color="#0082FC",selected_background_color="#283B5B", background_color='#0082FC',visible=True, enable_events=True)]
        ]

# Creating the main window
window = sg.Window('Window Title', layout, resizable=True, background_color='#0082FC')

# Establishing names for the elements in thw window
col1, col2, tabsGroup= window['COL1'], window['COL2'], window['TabGroup']

# Event Loop to process "events" and get the "values" of the inputs. Essentially, it allows us to perform an action when a button is pressed.
while True:
    event, values = window.read()
    # When the user closes the window, the loop is exited and the program ends
    if event == sg.WIN_CLOSED : 
        break
    # When the button "Analyze" is pressed, the files chosen, time filters and mode chosen are used to obtain, filter and format the data of interest
    # We switch from one screen to the next one
    elif event == 'Analyze' :
        csv_address = values["-FILE_PATH-"]
        csv_values=convert_csv_array(csv_address)
        for i in range(len(csv_values)):
            csv_values[i][1]=csv_values[i][1].split('.')[0]
        datetime_from = datetime.strptime(values["-FROM-"], '%Y-%m-%d %H:%M:%S')
        datetime_to = datetime.strptime(values["-TO-"], '%Y-%m-%d %H:%M:%S')
        values_timed=filter_by_time(datetime_from,datetime_to,csv_values)
        protocols_list=find_protocols(values_timed)
        if values["Classic"]:
            format_packets_Classic(values_timed,protocols_list)
        elif values["BLE"]:
            format_packets_LE(values_timed,protocols_list)
        else:
            format_packets_Not_Implemented(values_timed,protocols_list)
        for key in protocols_list.copy():
            if not protocols_list[key]:
                del protocols_list[key]
        protocols = list(protocols_list.keys())
        protocols_element = window.find_element('-PROTOCOLS-', silent_on_error=True)
        protocols_element.update(values=protocols)
        col2.update(visible=True)
        col1.update(visible=False)
        filterIter=0
        secondaryWindowCounter=0

    elif event == 'Filter' :
    #When the 'Filter' button is pressed, the information related to the protocol selected is presented in a new tab.
        window['AnalysisSuccess'].update(visible=False)
        selected_protocol=protocols_element.get()
        selected_protocol_list=protocols_list[selected_protocol]
        col3_layout = []
        if values['BLE']:
            present_packets(selected_protocol_list,selected_protocol,col3_layout,True)
        else:
            present_packets(selected_protocol_list,selected_protocol,col3_layout,False)
        
        col3 = sg.Column(col3_layout, key='COL3'+str(filterIter)+'-', scrollable=True, size=(1200, 800),background_color='#FFFFFF')
        newTab=sg.Tab("Filtering "+ str(filterIter+1), [[col3]], key='TAB'+str(filterIter))
        tabs.append(newTab)
        tabsGroup.add_tab(newTab)
        tabsGroup.update(visible=True)
        window.refresh()
        filterIter+=1

    elif event == 'Help':
    #When the '?' button is pressed, a secondary window is created to give useful resources to understand each protocol. 
    #Each button redirects us to a different webpage.
        if values['BLE']:
            #A new instance is created each time
            if secondaryWindowCounter>0:
                sec_layout_BLE=[[sg.Text('References to understand actions that have taken place for every protocol involved with BLE: ',background_color='#0082FC',key="helpTextBLE"+str(secondaryWindowCounter))],
                                [sg.Button('HCI_CMD & HCI_EVT',key='HCI_CMD & HCI_EVT'+str(secondaryWindowCounter))],
                                [sg.Button('L2CAP',key='L2CAP'+str(secondaryWindowCounter))],
                                [sg.Button('ATT',key='ATT'+str(secondaryWindowCounter))],
                                [sg.Button('SMP',key='SMP'+str(secondaryWindowCounter))]]

            window_secundaria = sg.Window("Ventana Secundaria", sec_layout_BLE,background_color='#0082FC', modal=True)

            # Loop for the secondary window of LE. Detects which button has been pressed to open a webpage related to the selected protocol.
            while True:
                event_secundaria, values_secundaria = window_secundaria.read()
                if event_secundaria == sg.WINDOW_CLOSED or event_secundaria == "Cerrar Ventana Secundaria":
                    break
                elif 'HCI_CMD & HCI_EVT' in event_secundaria:
                    webbrowser.open("https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/Core-54/out/en/host-controller-interface/host-controller-interface-functional-specification.html#UUID-5ab4cace-d0bc-38ea-2675-598d57905d3d")
                elif 'L2CAP' in event_secundaria:
                    webbrowser.open("https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/Core-54/out/en/host/logical-link-control-and-adaptation-protocol-specification.html#UUID-32a25a06-4aa4-c6c7-77c5-dcfe3682355d")
                elif 'ATT' in event_secundaria:
                    webbrowser.open("https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/Core-54/out/en/host/attribute-protocol--att-.html#UUID-44501232-7370-3ff0-be57-3d458b542a5b")
                elif 'SMP' in event_secundaria:
                    webbrowser.open("https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/Core-54/out/en/host/security-manager-specification.html#UUID-357f5fc6-5b55-6d33-e459-f42c929137f8")
            window_secundaria.close()
            secondaryWindowCounter+=1
        else:
            if secondaryWindowCounter>0:
                sec_layout_Classic=[[sg.Text('References to understand actions that have taken place for every protocol involved with Bluetooth Classic: ', background_color='#0082FC',key="helpTextClassic"+str(secondaryWindowCounter))],
                                [sg.Button('HCI_CMD & HCI_EVT',key='HCI_CMD & HCI_EVT'+str(secondaryWindowCounter))],
                                [sg.Button('L2CAP',key='L2CAP'+str(secondaryWindowCounter))],
                                [sg.Button('RFCOMM',key='RFCOMM'+str(secondaryWindowCounter)),sg.Text('Check section 4',font=('Helvetica', 12, 'bold italic'),background_color='#0082FC', key="helpTextRFCOMM"+str(secondaryWindowCounter))],
                                [sg.Button('AVCTP',key='AVCTP'+str(secondaryWindowCounter)), sg.Text('Check section 6',font=('Helvetica', 12, 'bold italic'),background_color='#0082FC',key="helpTextAVCTP"+str(secondaryWindowCounter))],
                                [sg.Button('AVRCP',key='AVRCP'+str(secondaryWindowCounter)),sg.Text('PDF with specifications can be downloaded. Check section 6.',font=('Helvetica', 12, 'bold italic'),background_color='#0082FC',key="helpTextAVRCP"+str(secondaryWindowCounter))],
                                [sg.Button('AVDTP',key='AVDTP'+str(secondaryWindowCounter)), sg.Text('PDF with specifications can be downloaded. Check section 6.',font=('Helvetica', 12, 'bold italic'),background_color='#0082FC',key="helpTextAVDTP"+str(secondaryWindowCounter))],
                                [sg.Button('A2DP',key='A2DP'+str(secondaryWindowCounter)), sg.Text('PDF with specifications can be downloaded. Check section 2.',font=('Helvetica', 12, 'bold italic'),background_color='#0082FC',key="helpTextA2DP"+str(secondaryWindowCounter))]
                            ]

            window_secundaria = sg.Window("Ventana Secundaria", sec_layout_Classic,background_color='#0082FC', modal=True)

            # Loop for the secondary window of Classic. Detects which button has been pressed to open a webpage related to the selected protocol.
            while True:
                event_secundaria, values_secundaria = window_secundaria.read()
                if event_secundaria == sg.WINDOW_CLOSED or event_secundaria == "Cerrar Ventana Secundaria":
                    break
                elif 'HCI_CMD & HCI_EVT' in event_secundaria:
                    webbrowser.open("https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/Core-54/out/en/host-controller-interface/host-controller-interface-functional-specification.html#UUID-5ab4cace-d0bc-38ea-2675-598d57905d3d")
                elif 'L2CAP' in event_secundaria:
                    webbrowser.open("https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/Core-54/out/en/host/logical-link-control-and-adaptation-protocol-specification.html#UUID-32a25a06-4aa4-c6c7-77c5-dcfe3682355d")
                elif 'RFCOMM' in event_secundaria:
                    webbrowser.open("https://www.bluetooth.com/specifications/specs/rfcomm-1-1-html/")
                elif 'AVCTP' in event_secundaria:
                    webbrowser.open("https://www.bluetooth.com/specifications/specs/avctp-1-4/")
                elif 'AVRCP' in event_secundaria:
                    webbrowser.open("https://www.bluetooth.com/specifications/specs/a-v-remote-control-profile-1-6-2/")
                elif 'AVDTP' in event_secundaria:
                    webbrowser.open("https://www.bluetooth.com/specifications/specs/a-v-distribution-transport-protocol-1-3/")
                elif 'A2DP' in event_secundaria:
                    webbrowser.open("https://www.bluetooth.com/specifications/specs/advanced-audio-distribution-profile-1-4/")
            window_secundaria.close()   
            secondaryWindowCounter+=1
window.close()
