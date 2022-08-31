import sys
import time
from Automation.BDaq import *
from Automation.BDaq.InstantDiCtrl import InstantDiCtrl
from Automation.BDaq.BDaqApi import AdxEnumToString, BioFailed

import pandas as pd
import streamlit as st
import paho.mqtt.client as mqtt

sys.path.append('..')

st.set_page_config(layout="wide")

# Initialize session state variables
if 'var1' not in st.session_state:
    st.session_state.var1 = 0
if 'greenCircle' not in st.session_state:
    st.session_state.greenCircle = "http://clipart-library.com/new_gallery/circle-clipart-26.png"
if 'redCircle' not in st.session_state:
    st.session_state.redCircle = "https://i.im.ge/2022/08/23/OiRaYY.circle.png"
if 'deviceDescription' not in st.session_state:
    # st.session_state.deviceDescription = "USB-5856,BID#0"
    st.session_state.deviceDescription = "DemoDevice,BID#0"
if 'profilePath' not in st.session_state:
    st.session_state.profilePath = u"..\\..\\profile\\DemoDevice.xml"
if 'startPort' not in st.session_state:
    st.session_state.startPort = 0
if 'portCount' not in st.session_state:
    st.session_state.portCount = 4
if 'nBit' not in st.session_state:
    st.session_state.nBit = 32
if 'nums' not in st.session_state:
    nums = []
    for i in range(8): 
        nums.append([])
        nums[i].append(i)
        nums[i].append(0)
    st.session_state.nums = nums
if 'stat' not in st.session_state:
    stat = []
    for i in range(8):
        stat.append(st.session_state.redCircle)
    st.session_state.stat = stat
if 'dfName' not in st.session_state:
    dfName = ["col1", "col2", "col3", "col4"]
    st.session_state.df = {}
    nums = st.session_state.nums
    for name in dfName:
        for i in range(8):
            nums[i][0] = (i + (8*(dfName.index(name))))
        st.session_state.df[name] = pd.DataFrame(nums)
        st.session_state.df[name].columns = ["Port", "DI"]
        st.session_state.df[name]["Stat"] = st.session_state.stat
    st.session_state.dfName = dfName

# To get the binary value
getbinary = lambda x, nBit: format(x, 'b').zfill(nBit)

if 'completion' not in st.session_state:
    st.session_state.completion = False

# Containers
container1 = st.container()
col = st.columns(4)

# Page title
container1.title("Read Input Test")

# HTML format for the images
def path_to_image_html(path):
    return '<img src="' + path + '" width="10" >'

def AdvInstantDI():
    ret = ErrorCode.Success

    # Step 1: Create a 'InstantDiCtrl' for DI function.
    # Select a device by device number or device description and specify the access mode.
    # In this example we use ModeWrite mode so that we can fully control the device,
    # including configuring, sampling, etc.
    instantDiCtrl = InstantDiCtrl(st.session_state.deviceDescription)
    for _ in range(1):
        instantDiCtrl.loadProfile = st.session_state.profilePath

        # Step 2: Read DI ports' status and show.
        with container1:
            st.session_state.readInput = st.checkbox("test1")
        
        # If the checkbox is checked, read the digital input and send to node red using MQTT
        if st.session_state.readInput:
            st.session_state.completion = True
            ret, data = instantDiCtrl.readAny(st.session_state.startPort, st.session_state.portCount)
            st.write(data[st.session_state.startPort])
            st.write("%#x" % data[st.session_state.startPort])
            for i in range(st.session_state.startPort, st.session_state.startPort + st.session_state.portCount):
                if i == 0:
                    st.session_state.bNum = getbinary(data[i - st.session_state.startPort], 8)[::-1]
                else:
                    st.session_state.bNum = st.session_state.bNum + getbinary(data[i - st.session_state.startPort], 8)[::-1]
            st.write(st.session_state.bNum)
            if BioFailed(ret):
                break
            
            for bitIndex in range(st.session_state.nBit):
                client = mqtt.Client()
                client.connect("localhost",1883,60)
                client.publish("DAQ/DI", st.session_state.bNum)
                time.sleep(0.01)
                client.disconnect()

                def updateValue(bitIndex, newBitIndex, index):
                    if st.session_state.bNum[bitIndex] == "1":
                        st.session_state.df[st.session_state.dfName[index]]["DI"][newBitIndex] = 1
                        st.session_state.df[st.session_state.dfName[index]]["Stat"][newBitIndex] = st.session_state.greenCircle
                    else:
                        st.session_state.df[st.session_state.dfName[index]]["DI"][newBitIndex] = 0
                        st.session_state.df[st.session_state.dfName[index]]["Stat"][newBitIndex] = st.session_state.redCircle

                if  0 <= bitIndex <= 7:
                    newBitIndex = bitIndex - 0
                    updateValue(bitIndex, newBitIndex, 0)
                if 8 <= bitIndex <= 15:
                    newBitIndex = bitIndex - 8
                    updateValue(bitIndex, newBitIndex, 1)
                if 16 <= bitIndex <= 23:
                    newBitIndex = bitIndex - 16
                    updateValue(bitIndex, newBitIndex, 2)
                if 24 <= bitIndex <= 31:
                    newBitIndex = bitIndex - 24
                    updateValue(bitIndex, newBitIndex, 3)

            for cNum in range(4):
                col[cNum].markdown(
                    st.session_state.df[st.session_state.dfName[cNum]].to_html(escape=False, formatters=dict(Stat=path_to_image_html)),
                    unsafe_allow_html=True,
                    )

            time.sleep(0.05)
            st.experimental_rerun()

        if st.session_state.completion:
            st.write("\n DI output completed !")
            st.session_state.completion = False

    # Step 3: Close device and release any allocated resource
    instantDiCtrl.dispose()

    # If something wrong in this execution, print the error code on screen for tracking.
    if BioFailed(ret):
        enumStr = AdxEnumToString("ErrorCode", ret.value, 256)
        print("Some error occurred. And the last error code is %#x. [%s]" % (ret.value, enumStr))
    return 0

if __name__ == '__main__':
    AdvInstantDI()