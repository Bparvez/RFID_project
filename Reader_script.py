#!/usr/bin/env python

import io                  # importing python libraries
import sys
import serial              # for the timer and the duration of the loop
import time, threading     # for time stamping and threading


pos_array = []   # array to store time stamped negative to positive edge/change values
neg_array = []   # array to store time stamped positive to negative edge/change values
frequency_array = [] # array to store the calculated frequency values
n = 0  # int to terminate the loop after some number of times, and for the array
ID = 0 # initilize the global int ID to zero
prev_ID = 0 # Initialize the global int prev_ID to zero for comparing the positive to negative edge
first_time = 0 # to not make the detection for the first time


def foo():
    num_of_times = 100
    frequency = 0
    global n
    global pos_array, neg_array
    global ID , prev_ID
    global first_time
    n = n+1
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


    print  "I am getting" , ID
    if first_time == 1:
        ts = time.time()     # ts is the time
        if (ID != prev_ID):               # To look for the edge transitions
            if ID == 0:                   # It is not equal and it changed to zero now that means there is a positive to negative transition
                neg_array.append(ts)
            else:                         # else it is a negative to positive transitions
                pos_array.append(ts)

    if n < num_of_times:
        threading.Timer(0.125, foo).start()

    if n == num_of_times:              # for displaying at the moment, not for the final code
        # print 'Negative array:',(neg_array)
        print 'Positive array:',(pos_array)
        for n in range(len(pos_array)):
            frequency =  (1/(pos_array[n]-pos_array[n-1]))
            frequency_array.append(frequency)

        print 'Frequency is ' , frequency_array
        print 'Temperature is blah blah'

    prev_ID = ID     # to look at the one to zero and zero to one transitions
    first_time = 1



foo()
