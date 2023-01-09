#!/usr/bin/python
# -*- coding:utf-8 -*-

from paho.mqtt import client as mqtt_client
broker = 'localhost'
port = 1883
topic = "DAQ/DO"
MSG = ""

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
*    StaticDO.py
*
* Example Category:
*    DIO
*
* Description:
*    This example demonstrates how to use Static DO function.
*
* Instructions for Running:
*    1. Set the 'deviceDescription' for opening the device.
*    2. Set the 'profilePath' to save the profile path of being initialized device.
*    3. Set the 'startPort'as the first port for Do .
*    4. Set the 'portCount'to decide how many sequential ports to operate Do.
*
* I/O Connections Overview:
*    Please refer to your hardware reference manual.
*
******************************************************************************/
"""
import sys
sys.path.append('..')

from Automation.BDaq import *
from Automation.BDaq.InstantDoCtrl import InstantDoCtrl
from Automation.BDaq.BDaqApi import AdxEnumToString, BioFailed

deviceDescription = "USB-4750,BID#0"
profilePath = u"..\\..\\profile\\DemoDevice.xml"
startPort = 0
portCount = 1


def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client('')
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def subscribe(client: mqtt_client,deviceDescription):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        temp(deviceDescription,msg.payload)

    client.subscribe(topic)
    client.on_message = on_message

def run(instantDoCtrl):
    client = connect_mqtt()
    subscribe(client,instantDoCtrl)
    client.loop_forever()






def AdvInstantDO(deviceDescription):

    ret = ErrorCode.Success

    # Step 1: Create a instantDoCtrl for DO function.
    # Select a device by device number or device description and specify the access mode.
    # In this example we use ModeWrite mode so that we can fully control the device,
    # including configuring, sampling, etc.
    
    run(deviceDescription)



def temp(deviceDescription,msg):
    instantDoCtrl = InstantDoCtrl(deviceDescription)

    for _ in range(1):
        instantDoCtrl.loadProfile = profilePath
        print(msg)

        # Step 2: Write DO ports
        dataBuffer = [0] * portCount
        for i in range(startPort, portCount + startPort):
            # inputVal = input("Input a 16 hex number for D0 port %d to output(for example, 0x00): " % i)
            inputVal = msg
            if not isinstance(inputVal, int):
                inputVal = int(inputVal, 16)

            dataBuffer[i-startPort] = inputVal

        ret = instantDoCtrl.writeAny(startPort, portCount, dataBuffer)
        if BioFailed(ret):
            break
            print("DO output completed!")

        # Step 3: Close device and release any allocated resource.
        instantDoCtrl.dispose()

        # If something wrong in this execution, print the error code on screen for tracking.
        if BioFailed(ret):
            enumStr = AdxEnumToString("ErrorCode", ret.value, 256)
            print("Some error occurred. And the last error code is %#x. [%s]" % (ret.value, enumStr))

        return 0


if __name__ == "__main__":
    AdvInstantDO(deviceDescription)
