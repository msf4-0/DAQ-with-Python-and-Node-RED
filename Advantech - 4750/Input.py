#!/usr/bin/python
# -*- coding:utf-8 -*-


"""
/*******************************************************************************
Copyright (c) 1983-2021 Advantech Co., Ltd.
********************************************************************************
THIS IS AN UNPUBLISHED WORK CONTAINING CONFIDENTIAL AND PROPRIETARY INFORMATION
WHICH IS THE PROPERTY OF ADVANTECH CORP., ANY DISCLOSURE, USE, OR REPRODUCTION,
WITHOUT WRITTEN AUTHORIZATION FROM ADVANTECH CORP., IS STRICTLY PROHIBITED. 

================================================================================
REVISION HISTORY
--------------------------------------------------------------------------------
$Log:  $

--------------------------------------------------------------------------------
$NoKeywords:  $
*/
/******************************************************************************
*
* Windows Example:
*    StaticDI.py
*
* Example Category:
*    DIO
*
* Description:
*    This example demonstrates how to use Static DI function.
*
* Instructions for Running:
*    1. Set the 'deviceDescription' for opening the device. 
*    2. Set the 'profilePath' to save the profile path of being initialized device. 
*    3. Set the 'startPort' as the first port for Di scanning.
*    4. Set the 'portCount' to decide how many sequential ports to operate Di scanning.
*
* I/O Connections Overview:
*    Please refer to your hardware reference manual.
*
******************************************************************************/
"""
import sys
sys.path.append('..')
from CommonUtils import kbhit
import time

from Automation.BDaq import *
from Automation.BDaq.InstantDiCtrl import InstantDiCtrl 
from Automation.BDaq.BDaqApi import AdxEnumToString, BioFailed

import random

from paho.mqtt import client as mqtt_client

broker = 'localhost'
port = 1883
topic = "PORT1"
topic_1 = "PORT2"
reverse_invert = "INVERT1"
reverse_invert1 = "INVERT2"

deviceDescription = "USB-4750,BID#0"
profilePath = u"..\\..\\profile\\USB_4750.xml"
startPort = 0
portCount = 2



def AdvInstantDI():
    ret = ErrorCode.Success

    # Step 1: Create a 'InstantDiCtrl' for DI function.
    # Select a device by device number or device description and specify the access mode.
    # In this example we use ModeWrite mode so that we can fully control the device,
    # including configuring, sampling, etc.
    instantDiCtrl = InstantDiCtrl(deviceDescription)

    for _ in range(1):
            instantDiCtrl.loadProfile = profilePath


        # Step 2: Read DI ports' status and show.
            print("Reading ports status is in progress, any key to quit!")

            def connect_mqtt():
                def on_connect(client, userdata, flags, rc):
                    if rc == 0:
                        print("Connected to MQTT Broker!")
                    else:
                        print("Failed to connect, return code %d\n", rc)

                client = mqtt_client.Client()
                client.on_connect = on_connect
                client.connect(broker, port)
                return client   

            def reverse_binary_string(s):
                 # Convert the string to a list of characters
                char_list = list(s)

                 # Reverse the list
                char_list.reverse()

                 # Join the list back into a string and return it
                return ''.join(char_list)
                
            while not kbhit():
                def publish(client):
                    msg_count = 0
                    while True:
                        time.sleep(1)
                        ret, data = instantDiCtrl.readAny(startPort, portCount)
                        if BioFailed(ret):
                            break

                        for i in range(startPort, startPort + portCount):
                            print("DI port %d status is %#x" % (i, data[i-startPort]))
                        
                        msg_1 = data[startPort]
                        msg_1 = '{0:08b}'.format(msg_1) 
                        msg = msg_1
                        binary_string = msg
                        reversed_string = reverse_binary_string(binary_string)
                        invert_1 = reversed_string 

                        

                        msg_2 = data[i-startPort]
                        print(type([i-startPort]))
                        msg_2 = '{0:08b}'.format(msg_2) 
                        binary_string_1 = msg_2
                        reversed_string_1 = reverse_binary_string(binary_string_1)
                        invert_2 = reversed_string_1 
                                               
                        
                        
                        
                    
                        result = client.publish(topic, msg)
                        # result: [0, 1]
                        status = result[0]
                        if status == 0:
                            print(f"Send `{msg}` to topic `{topic}`")
                        else:
                            print(f"Failed to send message to topic {topic}")

                        
                        result = client.publish(topic_1, msg_2)
                        # result: [0, 1]
                        status = result[0]
                        if status == 0:
                            print(f"Send `{msg_2}` to topic `{topic_1}`")
                        else:
                            print(f"Failed to send message to topic {topic_1}")    

                        result = client.publish(reverse_invert, invert_1)
                        # result: [0, 1]
                        status = result[0]
                        if status == 0:
                            print(f"Send `{invert_1}` to topic `{reverse_invert}`")
                        else:
                            print(f"Failed to send message to topic {reverse_invert}")    

                        result = client.publish(reverse_invert1, invert_2)
                        # result: [0, 1]
                        status = result[0]
                        if status == 0:
                            print(f"Send `{invert_2}` to topic `{reverse_invert1}`")
                        else:
                            print(f"Failed to send message to topic {reverse_invert1}")    
                        

                        msg_count += 1
                        time.sleep(1)

    def run():
        client = connect_mqtt()
        client.loop_start()
        publish(client)

    if __name__ == '__main__':
        run()
        
# Step 3: Close device and release any allocated resource
    instantDiCtrl.dispose()

    # If something wrong in this execution, print the error code on screen for tracking.
    if BioFailed(ret):
        enumStr = AdxEnumToString("ErrorCode", ret.value, 256)
        print("Some error occurred. And the last error code is %#x. [%s]" % (ret.value, enumStr))

    return 0

if __name__ == '__main__':
    mainData = AdvInstantDI()
    