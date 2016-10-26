#!/usr/bin/env python

import io                  # importing python libraries
import sys
import serial              # for the timer and the duration of the loop
import time, threading     # for time stamping and threading
import numpy as np    # for the mean

size_of_arrays = 10
size_of_pos_edges_array = 10
pos_array = list()   # array to store time stamped negative to positive edge/change values
neg_array = list()   # array to store time stamped positive to negative edge/change values , bot using it at the moment
frequency_array = list() # array to store the calculated frequency values
n = 0  # int to terminate the loop after some number of times, and for the array
ID = 0 # initilize the global int ID to zero
prev_ID = 0 # Initialize the global int prev_ID to zero for comparing the positive to negative edge
first_time = 0 # to not make the detection for the first time

#LUT for frecuencty to temp conversion
t_array = [ -40, -35, -30, -25, -20, -15, -10, -5, 0, 5, 10, 15,  20,  25,  30, 35, 40, 45, 50, 55, 60,  65, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130, 135, 140, 145, 150]
f_array = [ 0.0709,  0.0949,  0.1255,  0.1643,  0.2129, 0.2732, 0.3477, 0.4386, 0.5491,  0.6822,  0.8416, 1.0314, 1.2558,  1.5198, 1.8286, 2.1880,  2.6046,  3.0845, 3.6358,  4.2654,  4.9828,  5.7962,  6.71567,  7.7499, 8.9135, 10.2066,  11.6546, 13.2614 ]


#-------------------------------------------------------------------
# Function: main 
# Description: 
#
#-------------------------------------------------------------------
def main():

    num_of_times = 100
    frequency = 0
    global size_of_arrays
    global n
    global pos_array, neg_array, filtered_all_values_array, all_values_array
    global ID , prev_ID
    global first_time
    global frequency_array

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

<<<<<<< HEAD
    # Send out the command to the reader

    tiser.write(memoryview(command))  # memoryview is the same as buffer


    line_size = tiser.read(2)  # first pass, read first two bytes of reply

    if len(line_size) < 2:
        print ("No data returned.  Is the reader turned on?")
        tiser.close()
        sys.exit()

    # second pass

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

        ID = str("0x%0.2X" % response[20] + "%0.2X" % response[19]
                + "%0.2X" % response[18] + "%0.2X" % response[17]
                + "%0.2X" % response[16] + "%0.2X" % response[15]
                + "%0.2X" % response[14] + "%0.2X" % response[13])

    tiser.close()


    #print  "I am getting" , ID
    if first_time == 1:
        ts = time.time()     # ts is the time
        if (ID != prev_ID):               # To look for the edge transitions
            if ID == 0:                   # It is not equal and it changed to zero now that means there is a positive to negative transition
                neg_array.append(ts)
                if (len(neg_array) > size_of_arrays):
                    neg_array.pop(0)
            else:                         # else it is a negative to positive transitions
                pos_array.append(ts)
                if (len(pos_array) > size_of_arrays):
                    pos_array.pop(0)

    if n < num_of_times:
        threading.Timer(0.125, foo).start()
        #print pos_array
        #print 'doing it'    # for debugging information
        if (len(pos_array) > 2):
            for n in range(1,len(pos_array)):
                frequency =  (1/(pos_array[n]-pos_array[n-1]))
                frequency_array.append(frequency)
                #print frequency
                if (len(frequency_array) > size_of_arrays):
                    frequency_array.pop(0)


    prev_ID = ID     # to look at the one to zero and zero to one transitions
    first_time = 1


=======
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

                    if (ID != prev_ID):            # To look for the edge transitions
                        if (ID != 0):              # It is not equal and it changed to zero now that means there is a positive to negative transition
                            ts = time.time()       # ts is the time
                            pos_array.append(ts)
                            if (len(pos_array) > size_of_pos_edges_array):
                                pos_array.pop(0)

                else:
                    ID = 0

                #Build the all values array to be filtered
                ts = time.time()       # ts is the time
                all_values_array.append(ts)
                if (len(all_values_array) > size_of_arrays):
                    all_values_array.pop(0)

                filtered_all_values_array = filter_glitches(all_values_array)
                 
                #We will wait until the edges array is full
                if( len(filtered_all_values_array) => size_of_pos_edges_array): 
                    if((filtered_all_values_array[0] == 0) and (filtered_all_values_array[1] != 0)):
                        #load the edge
                        #TODO
                        #then load the next edge
                        #TODO
                        #then calculate the frecuency
                        frequency = (1/(filtered_all_values_array[0]-filtered_all_values_array[1]))
                        frequency_array.append(frequency)
                            if (len(frequency_array) > size_of_arrays):
                                frequency_array.pop(0)

                
                #Here we populate the frequency_array which contains all the samples
                #if (len(pos_array) > 2):
                #    for n in range(1,len(pos_array)):
                #        frequency =  (1/(pos_array[n]-pos_array[n-1]))
                #        frequency_array.append(frequency)
                #        #print frequency
                #        if (len(frequency_array) > size_of_arrays):
                #            frequency_array.pop(0)

                #print  "I am getting" , ID

            freq_print()

        except KeyboardInterrupt:
            tiser.close() # close and turn down the light
            break # Exit while(True)


#-------------------------------------------------------------------
# Function: freq_print
# Description: this function calculates the output freq
# by eliminating the left most and right most values of the list
# after sorting the values in a new array
# the idea is to eliminate the farmost values of the sampling
#
#-------------------------------------------------------------------
>>>>>>> 5c699b23bd2ce5e75b6fba905d513a6ac64c3fb3
def freq_print():

    global frequency_array
    global pos_array
    frequency = 0
    new_frequency_array =[] # to hold the values
<<<<<<< HEAD
    print pos_array
=======
    
    #print frequency_array

>>>>>>> 5c699b23bd2ce5e75b6fba905d513a6ac64c3fb3
    if (len(frequency_array) > 6):
        #print 'yes'
        new_frequency_array = sorted(frequency_array)
        new_frequency_array = new_frequency_array[2:(len(new_frequency_array)- 2)]
        frequency = np.mean(new_frequency_array)
        #print 'Frequency is ' , frequency
        Temperature = f_2_t(frequency)
        #print 'Temperature is ' , Temperature

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
            temp = freq * (t_array[i] - t_array[i+1]) / (f_array[i] - f_array[i+1])
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
def filter_glitches(unfiltered_array)

    filtered_array = unfiltered_array # array to be returned  

    if (len(filtered_array) > 3): #safety check
        if((filtered_array[-1] != 0) and (filtered_array[-2] == 0) and (filtered_array[-3] != 0)): 
            filtered_array[-2] = filtered_array[-1] + ((filtered_array[-3] - filtered_array[-1])/2)
    return filtered_array

# ++++++++++++++++++++++  main ++++++++++++++++++++++++++++++++++++++++
main()
