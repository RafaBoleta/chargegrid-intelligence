from lcd_api import LcdApi
from machine import I2C
from time import sleep_ms


class I2cLcd(LcdApi):

    MASK_RS = 0x01
    MASK_RW = 0x02
    MASK_E = 0x04
    MASK_BACKLIGHT = 0x08

    def __init__(self, i2c, i2c_addr, num_lines, num_columns):

        self.i2c = i2c
        self.i2c_addr = i2c_addr
        self.backlight = self.MASK_BACKLIGHT

        super().__init__(num_lines, num_columns)

        self._init_lcd()

    def _write_byte(self, data):
        self.i2c.writeto(
            self.i2c_addr,
            bytes([data | self.backlight])
        )

    def _pulse_enable(self, data):
        self._write_byte(data | self.MASK_E)
        sleep_ms(1)
        self._write_byte(data & ~self.MASK_E)
        sleep_ms(1)

    def _write4bits(self, data):
        self._write_byte(data)
        self._pulse_enable(data)

    def hal_write_command(self, cmd):
        high = cmd & 0xF0
        low = (cmd << 4) & 0xF0

        self._write4bits(high)
        self._write4bits(low)

    def hal_write_data(self, data):
        high = data & 0xF0
        low = (data << 4) & 0xF0

        self._write4bits(high | self.MASK_RS)
        self._write4bits(low | self.MASK_RS)

    def _init_lcd(self):

        sleep_ms(50)

        self._write4bits(0x30)
        sleep_ms(5)

        self._write4bits(0x30)
        sleep_ms(1)

        self._write4bits(0x30)
        sleep_ms(1)

        self._write4bits(0x20)
        sleep_ms(1)

        self.hal_write_command(
            self.LCD_FUNCTION |
            self.FUNCTION_2LINES |
            self.FUNCTION_5X8DOTS
        )

        self.hal_write_command(
            self.LCD_DISPLAY_CTRL |
            self.DISPLAY_ON |
            self.CURSOR_OFF |
            self.BLINK_OFF
        )

        self.clear()

        self.hal_write_command(
            self.LCD_ENTRY_MODE |
            self.ENTRY_LEFT |
            self.ENTRY_SHIFT_DECREMENT
        )