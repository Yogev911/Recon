from __future__ import division
from __future__ import with_statement
import smbus


MIN_SATS = 7
EARTH_RADIUS = 6371000 # meters
GRAV_ACCEL = 9.80665   # meters per second per second



rc_status_name = ("PASSIVE", "TAKEOFF", "FLYING", "LANDING", "POWEROFF")

FULL_FIFO_BATCHES = 20 # << int(512 / 12)

####################################################################################################
#
#  Adafruit i2c interface enhanced with performance / error handling enhancements
#
####################################################################################################
class I2C:

    def __init__(self, address, bus=smbus.SMBus(1)):
        self.address = address
        self.bus = bus
        self.misses = 0

    def reverseByteOrder(self, data):
        "Reverses the byte order of an int (16-bit) or long (32-bit) value"
        # Courtesy Vishal Sapre
        dstr = hex(data)[2:].replace('L','')
        byteCount = len(dstr[::2])
        val = 0
        for i, n in enumerate(range(byteCount)):
            d = data & 0xFF
            val |= (d << (8 * (byteCount - i - 1)))
            data >>= 8
        return val

    def writeByte(self, value):
        while True:
            try:
                self.bus.write_byte(self.address, value)
                break
            except IOError, err:
                self.misses += 1

    def write8(self, reg, value):
        "Writes an 8-bit value to the specified register/address"
        while True:
            try:
                self.bus.write_byte_data(self.address, reg, value)
                break
            except IOError, err:
                self.misses += 1

    def writeList(self, reg, list):
        "Writes an array of bytes using I2C format"
        while True:
            try:
                self.bus.write_i2c_block_data(self.address, reg, list)
                break
            except IOError, err:
                self.misses += 1

    def readU8(self, reg):
        "Read an unsigned byte from the I2C device"
        while True:
            try:
                result = self.bus.read_byte_data(self.address, reg)
                return result
            except IOError, err:
                self.misses += 1

    def readS8(self, reg):
        "Reads a signed byte from the I2C device"
        while True:
            try:
                result = self.bus.read_byte_data(self.address, reg)
                if (result > 127):
                    return result - 256
                else:
                    return result
            except IOError, err:
                self.misses += 1

    def readU16(self, reg):
        "Reads an unsigned 16-bit value from the I2C device"
        while True:
            try:
                hibyte = self.bus.read_byte_data(self.address, reg)
                result = (hibyte << 8) + self.bus.read_byte_data(self.address, reg+1)
                return result
            except IOError, err:
                self.misses += 1

    def readS16(self, reg):
        "Reads a signed 16-bit value from the I2C device"
        while True:
            try:
                hibyte = self.bus.read_byte_data(self.address, reg)
                if (hibyte > 127):
                    hibyte -= 256
                result = (hibyte << 8) + self.bus.read_byte_data(self.address, reg+1)
                return result
            except IOError, err:
                self.misses += 1

    def readList(self, reg, length):
        "Reads a byte array value from the I2C device"
        result = self.bus.read_i2c_block_data(self.address, reg, length)
        return result

    def getMisses(self):
        return self.misses


