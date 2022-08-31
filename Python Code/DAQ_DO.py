# Library
import streamlit as st
import paho.mqtt.client as mqtt
from streamlit.script_run_context import add_script_run_ctx
import time
import sys
sys.path.append('..')

from Automation.BDaq import *
from Automation.BDaq.InstantDoCtrl import InstantDoCtrl
from Automation.BDaq.BDaqApi import AdxEnumToString, BioFailed

# Device parameters
deviceDescription = "USB-5856,BID#0"
profilePath = u"..\\..\\profile\\DemoDevice.xml"
startPort = 0
portCount = 4

# Streamlit container
mainCon = st.container()
textCon = st.container()

# Variables
if 'temp1' not in st.session_state:
    st.session_state.temp1 = st.empty()

if 'inputVal' not in st.session_state:
    st.session_state.inputVal = "00000000000000000000000000000000"

# MQTT Callbacks
def on_connect(client,userdata,flags,rc):
    """
    on_connect callback; when connected to a broker, subscribe to the desired topic
    """
    print("Connected with result code " + str(rc))
    # rc code meaning:
    #   0: Connection successful
    #   1: Connection refused – incorrect protocol version
    #   2: Connection refused – invalid client identifier
    #   3: Connection refused – server unavailable
    #   4: Connection refused – bad username or password
    #   5: Connection refused – not authorised
    #   6-255: Currently unused.
    client.subscribe("DAQ/DO", qos=2)

def on_message(client,userdata,msg):
    """
    on_message callback; when a publish message is received from the server, assign the payload to the message variable.
    """
    # When a messgae received, assign the value to the session state variable
    st.session_state.inputVal = msg.payload.decode("UTF-8")

# To execute the DO (Digital Output)
def AdvInstantDO():
    ret = ErrorCode.Success

    # Step 1: Create a instantDoCtrl for DO function.
    # Select a device by device number or device description and specify the access mode.
    # In this example we use ModeWrite mode so that we can fully control the device,
    # including configuring, sampling, etc.
    instantDoCtrl = InstantDoCtrl(deviceDescription)

    # Launch button
    st.session_state.launchButton = mainCon.checkbox("launch", value=False)
    
    #MQTT client
    client = mqtt.Client()

    # Create a MQTT client, connect to the desired broker, and start the loop
    try:
        client.connect("localhost", 1883)
    except:
        st.warning("Couldn't find the broker!")

    client.on_connect = on_connect
    client.on_message = on_message
    client.loop_start()
    add_script_run_ctx(client._thread)

    for _ in range(1):
        instantDoCtrl.loadProfile = profilePath

        # Step 2: Write DO ports
        dataBuffer = [0] * portCount

        while st.session_state.launchButton:
            # To avoid the error when dealing with while loop in streamlit
            with st.session_state.temp1.container():
                st.write("")
                time.sleep(0.1)
            st.session_state.temp1.empty()

            # To assign the values to each port (in this case, there are 4 ports with 8 channels each)
            for i in range(startPort, portCount + startPort):
                portValue = st.session_state.inputVal[(24-(i*8)):(40-((i*8)+8))]
                portValue = int(portValue, 2)
                dataBuffer[i-startPort] = portValue

            ret = instantDoCtrl.writeAny(startPort, portCount, dataBuffer)
            if BioFailed(ret):
                break
        
        print("DO output completed!")

    # Step 3: Close device and release any allocated resource.
    instantDoCtrl.dispose()
    
    # Close the MQTT loop and dissconnect
    client.loop_stop()
    client.disconnect()

    # If something wrong in this execution, print the error code on screen for tracking.
    if BioFailed(ret):
        enumStr = AdxEnumToString("ErrorCode", ret.value, 256)
        print("Some error occurred. And the last error code is %#x. [%s]" % (ret.value, enumStr))

    return 0

if __name__ == "__main__":
    AdvInstantDO()