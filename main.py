import serial #import pyserial library
from time import sleep #import sleep library
ser=serial.Serial('/dev/ttyAMA0',9600) #Initialize Serial Port
from time import sleep #import sleep library
import pynmea2
class my_gps:                      #Create GPS class
        def __init__(self):     #This init will run when you create a GPS object.
                #This sets up variables for useful commands.
                #This set is used to set the rate the GPS reports
                UPDATE_10_sec=  "$PMTK220,10000*2F\r\n" #Update Every 10 Seconds
                UPDATE_5_sec=  "$PMTK220,5000*1B\r\n"   #Update Every 5 Seconds
                UPDATE_1_sec=  "$PMTK220,1000*1F\r\n"   #Update Every One Second
                UPDATE_200_msec=  "$PMTK220,200*2C\r\n" #Update Every 200 Milliseconds
                #This set is used to set the rate the GPS takes measurements
                MEAS_10_sec = "$PMTK300,10000,0,0,0,0*2C\r\n" #Measure every 10 seconds
                MEAS_5_sec = "$PMTK300,5000,0,0,0,0*18\r\n"   #Measure every 5 seconds
                MEAS_1_sec = "$PMTK300,1000,0,0,0,0*1C\r\n"   #Measure once a second
                MEAS_200_msec= "$PMTK300,200,0,0,0,0*2F\r\n"  #Meaure 5 times a second
                #Set the Baud Rate of GPS
                BAUD_57600 = "$PMTK251,57600*2C\r\n"          #Set Baud Rate at 57600
                BAUD_9600 ="$PMTK251,9600*17\r\n"             #Set 9600 Baud Rate
                #Commands for which NMEA Sentences are sent
                GPRMC_ONLY= "$PMTK314,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0*29\r\n" #Send only the GPRMC Sentence
                GPRMC_GPGGA="$PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0*28\r\n"#Send GPRMC AND GPGGA Sentences
                SEND_ALL ="$PMTK314,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0*28\r\n" #Send All Sentences
                SEND_NOTHING="$PMTK314,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0*28\r\n" #Send Nothing
                ser.write(BAUD_57600)   #Set Baud Rate to 57600
                sleep(1)                #Paulse
                ser.baudrate=57600      #IMPORTANT Since change ser baudrate to match GPS
                ser.write(UPDATE_200_msec) #Set update rate
                sleep(1)
                ser.write(MEAS_200_msec)  #Set measurement rate
                sleep(1)
                ser.write(SEND_ALL)    #Ask for only GPRMC and GPGGA Sentences
                sleep(1)
                ser.flushInput()          #clear buffers
                ser.flushOutput()
                print "GPS is Initialized" #Print message

myGPS=my_gps()
while(1):
        # ser.flushInput() #Clear Buffers
        # ser.flushInput()
        while ser.inWaiting()==0: #Wait for input
                pass
        NMEA1=ser.read_all()      #Read NMEA1
        # NMEA2=ser.readline()
        print NMEA1
        # print pynmea2.parse(NMEA2)
        print '******************'