####################################################################################################
#
#  Garmin LiDAR-Lite v3 range finder
#
####################################################################################################
class GLLv3:
    i2c = None

    __GLL_ACQ_COMMAND       = 0x00
    __GLL_STATUS            = 0x01
    __GLL_SIG_COUNT_VAL     = 0x02
    __GLL_ACQ_CONFIG_REG    = 0x04
    __GLL_VELOCITY          = 0x09
    __GLL_PEAK_CORR         = 0x0C
    __GLL_NOISE_PEAK        = 0x0D
    __GLL_SIGNAL_STRENGTH   = 0x0E
    __GLL_FULL_DELAY_HIGH   = 0x0F
    __GLL_FULL_DELAY_LOW    = 0x10
    __GLL_OUTER_LOOP_COUNT  = 0x11
    __GLL_REF_COUNT_VAL     = 0x12
    __GLL_LAST_DELAY_HIGH   = 0x14
    __GLL_LAST_DELAY_LOW    = 0x15
    __GLL_UNIT_ID_HIGH      = 0x16
    __GLL_UNIT_ID_LOW       = 0x17
    __GLL_I2C_ID_HIGHT      = 0x18
    __GLL_I2C_ID_LOW        = 0x19
    __GLL_I2C_SEC_ADDR      = 0x1A
    __GLL_THRESHOLD_BYPASS  = 0x1C
    __GLL_I2C_CONFIG        = 0x1E
    __GLL_COMMAND           = 0x40
    __GLL_MEASURE_DELAY     = 0x45
    __GLL_PEAK_BCK          = 0x4C
    __GLL_CORR_DATA         = 0x52
    __GLL_CORR_DATA_SIGN    = 0x53
    __GLL_ACQ_SETTINGS      = 0x5D
    __GLL_POWER_CONTROL     = 0x65

    def __init__(self, address=0x62, rate=10):
        self.i2c = I2C(address)
        self.rate = rate

        #-------------------------------------------------------------------------------------------
        # Set to continuous sampling after initial read.
        #-------------------------------------------------------------------------------------------
        self.i2c.write8(self.__GLL_OUTER_LOOP_COUNT, 0xFF)

        #-------------------------------------------------------------------------------------------
        # Set the sampling frequency as 2000 / Hz:
        # 10Hz = 0xc8
        # 20Hz = 0x64
        # 100Hz = 0x14
        #-------------------------------------------------------------------------------------------
        self.i2c.write8(self.__GLL_MEASURE_DELAY, int(2000 / rate))

        #-------------------------------------------------------------------------------------------
        # Include receiver bias correction 0x04
        #AB! 0x04 | 0x01 should cause (falling edge?) GPIO_GLL_DR_INTERRUPT.  Can GPIO handle this?
        #-------------------------------------------------------------------------------------------
        self.i2c.write8(self.__GLL_ACQ_COMMAND, 0x04 | 0x01)

        #-------------------------------------------------------------------------------------------
        # Acquisition config register:
        # 0x01 Data ready interrupt
        # 0x20 Take sampling rate from MEASURE_DELAY
        #-------------------------------------------------------------------------------------------
        self.i2c.write8(self.__GLL_ACQ_CONFIG_REG, 0x21)


    def read(self):
        #-------------------------------------------------------------------------------------------
        # Distance is in cm hence the 100s to convert to meters.
        # Velocity is in cm between consecutive reads; sampling rate converts these to a velocity.
        # Reading the list from 0x8F seems to get the previous reading, probably cached for the sake
        # of calculating the velocity next time round.
        #-------------------------------------------------------------------------------------------
        dist1 = self.i2c.readU8(self.__GLL_FULL_DELAY_HIGH)
        dist2 = self.i2c.readU8(self.__GLL_FULL_DELAY_LOW)
        distance = (dist1 << 8) + dist2

        if distance == 1:
            print 'laser is out of range'

        return distance / 100


####################################################################################################
#
#  Garmin LiDAR-Lite v3HP range finder
#
####################################################################################################
class GLLv3HP:
    i2c = None

    __GLL_ACQ_COMMAND       = 0x00
    __GLL_STATUS            = 0x01
    __GLL_SIG_COUNT_VAL     = 0x02
    __GLL_ACQ_CONFIG_REG    = 0x04
    __GLL_LEGACY_RESET_EN   = 0x06
    __GLL_SIGNAL_STRENGTH   = 0x0E
    __GLL_FULL_DELAY_HIGH   = 0x0F
    __GLL_FULL_DELAY_LOW    = 0x10
    __GLL_REF_COUNT_VAL     = 0x12
    __GLL_UNIT_ID_HIGH      = 0x16
    __GLL_UNIT_ID_LOW       = 0x17
    __GLL_I2C_ID_HIGHT      = 0x18
    __GLL_I2C_ID_LOW        = 0x19
    __GLL_I2C_SEC_ADDR      = 0x1A
    __GLL_THRESHOLD_BYPASS  = 0x1C
    __GLL_I2C_CONFIG        = 0x1E
    __GLL_PEAK_STACK_HIGH   = 0x26
    __GLL_PEAK_STACK_LOW    = 0x27
    __GLL_COMMAND           = 0x40
    __GLL_HEALTHY_STATUS    = 0x48
    __GLL_CORR_DATA         = 0x52
    __GLL_CORR_DATA_SIGN    = 0x53
    __GLL_POWER_CONTROL     = 0x65

    def __init__(self, address=0x62):
        self.i2c = I2C(address)

        self.i2c.write8(self.__GLL_SIG_COUNT_VAL, 0x80)
        self.i2c.write8(self.__GLL_ACQ_CONFIG_REG, 0x08)
        self.i2c.write8(self.__GLL_REF_COUNT_VAL, 0x05)
        self.i2c.write8(self.__GLL_THRESHOLD_BYPASS, 0x00)

    def read(self):
        acquired = False

        # Trigger acquisition
        self.i2c.write8(self.__GLL_ACQ_COMMAND, 0x01)

        # Poll acquired?
        while not acquired:
            acquired = not (self.i2c.readU8(self.__GLL_STATUS) & 0x01)
        else:
            dist1 = self.i2c.readU8(self.__GLL_FULL_DELAY_HIGH)
            dist2 = self.i2c.readU8(self.__GLL_FULL_DELAY_LOW)
            distance = (dist1 << 8) + dist2

            if distance == 10:
                print 'laser is out of range'

        return distance / 100

