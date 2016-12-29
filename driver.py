
import time


class Driver_7Seg:
    CMD_CLEAR_DISPLAY = b'\x76'
    CMD_DOT = b'\x77'
    CMD_CURSOR = b'\x79'
    CMD_BRIGHTNESS = b'\x7A'
    CMD_DIGIT_1 = b'\x7B'
    CMD_DIGIT_2 = b'\x7C'
    CMD_DIGIT_3 = b'\x7D'
    CMD_DIGIT_4 = b'\x7E'
    CMD_BAUDRATE = b'\x7F'
    CMD_I2C_ADDR = b'\x80'
    CMD_FACTORY_RESET = b'\x81'

    def __enter__(self):
        raise NotImplementedError

    def __exit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError

    def __write(self, values: bytes):
        with self as c:
            c.write(values)

    def print(self, txt: str):
        valid = '0123456789abcdefghijlnopqrstuy -'
        for c in txt:
            if c.lower() not in valid:
                raise ValueError(repr(c) + ' is not legal (' + txt + ')')
        data = bytes(txt.encode('ascii'))
        with self as c:
            for byte in data:
                c.write(bytes([byte]))

    DOT_DIGIT1     = 0b000001
    DOT_DIGIT2     = 0b000010
    DOT_DIGIT3     = 0b000100
    DOT_DIGIT4     = 0b001000
    DOT_COLON      = 0b010000
    DOT_APOSTROPHE = 0b100000

    def write_dot(self, dot=None):
        if dot is not None:
            self.dot = dot
        assert (dot in range(0, 64))
        self.__write(self.CMD_DOT + bytes([dot]))

    SEG_A = 0b0000001
    SEG_B = 0b0000010
    SEG_C = 0b0000100
    SEG_D = 0b0001000
    SEG_E = 0b0010000
    SEG_F = 0b0100000
    SEG_G = 0b1000000

    def write_seg(self, digit, seg):
        if digit == 0:
            cmd = self.CMD_DIGIT_1
        elif digit == 1:
            cmd = self.CMD_DIGIT_2
        elif digit == 2:
            cmd = self.CMD_DIGIT_3
        elif digit == 3:
            cmd = self.CMD_DIGIT_4
        else:
            assert(False)

        self.__write(cmd + bytes([seg]))

    def clear(self):
        self.__write(self.CMD_CLEAR_DISPLAY)

    def set_cursor(self, pos: int):
        assert (pos in range(0, 4))
        self.__write(self.CMD_CURSOR + bytes([pos]))

    def set_brightness(self, brightness: int):
        assert (brightness in range(0, 256))
        self.__write(self.CMD_BRIGHTNESS + bytes([brightness]))

    def _set_baudrate(self, baudrate: int):
        assert (baudrate in range(0, 12))
        self.__write(self.CMD_BAUDRATE + bytes([baudrate]))

    def _set_i2c_address(self, address: int):
        assert (address in range(1, 127))
        self.__write(self.CMD_I2C_ADDR + bytes([address]))

    def _factory_reset(self):
        self.__write(self.CMD_FACTORY_RESET)


class SerialDriver_7Seg(Driver_7Seg):
    def __init__(self, serial_param):
        import serial
        super(SerialDriver_7Seg, self).__init__()
        self.connection = serial.Serial(*serial_param)

    def __del__(self):
        self.connection.close()

    def __enter__(self):
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

if __name__ == '__main__':
    d = SerialDriver_7Seg(('/dev/ttyUSB0', 9600))

    # change brightness
    d.set_brightness(255)

    # write numbers
    with d as f:
        for val in range(0, 16):
            f.write([val])
            time.sleep(0.2)
    d.clear()

    # move dots
    for val in [2**i for i in range(0, 6)]:
        d.write_dot(val)
        time.sleep(0.2)
    d.clear()

    # spin
    for val in [d.SEG_A, d.SEG_B, d.SEG_G, d.SEG_F] * 3:
        d.write_seg(0, val)
        time.sleep(0.2)
    d.clear()