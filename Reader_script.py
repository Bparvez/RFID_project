#!/usr/bin/env python

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


# This code is for using an OOK on a temperature sensor

import io                  # importing python libraries
import sys
import serial              # for the timer and the duration of the loop
import time, threading     # for time stamping and threading
import numpy as np         # for the mean
import os
from Tkinter import *   # for the Gui

size_of_arrays = 10
size_of_pos_edges_array = 10
pos_array = list()   # array to store time stamped negative to positive edge/change values
neg_array = list()   # array to store time stamped positive to negative edge/change values , bot using it at the moment
frequency_array = list() # array to store the calculated frequency values
all_values_array = list() # array to store all the time stamps of the reading either 0 on non presence of the tag, or time stamp on tag presence
filtered_all_values_array = list() #array to store the time stamps values after filtering
wave_form = list()
n = 0  # int to terminate the loop after some number of times, and for the array
ID = 0 # initilize the global int ID to zero
prev_ID = 0 # Initialize the global int prev_ID to zero for comparing the positive to negative edge
first_time = 0 # to not make the detection for the first time
top = Tk()
text1 = Text(top, height=20, width=50) # for making the variable global
var = StringVar()
var.set('0')
Temperature = 0 # Initializing the global temperature to zero , for the gui

WINDOW_W = 500      # variables for our display window
WINDOW_H = 100

#LUT for frecuencty to temp conversion
t_array = [ -40, -35, -30, -25, -20, -15, -10, -5, 0, 5, 10, 15,  20,  25,  30, 35, 40, 45, 50, 55, 60,  65, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130, 135, 140, 145, 150]
f_array = [ 0.015, 0.020, 0.027, 0.035, 0.045, 0.058, 0.074, 0.093, 0.117, 0.145, 0.179, 0.219, 0.267, 0.323, 0.389, 0.466, 0.554, 0.656, 0.774, 0.908, 1.060, 1.233, 1.429, 1.649, 1.896, 2.172, 2.480, 2.822, 3.202, 3.621, 4.083, 4.593, 5.149, 5.764, 6.428, 7.154, 7.945, 8.787, 9.710]


#-------------------------------------------------------------------
# Function: main
# Description: The function creates a command to send through a
# serial line to TI S6350 RFID reader
#
#-------------------------------------------------------------------
def main():

    num_of_times = 100
    frequency = 0
    global size_of_arrays
    global n
    global pos_array, neg_array, filtered_all_values_array, all_values_array, wave_form
    global ID , prev_ID
    global first_time
    global frequency_array
    global Temperature

    ID = 0       # Initialize ID to zero for the next thread

    if len(sys.argv) < 2 :
        print ("Usage: " + sys.argv[0] + " serial_port_to_use")
        sys.exit()

    try:
        tiser = serial.Serial(sys.argv[1], baudrate=57600, bytesize=8,
            parity='N', stopbits=1, timeout=2, xonxoff=0, rtscts=0, dsrdtr=0)
    except:
        print ("Usage: " + sys.argv[0] + " serial_port_to_use")
        print ("Can't open " + sys.argv[1] + ".")
        print ("Under linux or Apple OS you need the full path, ie /dev/ttyUSB0.")
        print ("Under windows use the communication port name, ie COM8")
        sys.exit()

    read_transponder_details = [0x01, 0, 0, 0, 0, 0, 0x60]  # the ISO wrapper

    read_transponder_details.extend([0x11, 0x27, 0x01, 0])

    read_transponder_details.extend([0, 0])  # the two checksum bytes

    command_len = len(read_transponder_details)

    command = bytearray(command_len)
    idx = 0

    for i in read_transponder_details:
        command[idx] = i
        idx += 1

    # Fill in the length
    command[1] = command_len

    # Compute and fill in the two checksum bytes
    chksum = 0
    idx = 0
    while idx < (command_len - 2):
        chksum ^= command[idx]
        idx += 1

    command[command_len - 2] = chksum  # 1st byte is the checksum
    command[command_len - 1] = chksum ^ 0xff  # 2nd byte is ones comp of the checksum


    ### for GUI

    # for the top most Text
    canvas = Canvas(top, width=WINDOW_W, height=WINDOW_H)
    canvas.pack()
    text1.tag_configure('big', font=('Verdana', 20, 'bold'))
    text1.insert(END,'\nTemperature Sensor\n', 'big')
    text1.pack()

    # for the changing values
    l = Label(top, textvariable = var)
    l.pack()
    # top.mainloop()
    ### for the GUI

    #Continuos execution loop to calculate

    while(True):

        try:
            #wait to issue an new read
            time.sleep(0.125)

            # Send out the command to the reader
            tiser.write(memoryview(command))  # memoryview is the same as buffer

            line_size = tiser.read(2)  # first pass, read first two bytes of reply

            if len(line_size) < 2:
                print ("No data returned.  Is the reader turned on?")
                #tiser.close()
                #sys.exit()

            else:
                line_data = tiser.read((ord(line_size[1]) - 2))  # get the rest of the reply

                response_len = ord(line_size[1]) # this is the length of the entire response
                response = []
                idx = 0

                response.append(ord(line_size[0])) # response SOF
                response.append(ord(line_size[1])) # response size

                # In the next line the -2 accounts for the SOF and size bytes done above.
                while idx < (response_len - 2): # do the rest of the response
                    response.append(ord(line_data[idx]))
                    idx += 1

                if response[7] == 0x01:

                    prev_ID = ID     # to look at the one to zero and zero to one transitions

                    ID = str("0x%0.2X" % response[20] + "%0.2X" % response[19]
                             + "%0.2X" % response[18] + "%0.2X" % response[17]
                             + "%0.2X" % response[16] + "%0.2X" % response[15]
                             + "%0.2X" % response[14] + "%0.2X" % response[13])

                    #if (ID != prev_ID):            # To look for the edge transitions
                    #    if (ID != 0):              # It is not equal and it changed to zero now that means there is a positive to negative transition
                    #        ts = time.time()       # ts is the time
                    #        pos_array.append(ts)
                    #        if (len(pos_array) > size_of_pos_edges_array):
                    #            pos_array.pop(0)
                    ts = time.time()       # ts is the time
                    wave_form.append("|")
                else:
                    ID = 0
                    ts = 0
                    wave_form.append("_")

                if(len(wave_form)>10):
                    wave_form.pop(0)
                os.system('clear')
                print wave_form

                #Build the all values array to be filtered
                all_values_array.append(ts)
                if (len(all_values_array) > size_of_arrays):
                    all_values_array.pop(0)
                #print all_values_array

                #filter the glitches
                #filtered_all_values_array = all_values_array
                filtered_all_values_array = filter_glitches(all_values_array)

                #print filtered_all_values_array

                #We will wait until the edges array is full
                if(len(filtered_all_values_array) >= size_of_arrays):
                    if((filtered_all_values_array[0] == 0) and (filtered_all_values_array[1] != 0)): #This line is a pos edge detection
                        #load the edge array
                        pos_array.append(filtered_all_values_array[1])
                        if (len(pos_array) > size_of_pos_edges_array): # Keep the value of the array up to the maximum
                            pos_array.pop(0)

                #Here we populate the frequency_array which contains all the samples
                if (len(pos_array) > 2):

                    #for n in range(1,len(pos_array)):
                    frequency = (1/(pos_array[1]-pos_array[0]))
                    frequency_array.append(frequency)
                    #print frequency
                    if (len(frequency_array) > size_of_arrays):
                        frequency_array.pop(0)

                #print frequency_array
                #print  "I am getting" , ID

            freq_print()

        except KeyboardInterrupt:
            tiser.close() # close and turn down the light
            break # Exit while(True)

    #end of while(True)
    sys.exit()

