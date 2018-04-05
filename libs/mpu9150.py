class mpu9150:
    # Accelerometer addresses
    ACCEL_CONFIG = 0x1c
    ACCEL_XOUT_L = 0x3b
    ACCEL_YOUT_L = 0x3d
    ACCEL_ZOUT_L = 0x3f
    # Accelerometer values
    AFS_SEL_2G = 0
    AFS_SEL_4G = 1
    AFS_SEL_8G = 2
    AFS_SEL_16G = 3

    SMPRT_DIV = 0x25

    PWR_MGMT_1 = 0x6b

    def __init__(self, i2c_bus):
        self.i2c = i2c_bus

    @staticmethod
    def twos_comp(val, bits):
        """Compute the 2's compliment of int value val"""
        if (val & (1 << (bits - 1))) != 0:
            val = val - (1 << bits)
        return val

    def read_x_acc_raw(self):
        return self.i2c.read_word(self.ACCEL_XOUT_L)

    def read_x_acc(self):
        acc_resolution = self.get_acc_sensitivity()
        value = mpu9150.twos_comp(self.read_x_acc_raw(), 16)
        scaled_value = float(value) / acc_resolution
        return scaled_value

    def read_y_acc_raw(self):
        return self.i2c.read_word(self.ACCEL_YOUT_L)

    def read_y_acc(self):
        acc_resolution = self.get_acc_sensitivity()
        value = mpu9150.twos_comp(self.read_y_acc_raw(), 16)
        scaled_value = float(value) / acc_resolution
        return scaled_value

    def read_z_acc_raw(self):
        return self.i2c.read_word(self.ACCEL_ZOUT_L)

    def read_z_acc(self):
        acc_resolution = self.get_acc_sensitivity()
        value = mpu9150.twos_comp(self.read_z_acc_raw(), 16)
        scaled_value = float(value) / acc_resolution
        return scaled_value

    def set_acc_full_scale_range(self, value):
        register_value = self.i2c.read_byte(self.ACCEL_CONFIG)
        new_value = register_value & 0xe7
        new_value |= (value & 0x03) << 3
        self.i2c.write_byte(self.ACCEL_CONFIG, new_value)

    def get_acc_sensitivity(self):
        """Returns the accelerometer sensitivity, set by AFS_SEL (see description of register 28 in documentation)"""
        register_value = self.i2c.read_byte(self.ACCEL_CONFIG)
        scale_value = (register_value >> 3) & 0x03
        sensitivity = 16384 >> scale_value
        return sensitivity

    def set_sample_rate_divider(self, value):
        self.i2c.write_byte(self.SMPRT_DIV, value)

    def set_sleep_state(self, value):
        register_value = self.i2c.read_byte(self.PWR_MGMT_1)
        new_value = register_value & 0xbf
        new_value |= (value & 0x01) << 6
        self.i2c.write_byte(self.PWR_MGMT_1, new_value)

    def select_clock_source(self, value):
        register_value = self.i2c.read_byte(self.PWR_MGMT_1)
        new_value = register_value & 0xf8
        new_value |= value & 0x07
        self.i2c.write_byte(self.PWR_MGMT_1, new_value)
