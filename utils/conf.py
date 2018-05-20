RECONUNITID = 1
MARK = 'mark'
TARGET_TYPES = ['warrning','danger','ally','unknown']
SOLDIER_SCAN_INTERVAL = 3

# DB region
DB_HOST = '0.0.0.0'
DB_PORT = 3000
DB_LANE = 'hello'
HEADER = {"reconunitid": 1}

# GPS region
COLD_START = "$PMTK103*30\r\n"
WARM_START = "$PMTK102*31\r\n"
UPDATE_10_sec = "$PMTK220,10000*2F\r\n"  # Update Every 10 Seconds
UPDATE_5_sec = "$PMTK220,5000*1B\r\n"  # Update Every 5 Seconds
UPDATE_1_sec = "$PMTK220,1000*1F\r\n"  # Update Every One Second
UPDATE_200_msec = "$PMTK220,200*2C\r\n"  # Update Every 200 Milliseconds
# This set is used to set the rate the GPS takes measurements
MEAS_10_sec = "$PMTK300,10000,0,0,0,0*2C\r\n"  # Measure every 10 seconds
MEAS_5_sec = "$PMTK300,5000,0,0,0,0*18\r\n"  # Measure every 5 seconds
MEAS_1_sec = "$PMTK300,1000,0,0,0,0*1C\r\n"  # Measure once a second
MEAS_200_msec = "$PMTK300,200,0,0,0,0*2F\r\n"  # Meaure 5 times a second
# Set the Baud Rate of GPS
BAUD_57600 = "$PMTK251,57600*2C\r\n"  # Set Baud Rate at 57600
BAUD_9600 = "$PMTK251,9600*17\r\n"  # Set 9600 Baud Rate
# Commands for which NMEA Sentences are sent
GPRMC_ONLY = "$PMTK314,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0*29\r\n"  # Send only the GPRMC Sentence
GPGGA_ONLY = "$PMTK314,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0*29\r\n"  # Send only the GPRMC Sentence
GPRMC_GPGGA = "$PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0*28\r\n"  # Send GPRMC AND GPGGA Sentences
SEND_ALL = "$PMTK314,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0*28\r\n"  # Send All Sentences
SEND_NOTHING = "$PMTK314,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0*28\r\n"  # Send Nothing


# api region
HOST = 'localhost'
PORT = 7080

data = [
    {
        "id": 1,
        "reconunitid": 1,
        "altitude": "123123",
        "longitude": "123",
        "latitude": "123",
        "azimuth": "123",
        "size": 123,
        "type": "123"
    },
    {
        "id": 3,
        "reconunitid": 1,
        "altitude": "423423",
        "longitude": "23423",
        "latitude": "234",
        "azimuth": "234",
        "size": 234,
        "type": "234"
    },
    {
        "id": 4,
        "reconunitid": 1,
        "altitude": "111",
        "longitude": "222",
        "latitude": "22",
        "azimuth": "33",
        "size": 234,
        "type": "234"
    },
    {
        "id": 5,
        "reconunitid": 1,
        "altitude": "22",
        "longitude": "3323",
        "latitude": "343",
        "azimuth": "4",
        "size": 34,
        "type": "234234"
    },
    {
        "id": 6,
        "reconunitid": 1,
        "altitude": "2222",
        "longitude": "3323",
        "latitude": "322",
        "azimuth": "4",
        "size": 34,
        "type": "234234"
    },
    {
        "id": 7,
        "reconunitid": 1,
        "altitude": "2222",
        "longitude": "3323",
        "latitude": "322",
        "azimuth": "4",
        "size": 34,
        "type": "234234"
    },
    {
        "id": 8,
        "reconunitid": 1,
        "altitude": "2222",
        "longitude": "3323",
        "latitude": "322",
        "azimuth": "4",
        "size": 34,
        "type": "234234"
    }
]
