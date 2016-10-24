#!/usr/bin/env python

import io                  # importing python libraries
import sys
import serial              # for the timer and the duration of the loop




import time, threading


times = 0  # variable to count the number of times it is seen

def foo():
       # hits = 0
        #prev_ID = 1
        ID = 0
        #xxx = 0
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
           # ID = 0


            ID = str("0x%0.2X" % response[20] + "%0.2X" % response[19]
                    + "%0.2X" % response[18] + "%0.2X" % response[17]
                    + "%0.2X" % response[16] + "%0.2X" % response[15]
                    + "%0.2X" % response[14] + "%0.2X" % response[13])

        tiser.close()
        #times += 1


        print  "I am getting" , ID , times
        threading.Timer(0.125, foo).start()


foo()