#-------------------------------------------------------------------
# Function: freq_print
# Description: this function calculates the output freq
# by eliminating the left most and right most values of the list
# after sorting the values in a new array
# the idea is to eliminate the farmost values of the sampling
#
#-------------------------------------------------------------------
def freq_print():

    global frequency_array
    global pos_array
    global Temperature
    global text1
    frequency = 0
    new_frequency_array =[] # to hold the values

    #print frequency_array

    if (len(frequency_array) > 6):
        #print 'yes'
        new_frequency_array = sorted(frequency_array)
        new_frequency_array = new_frequency_array[2:(len(new_frequency_array)- 2)]
        frequency = np.mean(new_frequency_array)

        #Rounding for our precision
        frequency = int((frequency * 8 + 0.5)) / 8.0
        print 'Frequency is ' , frequency
        Temperature = f_2_t(frequency)
        print 'Temperature is ' , Temperature
        var.set(str(Temperature))
        top.update_idletasks()         # for updating the displayed values, to be used in the timer loop

#-------------------------------------------------------------------
# Function: f_2_t
# Description: calculate the temperature with the LUT with frequency
# as input.
#
#-------------------------------------------------------------------
def f_2_t(freq):

    done = False
    for i in range(len(f_array)-1):
        if(freq == f_array[i]):
            temp = t_array[i]
            done = True

        if((freq >= f_array[i]) and (freq <= f_array[i+1])):
            temp = ((freq-f_array[i]) * (5.0 / (f_array[i+1] - f_array[i])) ) + t_array[i]
            done = True

    if(freq == f_array[-1]):  #compare with the last element
        temp = t_array[i]
        done = True

    if (done == False):
        return False

    return temp

#-------------------------------------------------------------------
# Function: filter
# Description: filter low frecuency glitches from the samples
# as input. The array element are time stamps
#
#-------------------------------------------------------------------
def filter_glitches(unfiltered_array):

    filtered_array = unfiltered_array # array to be returned

    if (len(filtered_array) > 3): #safety check
        if((filtered_array[-1] != 0) and (filtered_array[-2] == 0) and (filtered_array[-3] != 0)):
            filtered_array[-2] = filtered_array[-1] + ((filtered_array[-3] - filtered_array[-1])/2)

    return filtered_array

# ++++++++++++++++++++++  main ++++++++++++++++++++++++++++++++++++++++
main()
